#!/bin/bash
# Clean and build using python3 -m build (modern method)

echo "🚀 Building with python3 -m build..."
rm -rf dist/ build/ *.egg-info/
python3 -m build
echo "✓ Done!"
ls -lh dist/
