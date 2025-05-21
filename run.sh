#!/bin/bash
# Wrapper script to maintain compatibility
exec "$(dirname "$0")/scripts/run.sh" "$@"