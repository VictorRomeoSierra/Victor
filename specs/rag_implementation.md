# RAG and MCP Implementation for Victor

## Overview
This document details the Retrieval-Augmented Generation (RAG) and Multi-Context Programming (MCP) implementation for Victor, the AI coding assistant for DCS Lua development.

## RAG Architecture

### 1. Document Processing Pipeline

#### Code Ingestion
- **File Discovery**:
  - Recursive traversal of codebase
  - Filtering by extension (.lua, .cfg, etc.)
  - Metadata extraction (modification time, size, path)

- **Preprocessing**:
  - Comment extraction and normalization
  - Function and class identification
  - Dependency mapping between files

- **Chunking Strategy**:
  - Semantic chunking based on code structures
  - Overlap to maintain context across chunks
  - Special handling for long functions/classes

#### Embedding Generation
- **Embedding Model**:
  - Code-optimized embedding model (e.g., BGE, E5, or INSTRUCTOR)
  - Dimensionality: 768-1536 depending on model
  - Batch processing for efficiency

- **Storage Schema**:
  ```sql
  CREATE TABLE embeddings (
    id SERIAL PRIMARY KEY,
    file_path TEXT NOT NULL,
    chunk_id INTEGER NOT NULL,
    chunk_content TEXT NOT NULL,
    metadata JSONB NOT NULL,
    embedding vector(1536) NOT NULL
  );
  ```

### 2. Retrieval System

#### Query Processing
- **Query Understanding**:
  - Classification of query type (code explanation, flow analysis, purpose)
  - Extraction of relevant entities (functions, variables, files)
  - Query expansion with domain-specific knowledge

- **Hybrid Retrieval**:
  - Vector similarity search for semantic matching
  - Keyword-based filtering for specificity
  - Metadata filtering (file type, modification date)

#### Relevance Ranking
- **Ranking Factors**:
  - Embedding similarity score
  - Call graph proximity to query entities
  - Import/dependency relationships
  - Usage frequency of entity

- **Result Reranking**:
  - Cross-encoder reranking for precision
  - Diversity enforcement for context breadth
  - Recency bias for newer code

## MCP Implementation

### 1. Context Types

#### Code-Specific Contexts
- **Function Context**: Detailed information about specific functions
- **File Context**: Overall purpose and structure of a file
- **Module Context**: Interactions between related files
- **Call Graph Context**: Execution flow representation

#### Domain Knowledge Contexts
- **DCS API Context**: Information about DCS-specific APIs
- **Lua Patterns Context**: Common Lua idioms and best practices
- **XSAF Architecture Context**: Overall design principles of the codebase

### 2. Context Switching

#### Context Selection
- **Automatic Detection**:
  - Pattern matching to identify context needs
  - User intent analysis from query
  - Current file/location awareness

- **Manual Override**:
  - User-specified context preferences
  - Explicit context commands

#### Context Composition
- **Sequential Reasoning**:
  - Progressive context narrowing
  - Multi-step analysis with different contexts
  - Resolution of ambiguities

- **Parallel Reasoning**:
  - Multiple contexts applied simultaneously
  - Weighted combination of context outputs
  - Conflict resolution strategies

## Implementation Timeline

### Phase 1: Basic RAG (Weeks 1-2)
- Document processing pipeline
- Basic vector search
- Initial chunking strategy

### Phase 2: Advanced Retrieval (Weeks 3-4)
- Hybrid retrieval system
- Relevance ranking
- Query understanding

### Phase 3: MCP Implementation (Weeks 5-6)
- Context definitions
- Context switching logic
- User interface for context control

### Phase 4: Optimization (Weeks 7-8)
- Performance tuning
- Response quality improvement
- Edge case handling