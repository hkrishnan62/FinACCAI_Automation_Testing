#!/bin/bash
# Production build and deployment script for FinAccAI Mobile
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
# Handle both root and mobile directory execution
if [ "$(basename "$SCRIPT_DIR")" = "mobile" ]; then
    cd "$SCRIPT_DIR/android"
else
    cd "$SCRIPT_DIR/mobile/android"
fi

# Color output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 FinAccAI Mobile — Production Build${NC}"
echo ""

# Check environment
echo "Checking production environment..."

if [ -z "$FINACCAI_KEYSTORE_PATH" ]; then
    echo -e "${RED}❌ FINACCAI_KEYSTORE_PATH not set${NC}"
    exit 1
fi

if [ -z "$FINACCAI_KEYSTORE_PASSWORD" ]; then
    echo -e "${RED}❌ FINACCAI_KEYSTORE_PASSWORD not set${NC}"
    exit 1
fi

if [ -z "$FINACCAI_KEY_PASSWORD" ]; then
    echo -e "${RED}❌ FINACCAI_KEY_PASSWORD not set${NC}"
    exit 1
fi

if [ ! -f "$FINACCAI_KEYSTORE_PATH" ]; then
    echo -e "${RED}❌ Keystore file not found: $FINACCAI_KEYSTORE_PATH${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Keystore configured${NC}"

if [ -z "$FINACCAI_BACKEND_URL" ]; then
    FINACCAI_BACKEND_URL="https://api.finaccai.example.com"
    echo -e "${YELLOW}⚠ Using default backend URL: $FINACCAI_BACKEND_URL${NC}"
fi

if [ -z "$FINACCAI_PRIVACY_POLICY_URL" ]; then
    FINACCAI_PRIVACY_POLICY_URL="https://finaccai.example.com/privacy"
    echo -e "${YELLOW}⚠ Using default privacy URL: $FINACCAI_PRIVACY_POLICY_URL${NC}"
fi

echo ""
echo "Configuration:"
echo "  Backend: $FINACCAI_BACKEND_URL"
echo "  Privacy: $FINACCAI_PRIVACY_POLICY_URL"
echo "  Keystore: $FINACCAI_KEYSTORE_PATH"
echo ""

# Clean
echo "Cleaning build artifacts..."
./gradlew clean > /dev/null 2>&1

# Build production release
echo "Building production release APK..."
./gradlew assembleProdRelease --stacktrace

RELEASE_APK="app/build/outputs/apk/prod/release/app-release.apk"
RELEASE_MAPPING="app/build/outputs/mapping/prodRelease/mapping.txt"

if [ ! -f "$RELEASE_APK" ]; then
    echo -e "${RED}❌ Build failed: APK not generated${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Production APK built${NC}"
echo ""

# Get APK info
APK_SIZE=$(du -h "$RELEASE_APK" | cut -f1)
APK_SHA256=$(sha256sum "$RELEASE_APK" | awk '{print $1}')

echo "Build Artifacts:"
echo "  APK: $RELEASE_APK"
echo "  Size: $APK_SIZE"
echo "  SHA256: $APK_SHA256"
echo ""

if [ -f "$RELEASE_MAPPING" ]; then
    echo "  ProGuard mapping: $RELEASE_MAPPING"
    echo "  ⚠️  Keep mapping.txt safe for crash analysis!"
    echo ""
fi

echo -e "${GREEN}✅ Production build complete!${NC}"
echo ""
echo "Next steps:"
echo "  1. Test on physical device:"
echo "     adb install -r $RELEASE_APK"
echo ""
echo "  2. Verify in-app:"
echo "     - Check backend URL is production"
echo "     - Run sample analysis"
echo "     - Enable accessibility service"
echo "     - Test live app capture"
echo ""
echo "  3. Upload to Play Store:"
echo "     - Go to Google Play Console"
echo "     - Select FinAccAI app"
echo "     - Release → Production"
echo "     - Upload: $RELEASE_APK"
echo "     - Follow on-screen prompts"
echo ""
echo "  4. Post-launch:"
echo "     - Monitor crash reports"
echo "     - Track ratings and reviews"
echo "     - Check analytics"
echo ""
