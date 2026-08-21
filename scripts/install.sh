#!/bin/bash
# Install cache-ai from GitHub
set -e

pip install "git+https://github.com/FlossWare/cache-ai.git"

echo "cache-ai installed successfully"
echo "Verify: python3 -c 'import cache_ai; print(cache_ai.__version__)'"
