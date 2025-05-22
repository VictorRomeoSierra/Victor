#!/bin/bash

# Debug script for Victor API container issues

echo "=== Victor API Container Debug ==="
echo

cd "$(dirname "$0")/../src/docker"

# Test with minimal API first
echo "1. Testing with minimal API..."
docker-compose exec victor-api python /app/src/api/main_minimal.py &
MINIMAL_PID=$!
sleep 3

echo "   Checking minimal API health..."
curl -s http://localhost:8000/health || echo "   Failed"

echo "   Checking debug endpoints..."
curl -s http://localhost:8000/debug/env | python3 -m json.tool || echo "   Env check failed"
curl -s http://localhost:8000/debug/imports | python3 -m json.tool || echo "   Import check failed"

kill $MINIMAL_PID 2>/dev/null

echo
echo "2. Checking Python environment in container..."
docker-compose exec victor-api python -c "import sys; print('Python:', sys.version)"
docker-compose exec victor-api python -c "import os; print('PYTHONPATH:', os.getenv('PYTHONPATH'))"
docker-compose exec victor-api python -c "import os; print('Working dir:', os.getcwd())"

echo
echo "3. Testing imports directly..."
docker-compose exec victor-api python -c "
try:
    import tree_sitter_languages
    print('✓ tree_sitter_languages')
except Exception as e:
    print('✗ tree_sitter_languages:', e)

try:
    import pgvector
    print('✓ pgvector')
except Exception as e:
    print('✗ pgvector:', e)

try:
    import asyncpg
    print('✓ asyncpg')
except Exception as e:
    print('✗ asyncpg:', e)

try:
    import openai
    print('✓ openai')
except Exception as e:
    print('✗ openai:', e)
"

echo
echo "4. Checking file structure..."
docker-compose exec victor-api ls -la /app/src/
docker-compose exec victor-api ls -la /app/src/api/
docker-compose exec victor-api ls -la /app/src/embedding/app/services/

echo
echo "5. Testing database connection..."
docker-compose exec victor-api python -c "
import asyncio
import asyncpg
import os

async def test_db():
    db_url = os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@host.docker.internal:5433/vectordb')
    print(f'Testing connection to: {db_url}')
    try:
        # Parse the URL for asyncpg
        if '+asyncpg' in db_url:
            db_url = db_url.replace('+asyncpg', '')
        conn = await asyncpg.connect(db_url)
        result = await conn.fetchval('SELECT 1')
        print(f'✓ Database connection successful: {result}')
        await conn.close()
    except Exception as e:
        print(f'✗ Database connection failed: {e}')

asyncio.run(test_db())
"

echo
echo "Run the following to see full startup logs:"
echo "cd src/docker && docker-compose logs victor-api | head -100"