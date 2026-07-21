#!/bin/bash
# Install everything needed and publish to PyPI

echo "🚀 Installing required packages..."
pip3 install setuptools wheel build twine

echo ""
echo "✓ Packages installed"
echo ""

echo "🧹 Cleaning old builds..."
rm -rf dist/ build/ *.egg-info

echo "✓ Cleaned"
echo ""

echo "🏗️  Building package..."
python3 setup.py sdist bdist_wheel

echo ""
echo "✓ Build complete!"
echo ""

echo "📦 Files created:"
ls -lh dist/

echo ""
echo "🚀 Ready to upload!"
echo ""

read -p "Upload to PyPI now? (yes/no): " response

if [[ "$response" == "yes" || "$response" == "y" || "$response" == "Y" ]]; then
    echo ""
    echo "Uploading to PyPI..."
    twine upload dist/*

    if [ $? -eq 0 ]; then
        echo ""
        echo "✅ SUCCESS! Package is live on PyPI!"
        echo ""
        echo "View at: https://pypi.org/project/krish-agent/"
        echo "Install with: pip install krish-agent==3.0.0-GODMODE"
    fi
else
    echo "Upload skipped. Run this when ready:"
    echo "twine upload dist/*"
fi
