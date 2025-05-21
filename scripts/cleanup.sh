#!/bin/bash

# Cleanup script to maintain clean project root

# Navigate to project root
cd "$(dirname "$0")/.."
PROJECT_ROOT=$(pwd)

echo "Checking for redundant files in project root..."

# Files that should be in the project root
ALLOWED_FILES=(
  ".git"
  ".gitignore"
  ".env"
  ".env.example"
  ".claude"
  "README.md"
  "LICENSE"
  "CONTRIBUTING.md"
  "ai_docs"
  "config"
  "docs"
  "scripts"
  "specs"
  "src"
)

# Check each file in the root
for file in "$PROJECT_ROOT"/*; do
  filename=$(basename "$file")
  
  # Skip if it's in the allowed list
  if [[ " ${ALLOWED_FILES[*]} " =~ " ${filename} " ]]; then
    continue
  fi
  
  echo "Found redundant file: $filename"
  
  # Check file extension to determine where it should go
  if [[ "$filename" == *.md ]]; then
    echo "  This appears to be documentation, consider moving to docs/"
  elif [[ "$filename" == *.py ]]; then
    echo "  This appears to be Python code, consider moving to src/"
  elif [[ "$filename" == *.sh ]]; then
    echo "  This appears to be a script, consider moving to scripts/"
  elif [[ "$filename" == *.json || "$filename" == *.yaml || "$filename" == *.yml ]]; then
    echo "  This appears to be a configuration file, consider moving to config/"
  else
    echo "  This file may not belong in the project root"
  fi
  
  read -p "  Remove this file? (y/n): " -n 1 -r
  echo
  if [[ $REPLY =~ ^[Yy]$ ]]; then
    rm -rf "$file"
    echo "  Removed: $filename"
  fi
done

echo "Cleanup complete!"