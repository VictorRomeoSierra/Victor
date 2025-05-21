import re
import logging
from typing import List, Dict, Any, Optional, Tuple

# Configure logging
logger = logging.getLogger("victor-lua-parser")

class LuaParser:
    """
    Parser for Lua code that extracts meaningful chunks and metadata.
    """
    
    def __init__(self):
        # Patterns for identifying Lua code structures
        self.function_pattern = re.compile(r'function\s+([^\s\(]+)\s*\(([^\)]*)\)')
        self.local_function_pattern = re.compile(r'local\s+function\s+([^\s\(]+)\s*\(([^\)]*)\)')
        self.assignment_function_pattern = re.compile(r'([a-zA-Z0-9_\.]+)\s*=\s*function\s*\(([^\)]*)\)')
        self.comment_pattern = re.compile(r'--.*?$', re.MULTILINE)
        self.multiline_comment_pattern = re.compile(r'--\[\[.*?\]\]', re.DOTALL)
    
    async def parse_file_content(
        self, 
        content: str,
        file_path: str
    ) -> List[Dict[str, Any]]:
        """
        Parse a Lua file content into semantic chunks.
        """
        try:
            chunks = []
            lines = content.split('\n')
            
            # Extract file-level metadata
            file_comment = await self._extract_file_comment(content)
            file_metadata = await self._extract_file_metadata(content, file_path)
            
            # Add file-level chunk with metadata
            chunks.append({
                "type": "file",
                "content": content,
                "start_line": 1,
                "end_line": len(lines),
                "metadata": {
                    "file_path": file_path,
                    "description": file_comment,
                    **file_metadata
                }
            })
            
            # Extract functions
            function_chunks = await self._extract_functions(content, lines)
            chunks.extend(function_chunks)
            
            # Extract meaningful code blocks (e.g., if blocks, loops)
            block_chunks = await self._extract_blocks(content, lines)
            chunks.extend(block_chunks)
            
            # If file is small and we have no chunks, create smaller generic chunks
            if len(chunks) <= 1 and len(lines) <= 300:
                # Create smaller chunks of ~50 lines each
                small_chunks = await self._create_small_chunks(content, lines)
                chunks.extend(small_chunks)
            
            return chunks
            
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
    
    async def _extract_file_comment(self, content: str) -> str:
        """
        Extract the file-level comment at the top of the file.
        """
        # Look for multiline comment at the start
        multiline_match = self.multiline_comment_pattern.search(content)
        if multiline_match and multiline_match.start() < 100:  # Only if near the start
            comment = multiline_match.group(0)
            return comment.replace('--[[', '').replace(']]', '').strip()
        
        # Look for single-line comments at the start
        lines = content.split('\n')
        comment_lines = []
        for line in lines:
            line = line.strip()
            if not line or line.isspace():
                continue
            if line.startswith('--'):
                comment_lines.append(line[2:].strip())
            else:
                break
        
        return '\n'.join(comment_lines)
    
    async def _extract_file_metadata(self, content: str, file_path: str) -> Dict[str, Any]:
        """
        Extract metadata about the file.
        """
        metadata = {}
        
        # Check for module definition
        module_match = re.search(r'module\s*\([\'"](.*?)[\'"]', content)
        if module_match:
            metadata["module_name"] = module_match.group(1)
        
        # Check for requires
        requires = re.findall(r'require\s*\([\'"](.*?)[\'"]', content)
        if requires:
            metadata["dependencies"] = requires
        
        # Count functions
        function_count = len(re.findall(r'function\s+', content))
        metadata["function_count"] = function_count
        
        return metadata
    
    async def _extract_functions(self, content: str, lines: List[str]) -> List[Dict[str, Any]]:
        """
        Extract function definitions from the content.
        """
        chunks = []
        
        # Find all function declarations
        function_matches = list(self.function_pattern.finditer(content))
        local_function_matches = list(self.local_function_pattern.finditer(content))
        assignment_function_matches = list(self.assignment_function_pattern.finditer(content))
        
        # Process all function types
        all_matches = []
        for match in function_matches:
            all_matches.append(("global_function", match))
        for match in local_function_matches:
            all_matches.append(("local_function", match))
        for match in assignment_function_matches:
            all_matches.append(("assigned_function", match))
        
        # Sort by position in file
        all_matches.sort(key=lambda x: x[1].start())
        
        line_offsets = [0]
        for i, line in enumerate(lines):
            line_offsets.append(line_offsets[i] + len(line) + 1)  # +1 for newline
        
        # Process each function
        for match_type, match in all_matches:
            try:
                # Find start and end lines
                start_pos = match.start()
                
                # Find the line numbers
                start_line = next(i for i, offset in enumerate(line_offsets) if offset > start_pos) - 1
                
                # Find the function end using bracket matching
                end_line = await self._find_function_end(lines, start_line)
                
                if end_line is None or end_line <= start_line:
                    # Fallback: just take a reasonable chunk
                    end_line = min(start_line + 30, len(lines) - 1)
                
                # Get the function content
                function_content = '\n'.join(lines[start_line:end_line+1])
                
                # Get comment above function
                comment = await self._get_comment_above(lines, start_line)
                
                # Extract function name and parameters
                if match_type in ["global_function", "local_function"]:
                    function_name = match.group(1)
                    parameters = match.group(2).split(',')
                else:  # assigned_function
                    function_name = match.group(1)
                    parameters = match.group(2).split(',')
                
                parameters = [p.strip() for p in parameters]
                
                chunks.append({
                    "type": "function",
                    "content": function_content,
                    "start_line": start_line + 1,  # 1-indexed
                    "end_line": end_line + 1,      # 1-indexed
                    "metadata": {
                        "function_name": function_name,
                        "parameters": parameters,
                        "function_type": match_type,
                        "description": comment
                    }
                })
            except Exception as e:
                logger.error(f"Error extracting function: {e}")
                continue
        
        return chunks
    
    async def _find_function_end(self, lines: List[str], start_line: int) -> Optional[int]:
        """
        Find the end line of a function by matching brackets.
        """
        bracket_count = 0
        in_function = False
        
        for i in range(start_line, len(lines)):
            line = lines[i]
            
            # Skip comments
            if re.match(r'^\s*--', line):
                continue
            
            # Look for function keyword
            if not in_function and "function" in line:
                in_function = True
            
            # Count opening brackets
            bracket_count += line.count('{')
            bracket_count += line.count('(')
            bracket_count += line.count('[')
            
            # Count closing brackets
            bracket_count -= line.count('}')
            bracket_count -= line.count(')')
            bracket_count -= line.count(']')
            
            # Check for end keyword
            if in_function and "end" in line and not re.search(r'[a-zA-Z0-9_]end', line) and not re.search(r'end[a-zA-Z0-9_]', line):
                # Make sure it's not within a string
                if not self._is_in_string(line, "end"):
                    return i
        
        return None
    
    async def _is_in_string(self, line: str, keyword: str) -> bool:
        """
        Check if a keyword is within a string literal.
        """
        # Simple check - this could be improved
        pos = line.find(keyword)
        if pos == -1:
            return False
        
        # Count quotes before this position
        single_quotes = line[:pos].count("'") - line[:pos].count("\\'")
        double_quotes = line[:pos].count('"') - line[:pos].count('\\"')
        
        # If odd number of quotes, we're in a string
        return single_quotes % 2 != 0 or double_quotes % 2 != 0
    
    async def _get_comment_above(self, lines: List[str], line_number: int) -> str:
        """
        Get the comment above a given line.
        """
        comment_lines = []
        
        # Look upward for comments
        for i in range(line_number - 1, max(0, line_number - 10), -1):
            line = lines[i].strip()
            if not line or line.isspace():
                continue
            if line.startswith('--'):
                comment_lines.insert(0, line[2:].strip())
            else:
                break
        
        return '\n'.join(comment_lines)
    
    async def _extract_blocks(self, content: str, lines: List[str]) -> List[Dict[str, Any]]:
        """
        Extract meaningful code blocks like if-statements, loops, etc.
        """
        chunks = []
        
        # Pattern for control structures
        control_pattern = re.compile(r'^\s*(if|for|while|repeat|do)\s+')
        
        in_block = False
        block_start = 0
        block_type = ""
        
        for i, line in enumerate(lines):
            line = line.strip()
            if not line or line.isspace():
                continue
            
            # Skip comments
            if line.startswith('--'):
                continue
            
            # Check for block start
            if not in_block and control_pattern.match(line):
                in_block = True
                block_start = i
                match = control_pattern.match(line)
                block_type = match.group(1)
            
            # Check for block end
            if in_block and "end" in line and not re.search(r'[a-zA-Z0-9_]end', line) and not re.search(r'end[a-zA-Z0-9_]', line):
                if not self._is_in_string(line, "end"):
                    block_content = '\n'.join(lines[block_start:i+1])
                    
                    # Skip very small blocks
                    if i - block_start > 3:
                        chunks.append({
                            "type": f"{block_type}_block",
                            "content": block_content,
                            "start_line": block_start + 1,
                            "end_line": i + 1,
                            "metadata": {
                                "block_type": block_type
                            }
                        })
                    
                    in_block = False
        
        return chunks
    
    async def _create_small_chunks(self, content: str, lines: List[str]) -> List[Dict[str, Any]]:
        """
        Create smaller chunks for files without clear semantic structure.
        """
        chunks = []
        chunk_size = 50
        
        for i in range(0, len(lines), chunk_size):
            end_idx = min(i + chunk_size, len(lines))
            chunk_content = '\n'.join(lines[i:end_idx])
            
            # Skip empty chunks
            if not chunk_content.strip():
                continue
            
            chunks.append({
                "type": "code_segment",
                "content": chunk_content,
                "start_line": i + 1,
                "end_line": end_idx,
                "metadata": {
                    "segment_index": len(chunks)
                }
            })
        
        return chunks