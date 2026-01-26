#!/bin/bash
# Quick production verification script
# Run this before submitting to Play Store

set -e

cd "$(dirname "$0")"

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}🔍 FinAccAI Production Verification${NC}"
echo ""

PASSED=0
FAILED=0
WARNINGS=0

check_config() {
    local file=$1
    local pattern=$2
    local description=$3
    
    if grep -q "$pattern" "$file" 2>/dev/null; then
        echo -e "${GREEN}✓${NC} $description"
        ((PASSED++))
    else
        echo -e "${RED}✗${NC} $description"
        ((FAILED++))
    fi
}

check_not_contains() {
    local file=$1
    local pattern=$2
    local description=$3
    
    if ! grep -q "$pattern" "$file" 2>/dev/null; then
        echo -e "${GREEN}✓${NC} $description"
        ((PASSED++))
    else
        echo -e "${RED}✗${NC} $description (found: $pattern)"
        ((FAILED++))
    fi
}

warn_if_contains() {
    local file=$1
    local pattern=$2
    local description=$3
    
    if grep -q "$pattern" "$file" 2>/dev/null; then
        echo -e "${YELLOW}⚠${NC} $description"
        ((WARNINGS++))
    else
        echo -e "${GREEN}✓${NC} $description"
        ((PASSED++))
    fi
}

echo "Checking backend configuration..."
check_config "mobile/android/app/src/main/java/com/finaccai/mobile/Config.kt" \
    'BACKEND_URL_PROD = "https' \
    "Production endpoint uses HTTPS"

check_config "mobile/android/app/src/main/java/com/finaccai/mobile/Config.kt" \
    "ENFORCE_HTTPS_ONLY" \
    "HTTPS enforcement configured"

echo ""
echo "Checking security..."
check_not_contains "mobile/android/app/build.gradle" \
    'AUTH_TOKEN.*=.*"[^"]*"' \
    "No hardcoded auth tokens"

check_not_contains "mobile/android/app/src/main/AndroidManifest.xml" \
    'debuggable="true"' \
    "Debuggable flag not set"

check_config "mobile/android/app/src/main/res/xml/data_extraction_rules.xml" \
    'cleartextTrafficPermitted="false"' \
    "Cleartext traffic disabled"

echo ""
echo "Checking build configuration..."
check_config "mobile/android/app/build.gradle" \
    'versionName = "1.0' \
    "Version name configured"

check_config "mobile/android/app/build.gradle" \
    'minifyEnabled true' \
    "ProGuard obfuscation enabled"

check_config "mobile/android/app/build.gradle" \
    'shrinkResources true' \
    "Resource shrinking enabled"

check_config "mobile/android/app/build.gradle" \
    'signingConfig signingConfigs.release' \
    "Release signing configured"

echo ""
echo "Checking compliance..."
check_config "mobile/android/app/src/main/res/values/strings.xml" \
    'accessibility_service_description' \
    "Accessibility service description present"

check_config "mobile/android/app/src/main/AndroidManifest.xml" \
    'BIND_ACCESSIBILITY_SERVICE' \
    "Accessibility service declared"

check_config "mobile/PROD_CHECKLIST.md" \
    'Production Readiness' \
    "Checklist available"

echo ""
echo "Checking documentation..."
check_config "mobile/DEPLOYMENT_GUIDE.md" \
    'Play Store Deployment' \
    "Deployment guide present"

check_config "mobile/README.md" \
    'Production' \
    "Production info in README"

echo ""
echo "Environment check..."
if [ -n "$FINACCAI_KEYSTORE_PATH" ] && [ -f "$FINACCAI_KEYSTORE_PATH" ]; then
    echo -e "${GREEN}✓${NC} Keystore file exists"
    ((PASSED++))
else
    echo -e "${YELLOW}⚠${NC} Keystore not configured (needed for Play Store build)"
    ((WARNINGS++))
fi

if [ -n "$FINACCAI_KEYSTORE_PASSWORD" ]; then
    echo -e "${GREEN}✓${NC} Keystore password set"
    ((PASSED++))
else
    echo -e "${YELLOW}⚠${NC} Keystore password not set"
    ((WARNINGS++))
fi

echo ""
echo "=========================================="
echo -e "${GREEN}Passed:${NC}  $PASSED"
echo -e "${RED}Failed:${NC}  $FAILED"
echo -e "${YELLOW}Warnings:${NC} $WARNINGS"
echo "=========================================="
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✅ All checks passed! App is ready for production.${NC}"
    echo ""
    echo "Next steps:"
    echo "  1. Fill in PROD_CHECKLIST.md"
    echo "  2. Run: ./deploy-prod.sh"
    echo "  3. Upload APK to Play Store"
    exit 0
else
    echo -e "${RED}❌ $FAILED check(s) failed. Please fix before releasing.${NC}"
    exit 1
fi
