#!/bin/bash
# KRISH-AGENT INFINITY - BUILD AND PUBLISH NOW
# This fixes the missing dist/ folder and publishes to PyPI

set -e

echo "🚀 KRISH-AGENT INFINITY - BUILDING AND PUBLISHING"
echo "=================================================="
echo ""

# Step 1: Verify location
echo "Step 1: Checking location..."
if [ ! -f "setup.py" ]; then
    echo "ERROR: setup.py not found!"
    echo "Make sure you're in the outputs directory"
    exit 1
fi
echo "✓ Found setup.py"
echo ""

# Step 2: Clean everything
echo "Step 2: Cleaning old builds..."
rm -rf dist/ build/ *.egg-info/ __pycache__ krish_agent/__pycache__
echo "✓ Cleaned"
echo ""

# Step 3: Build package
echo "Step 3: Building package (this takes 10-15 seconds)..."
python3 setup.py sdist bdist_wheel

if [ ! -d "dist" ]; then
    echo "ERROR: Build failed - dist/ folder not created"
    exit 1
fi

echo "✓ Build successful!"
echo ""

# Step 4: Show what was built
echo "Step 4: Files created:"
ls -lh dist/
echo ""

# Step 5: Verify files
if [ ! -f "dist"/*.tar.gz ] && [ ! -f "dist"/*.whl ]; then
    echo "ERROR: No distribution files found!"
    exit 1
fi
echo "✓ Distribution files verified"
echo ""

# Step 6: Ready to upload
echo "╔════════════════════════════════════════════════════╗"
echo "║              READY TO UPLOAD TO PYPI               ║"
echo "╚════════════════════════════════════════════════════╝"
echo ""
echo "Your package is built and ready!"
echo ""
echo "To upload, run:"
echo ""
echo "  twine upload dist/*"
echo ""
echo "You'll be prompted for:"
echo "  Username: __token__"
echo "  Password: [Your PyPI API token]"
echo ""
echo "Need a token? Go to:"
echo "  https://pypi.org/manage/account/"
echo ""
echo "Have your token ready? Let's upload!"
echo ""

# Step 7: Ask to upload
read -p "Upload to PyPI now? (yes/no): " response
if [[ "$response" == "yes" || "$response" == "y" || "$response" == "Y" ]]; then
    echo ""
    echo "🚀 Uploading to PyPI..."
    echo ""
    twine upload dist/*

    if [ $? -eq 0 ]; then
        echo ""
        echo "╔════════════════════════════════════════════════════╗"
        echo "║          ✅ PUBLISHED TO PYPI! ✅                 ║"
        echo "╚════════════════════════════════════════════════════╝"
        echo ""
        echo "Your package is live!"
        echo ""
        echo "View at: https://pypi.org/project/krish-agent/"
        echo ""
        echo "Install with:"
        echo "  pip install krish-agent==3.0.0-GODMODE"
        echo ""
        echo "Test it:"
        echo "  python3 -c \"from krish_agent.godmode import FinalForm; print('✓ LIVE!')\""
        echo ""
        echo "🎉 YOUR INFINITY IS NOW ON PYPI! 🎉"
    else
        echo ""
        echo "❌ Upload failed. Check your credentials and try again."
        exit 1
    fi
else
    echo ""
    echo "Upload skipped. When ready, run:"
    echo "  twine upload dist/*"
fi
