"""
Lua Parser Service - Parses Lua files using tree-sitter and extracts meaningful chunks
Ported from dcs-lua-analyzer project
"""

import os
import re
import logging
from typing import List, Dict, Any, Optional
import tree_sitter_languages as tsl
from tree_sitter import Node

# Configure logging
logger = logging.getLogger("victor-lua-parser")

# Get the Lua parser
parser = tsl.get_parser("lua")

# Lua node types to extract as separate chunks
CHUNK_NODE_TYPES = {
    'function_declaration',
    'function_definition',
    'local_function_definition',
    'table_constructor',
    'assignment',
    'comment',
    'do_statement',
    'if_statement',
    'while_statement',
    'for_statement',
    'return_statement'
}

# Keywords that might indicate DCS-specific content
DCS_KEYWORDS = {
    'coalition', 'country', 'trigger', 'action', 'condition',
    'unit', 'group', 'static', 'airbase', 'zone', 'waypoint',
    'task', 'mission', 'event', 'handler', 'missionCommands',
    'timer', 'scheduler', 'radio', 'marker', 'smoke', 'flare'
}

def extract_node_text(source_code: str, node: Node) -> str:
    """Extract the text content of a tree-sitter node."""
    return source_code[node.start_byte:node.end_byte]

def get_node_metadata(source_code: str, node: Node, file_path: str) -> Dict[str, Any]:
    """Extract metadata from a node, including DCS-specific information."""
    metadata = {
        'type': node.type,
        'start_line': node.start_point[0] + 1,
        'end_line': node.end_point[0] + 1,
        'file_path': file_path
    }
    
    # Extract function or variable names
    if node.type in ('function_declaration', 'function_definition', 'local_function_definition'):
        name_node = next((child for child in node.children if child.type == 'identifier'), None)
        if name_node:
            metadata['name'] = extract_node_text(source_code, name_node)
    
    # Check for DCS-specific content
    content = extract_node_text(source_code, node).lower()
    dcs_keywords_found = [kw for kw in DCS_KEYWORDS if kw in content]
    if dcs_keywords_found:
        metadata['dcs_keywords'] = dcs_keywords_found
    
    # Extract comments for documentation
    if node.type == 'comment':
        metadata['comment_text'] = extract_node_text(source_code, node)
    
    return metadata

def chunk_lua_file(file_path: str, content: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Parse a Lua file and extract meaningful chunks for embedding.
    
    Args:
        file_path: Path to the Lua file
        content: Optional file content (if not provided, will read from file)
    
    Returns:
        List of chunks with metadata
    """
    if content is None:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    
    # Parse the file
    tree = parser.parse(bytes(content, 'utf-8'))
    
    chunks = []
    
    def process_node(node: Node, parent_chunk_id: Optional[int] = None) -> None:
        """Recursively process nodes and extract chunks."""
        # Skip nodes that are too small
        if node.end_byte - node.start_byte < 10:
            for child in node.children:
                process_node(child, parent_chunk_id)
            return
        
        # Check if this node type should be extracted as a chunk
        if node.type in CHUNK_NODE_TYPES:
            chunk_content = extract_node_text(content, node)
            metadata = get_node_metadata(content, node, file_path)
            
            chunk = {
                'file_path': file_path,
                'chunk_type': node.type,
                'content': chunk_content,
                'meta_data': metadata,
                'line_start': node.start_point[0] + 1,
                'line_end': node.end_point[0] + 1,
                'parent_id': parent_chunk_id
            }
            
            chunks.append(chunk)
            
            # Use the index of the just-added chunk as the parent_id for children
            current_chunk_id = len(chunks) - 1
            
            # Process children with this chunk as parent
            for child in node.children:
                process_node(child, current_chunk_id)
        else:
            # Process children without changing parent
            for child in node.children:
                process_node(child, parent_chunk_id)
    
    # Start processing from the root
    process_node(tree.root_node)
    
    # If no chunks were extracted, create one chunk for the whole file
    if not chunks:
        chunks.append({
            'file_path': file_path,
            'chunk_type': 'file',
            'content': content,
            'meta_data': {'type': 'file', 'file_path': file_path},
            'line_start': 1,
            'line_end': len(content.splitlines()),
            'parent_id': None
        })
    
    return chunks

def should_index_file(file_path: str) -> bool:
    """
    Determine if a file should be indexed based on exclusion patterns.
    
    Excludes:
    - Files in XSAF.DB/ directory
    - Files in Moose/ directory  
    - Mist.lua files
    """
    # Normalize path for consistent checking
    normalized_path = os.path.normpath(file_path).replace('\\', '/')
    
    # Check exclusion patterns
    if '/XSAF.DB/' in normalized_path or normalized_path.endswith('/XSAF.DB'):
        return False
    if '/Moose/' in normalized_path or normalized_path.endswith('/Moose'):
        return False
    if normalized_path.endswith('/Mist.lua') or '/Mist.lua/' in normalized_path:
        return False
    
    return True

class LuaParser:
    """
    Async wrapper for Lua parsing functionality to maintain compatibility.
    """
    
    def __init__(self):
        pass
    
    async def parse_file_content(
        self, 
        content: str,
        file_path: str
    ) -> List[Dict[str, Any]]:
        """
        Parse a Lua file content into semantic chunks.
        Converts the sync function output to match async interface.
        """
        try:
            # Use the sync chunk_lua_file function
            chunks = chunk_lua_file(file_path, content)
            
            # Convert to expected format
            formatted_chunks = []
            for chunk in chunks:
                formatted_chunks.append({
                    "type": chunk['chunk_type'],
                    "content": chunk['content'],
                    "start_line": chunk['line_start'],
                    "end_line": chunk['line_end'],
                    "metadata": chunk['meta_data']
                })
            
            return formatted_chunks
            
        except Exception as e:
            logger.error(f"Error parsing file content: {e}")
            # Return just the file-level chunk on error
            return [{
                "type": "file",
                "content": content,
                "start_line": 1,
                "end_line": len(content.split('\n')),
                "metadata": {"file_path": file_path, "parse_error": str(e)}
            }]