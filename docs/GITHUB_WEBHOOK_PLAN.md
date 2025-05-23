# GitHub Webhook RAG Ingestion Pipeline

## Overview
Automatically update the Victor RAG database when code changes are pushed to the XSAF GitHub repository.

## Architecture

```
GitHub (XSAF Repo)
    │
    ├─[Push Event]
    │
    ▼
N8N Webhook Endpoint
    │
    ├─[Parse Event]
    ├─[Filter Branch]
    ├─[Extract Changed Files]
    │
    ▼
Victor API Reindex Endpoint
    │
    ├─[Fetch Changed Files]
    ├─[Parse Lua Code]
    ├─[Generate Embeddings]
    ├─[Update Database]
    │
    ▼
Notification System
    │
    ├─[Success/Failure]
    └─[Statistics]
```

## Implementation Steps

### 1. N8N Webhook Workflow
Create new workflow: "GitHub XSAF Indexing"

**Webhook Node**:
- Path: `/webhook/github-xsaf`
- Method: POST
- Response: Immediate (202 Accepted)

**Filter Node**:
```javascript
// Process pushes to main and development branches
const branch = $json.body.ref;
const allowedBranches = [
  'refs/heads/main',
  'refs/heads/master', 
  'refs/heads/vrsDevelopment'
];
const isBranchAllowed = allowedBranches.includes(branch);
const isPush = $json.headers['x-github-event'] === 'push';

return isBranchAllowed && isPush;
```

**Extract Changes Node**:
```javascript
// Extract changed Lua files
const commits = $json.body.commits || [];
const changedFiles = new Set();

commits.forEach(commit => {
  // Added files
  (commit.added || []).forEach(file => {
    if (file.endsWith('.lua')) changedFiles.add(file);
  });
  
  // Modified files
  (commit.modified || []).forEach(file => {
    if (file.endsWith('.lua')) changedFiles.add(file);
  });
  
  // Removed files (for deletion from index)
  (commit.removed || []).forEach(file => {
    if (file.endsWith('.lua')) changedFiles.add({ path: file, deleted: true });
  });
});

return Array.from(changedFiles);
```

### 2. Victor API Endpoint
Add new endpoint: `/api/reindex`

```python
@app.post("/api/reindex")
async def reindex_files(request: ReindexRequest):
    """
    Reindex specific files from GitHub
    """
    results = {
        "indexed": [],
        "failed": [],
        "deleted": []
    }
    
    for file_info in request.files:
        try:
            if file_info.get("deleted"):
                # Remove from database
                await delete_file_chunks(file_info["path"])
                results["deleted"].append(file_info["path"])
            else:
                # Fetch file content from GitHub
                content = await fetch_github_file(
                    repo=request.repository,
                    path=file_info["path"],
                    ref=request.ref
                )
                
                # Parse and index
                chunks = parse_lua_file(content, file_info["path"])
                await index_chunks(chunks)
                results["indexed"].append(file_info["path"])
                
        except Exception as e:
            results["failed"].append({
                "path": file_info["path"],
                "error": str(e)
            })
    
    return results
```

### 3. GitHub Repository Setup

**Add Webhook**:
1. Go to XSAF repo → Settings → Webhooks
2. Add webhook:
   - URL: `https://n8n.victorromeosierra.com/webhook/github-xsaf`
   - Content type: `application/json`
   - Events: Just the push event
   - Active: ✓

**Add Secret** (optional but recommended):
- Generate webhook secret
- Store in N8N workflow environment
- Validate signature in webhook node

### 4. Incremental Indexing Strategy

**Advantages**:
- Only process changed files
- Faster than full reindex
- Less resource intensive

**Implementation**:
```python
async def index_file_incrementally(file_path: str, content: str):
    # Delete existing chunks for this file
    await db.execute(
        "DELETE FROM lua_chunks WHERE file_path = $1",
        file_path
    )
    
    # Parse and insert new chunks
    chunks = parse_lua_file(content, file_path)
    for chunk in chunks:
        embedding = await generate_embedding(chunk.content)
        await db.execute(
            """
            INSERT INTO lua_chunks 
            (file_path, content, chunk_type, start_line, end_line, embedding)
            VALUES ($1, $2, $3, $4, $5, $6)
            """,
            chunk.file_path,
            chunk.content,
            chunk.chunk_type,
            chunk.start_line,
            chunk.end_line,
            embedding
        )
```

### 5. Monitoring & Notifications

**Success Notification**:
```javascript
// N8N Code node
const stats = $json.response;
const message = `✅ XSAF Reindexing Complete
- Files indexed: ${stats.indexed.length}
- Files deleted: ${stats.deleted.length}
- Failed: ${stats.failed.length}
- Time: ${executionTime}ms`;

// Send to Discord/Slack/Email
```

**Error Handling**:
- Retry failed files
- Log errors for debugging
- Alert on repeated failures

### 6. Security Considerations

1. **Webhook Validation**:
   - Verify GitHub signature
   - Check source IP
   - Validate payload structure

2. **Rate Limiting**:
   - Prevent abuse
   - Queue large updates

3. **Access Control**:
   - Restrict reindex endpoint
   - Require authentication

## Testing Plan

1. **Manual Test**:
   - Create test file in XSAF repo
   - Push to main branch
   - Verify indexing

2. **Load Test**:
   - Push multiple files
   - Verify queue handling

3. **Error Test**:
   - Invalid file content
   - Network failures
   - Database errors

## Future Enhancements

1. **Differential Updates**:
   - Only index changed functions
   - Track file versions

2. **Branch Support**:
   - Index feature branches
   - Tag different versions

3. **Analytics**:
   - Track indexing performance
   - Monitor code growth
   - Usage patterns