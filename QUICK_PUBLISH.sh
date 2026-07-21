#!/bin/bash
# KRISH-AGENT INFINITY - QUICK PUBLISH SCRIPT
# Copy this to your project root and run: bash QUICK_PUBLISH.sh

set -e

echo "🚀 KRISH-AGENT INFINITY PUBLISHING SEQUENCE"
echo "=============================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Step 1: Check prerequisites
echo -e "${BLUE}📋 STEP 1: Checking prerequisites${NC}"
if ! command -v python &> /dev/null; then
    echo "❌ Python not found. Install Python 3.8+"
    exit 1
fi
echo "✓ Python $(python --version | awk '{print $2}')"

if ! pip list | grep -q build; then
    echo "📦 Installing build tools..."
    pip install --upgrade build twine setuptools wheel
fi
echo "✓ Build tools installed"
echo ""

# Step 2: Clean old builds
echo -e "${BLUE}🧹 STEP 2: Cleaning old builds${NC}"
rm -rf build/ dist/ *.egg-info/
echo "✓ Cleaned"
echo ""

# Step 3: Build package
echo -e "${BLUE}🏗️  STEP 3: Building package${NC}"
python -m build
BUILD_SUCCESS=$?
if [ $BUILD_SUCCESS -eq 0 ]; then
    echo "✓ Build successful"
    ls -lh dist/
else
    echo "❌ Build failed"
    exit 1
fi
echo ""

# Step 4: Check package
echo -e "${BLUE}📊 STEP 4: Checking package${NC}"
twine check dist/* --strict
echo "✓ Package valid"
echo ""

# Step 5: Pre-upload verification
echo -e "${BLUE}🧪 STEP 5: Local verification${NC}"
echo "Testing import..."
python -c "
try:
    from krish_agent.godmode import FinalForm
    from krish_agent.godmode_integration import activate_all_godmode_features
    from krish_agent.hyperinfinity import initialize_hyperinfinity
    from krish_agent.quantum_universe import initialize_quantum_universe
    print('✓ All modules import successfully')
except Exception as e:
    print(f'❌ Import error: {e}')
    exit(1)
"
echo ""

# Step 6: Ready for upload
echo -e "${GREEN}✅ READY FOR UPLOAD${NC}"
echo ""
echo -e "${YELLOW}To publish to PyPI:${NC}"
echo ""
echo "Option 1 - Automatic (credentials from .pypirc or env):"
echo "  ${GREEN}twine upload dist/*${NC}"
echo ""
echo "Option 2 - Interactive (prompt for credentials):"
echo "  ${GREEN}twine upload dist/* --verbose${NC}"
echo ""
echo "Option 3 - From environment variables:"
echo "  ${GREEN}export TWINE_USERNAME=__token__${NC}"
echo "  ${GREEN}export TWINE_PASSWORD=pypi-your-token${NC}"
echo "  ${GREEN}twine upload dist/*${NC}"
echo ""
echo -e "${YELLOW}Test installation after upload:${NC}"
echo "  ${GREEN}pip install krish-agent==3.0.0-GODMODE${NC}"
echo ""
echo -e "${YELLOW}Current package files ready:${NC}"
ls -lh dist/
echo ""
echo "🎉 Ready to ship your ∞^∞^∞^∞% better AI agent!"
echo ""
