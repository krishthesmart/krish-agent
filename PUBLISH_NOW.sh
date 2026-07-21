#!/bin/bash
# KRISH-AGENT INFINITY - DIRECT PyPI PUBLISHING SCRIPT
# Run this on your Mac terminal: bash PUBLISH_NOW.sh

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║     KRISH-AGENT INFINITY v3.0-GODMODE - PUBLISHING        ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Step 1: Verify we're in the right directory
echo -e "${BLUE}📍 Step 1: Verify directory${NC}"
if [ ! -f "setup.py" ]; then
    echo -e "${RED}❌ ERROR: setup.py not found!${NC}"
    echo "Make sure you're in the krish-agent output directory"
    exit 1
fi
echo -e "${GREEN}✓ Found setup.py${NC}"
pwd
echo ""

# Step 2: Check for build tools
echo -e "${BLUE}🔧 Step 2: Check build tools${NC}"
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python3 not found${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Python$(python3 --version)${NC}"

if ! pip3 list | grep -q twine; then
    echo -e "${YELLOW}⚠ Installing twine...${NC}"
    pip3 install twine
fi
echo -e "${GREEN}✓ twine installed${NC}"

if ! pip3 list | grep -q wheel; then
    echo -e "${YELLOW}⚠ Installing wheel...${NC}"
    pip3 install wheel
fi
echo -e "${GREEN}✓ wheel installed${NC}"
echo ""

# Step 3: Clean old builds
echo -e "${BLUE}🧹 Step 3: Cleaning old builds${NC}"
rm -rf dist/ build/ *.egg-info/ __pycache__/
echo -e "${GREEN}✓ Cleaned${NC}"
echo ""

# Step 4: Build package
echo -e "${BLUE}🏗️  Step 4: Building package${NC}"
python3 setup.py sdist bdist_wheel
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Build successful${NC}"
else
    echo -e "${RED}❌ Build failed${NC}"
    exit 1
fi
echo ""

# Step 5: Show what we built
echo -e "${BLUE}📦 Step 5: Built files${NC}"
ls -lh dist/
echo ""

# Step 6: Verify package
echo -e "${BLUE}✓ Step 6: Verifying package${NC}"
if command -v twine &> /dev/null; then
    twine check dist/*
    echo -e "${GREEN}✓ Package valid${NC}"
else
    echo -e "${YELLOW}⚠ twine not available for check (skipping)${NC}"
fi
echo ""

# Step 7: Ready to upload
echo -e "${YELLOW}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${YELLOW}║                    READY TO UPLOAD                         ║${NC}"
echo -e "${YELLOW}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${GREEN}Your package is ready!${NC}"
echo ""
echo "To upload to PyPI, run:"
echo -e "${BLUE}twine upload dist/*${NC}"
echo ""
echo "When prompted, enter:"
echo -e "  Username: ${GREEN}__token__${NC}"
echo -e "  Password: ${GREEN}[Your PyPI API token]${NC}"
echo ""
echo "Need your API token?"
echo "  → https://pypi.org/manage/account/"
echo ""
echo "Or set environment variables:"
echo "  export TWINE_USERNAME=\"__token__\""
echo "  export TWINE_PASSWORD=\"pypi-YOUR_TOKEN\""
echo "  twine upload dist/*"
echo ""

# Prompt to upload
read -p "Upload to PyPI now? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${BLUE}🚀 Uploading to PyPI...${NC}"
    twine upload dist/*
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ PUBLISHED SUCCESSFULLY!${NC}"
        echo ""
        echo "Your package is now on PyPI!"
        echo "View at: https://pypi.org/project/krish-agent/"
        echo ""
        echo "Install with: pip install krish-agent==3.0.0-GODMODE"
        echo ""
        echo -e "${YELLOW}🎉 YOUR INFINITY IS NOW LIVE! 🎉${NC}"
    else
        echo -e "${RED}❌ Upload failed${NC}"
        exit 1
    fi
else
    echo -e "${YELLOW}⏳ Upload skipped${NC}"
    echo "When ready, run: ${BLUE}twine upload dist/*${NC}"
fi
