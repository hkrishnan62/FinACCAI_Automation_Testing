#!/bin/bash
# FinAccAI Mobile - Production Readiness Verification
# Comprehensive checklist for Play Store submission

set -e

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

PASSED=0
FAILED=0
WARNINGS=0

check_file() {
    local file=$1
    local description=$2
    if [ -f "$file" ] || [ -d "$file" ]; then
        echo -e "${GREEN}✓${NC} $description"
        ((PASSED++))
    else
        echo -e "${RED}✗${NC} $description (missing: $file)"
        ((FAILED++))
    fi
}

check_content() {
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

echo -e "${BLUE}════════════════════════════════════════${NC}"
echo -e "${BLUE}FinAccAI Mobile - Production Readiness${NC}"
echo -e "${BLUE}════════════════════════════════════════${NC}\n"

# 1. Environment Configuration
echo -e "${BLUE}📋 Environment Configuration${NC}"
check_file ".env.prod" "Production environment (.env.prod)"
check_file ".env.prod.example" "Environment template (.env.prod.example)"
check_file "setup-prod-env.sh" "Setup script (setup-prod-env.sh)"
check_content ".env.prod" "FINACCAI_BACKEND_URL" "Backend URL configured"
check_content ".env.prod" "FINACCAI_KEYSTORE_PATH" "Keystore path configured"
echo ""

# 2. Signing & Security
echo -e "${BLUE}🔐 Signing & Security${NC}"
check_file "mobile/android/finaccai-prod.jks" "Production keystore"
check_file "mobile/verify-prod.sh" "Production verification script"
check_file "mobile/deploy-prod.sh" "Production deployment script"
check_content "mobile/android/app/build.gradle" "minifyEnabled true" "ProGuard obfuscation enabled"
check_content "mobile/android/app/build.gradle" "shrinkResources true" "Resource shrinking enabled"
check_content "mobile/android/app/src/main/AndroidManifest.xml" 'debuggable="false"' "Debuggable disabled"
echo ""

# 3. Source Code
echo -e "${BLUE}💻 Source Code${NC}"
check_file "mobile/android/app/src/main/java/com/finaccai/mobile/MainActivity.kt" "MainActivity"
check_file "mobile/android/app/src/main/java/com/finaccai/mobile/FinAccAIAccessibilityService.kt" "AccessibilityService"
check_file "mobile/android/app/src/main/java/com/finaccai/mobile/Config.kt" "Config"
check_file "mobile/android/app/src/main/java/com/finaccai/mobile/ReportEntry.kt" "ReportEntry"
check_file "mobile/android/app/src/main/java/com/finaccai/mobile/ReportAdapter.kt" "ReportAdapter"
check_file "mobile/android/app/src/main/java/com/finaccai/mobile/Prefs.kt" "Preferences"
check_file "mobile/android/app/src/main/java/com/finaccai/mobile/AuthInterceptor.kt" "Auth interceptor"
check_file "mobile/android/app/src/main/java/com/finaccai/mobile/PrivacyPolicyActivity.kt" "Privacy activity"
echo ""

# 4. Resources & UI
echo -e "${BLUE}🎨 Resources & UI${NC}"
check_file "mobile/android/app/src/main/res/layout/activity_main.xml" "Main activity layout"
check_file "mobile/android/app/src/main/res/layout/item_report.xml" "Report item layout"
check_file "mobile/android/app/src/main/res/values/colors.xml" "Color resources"
check_file "mobile/android/app/src/main/res/values/strings.xml" "String resources"
check_file "mobile/android/app/src/main/res/values/themes.xml" "Theme resources"
check_file "mobile/android/app/src/main/res/xml/data_extraction_rules.xml" "Network security config"
check_file "mobile/android/app/src/main/res/xml/accessibility_service_config.xml" "Accessibility config"
echo ""

# 5. Manifest & Configs
echo -e "${BLUE}⚙️  Manifest & Configurations${NC}"
check_file "mobile/android/AndroidManifest.xml" "Android manifest"
check_file "mobile/android/build.gradle" "Project build.gradle"
check_file "mobile/android/app/build.gradle" "App build.gradle"
check_content "mobile/android/AndroidManifest.xml" "INTERNET" "INTERNET permission declared"
check_content "mobile/android/AndroidManifest.xml" "BIND_ACCESSIBILITY_SERVICE" "AccessibilityService permission"
check_content "mobile/android/AndroidManifest.xml" "com.finaccai.mobile" "Package name correct"
echo ""

# 6. Play Store Assets
echo -e "${BLUE}📦 Play Store Assets${NC}"
check_file "mobile/play_store_assets/icons/app_icon_512.png" "App icon (512×512)"
check_file "mobile/play_store_assets/graphics/feature_graphic_1024x500.png" "Feature graphic (1024×500)"
check_file "mobile/play_store_assets/screenshots/phone_1_1080x1920.png" "Phone screenshot 1"
check_file "mobile/play_store_assets/screenshots/phone_2_1080x1920.png" "Phone screenshot 2"
check_file "mobile/play_store_assets/screenshots/phone_3_1080x1920.png" "Phone screenshot 3"
check_file "mobile/play_store_assets/screenshots/phone_4_1080x1920.png" "Phone screenshot 4"
check_file "mobile/play_store_assets/screenshots/phone_5_1080x1920.png" "Phone screenshot 5"
check_file "mobile/play_store_assets/screenshots/tablet_1_1920x1080.png" "Tablet screenshot 1"
check_file "mobile/play_store_assets/screenshots/tablet_2_1920x1080.png" "Tablet screenshot 2"
echo ""

# 7. Documentation
echo -e "${BLUE}📚 Documentation${NC}"
check_file "PRODUCTION_STATUS.md" "Production status report"
check_file "SUBMIT_TO_PLAY_STORE.md" "Play Store submission guide"
check_file "PLAY_STORE_DEPLOYMENT.md" "Deployment guide"
check_file "mobile/DEPLOYMENT_GUIDE.md" "Mobile deployment guide"
check_file "mobile/README.md" "Mobile app README"
check_file "PROD_CHECKLIST.md" "Production checklist"
echo ""

# 8. Configuration Content
echo -e "${BLUE}✅ Configuration Content${NC}"
check_content "mobile/android/app/src/main/java/com/finaccai/mobile/Config.kt" \
    'BACKEND_URL_PROD = "https' "Production endpoint HTTPS"
check_content "mobile/android/app/src/main/java/com/finaccai/mobile/Config.kt" \
    "ENFORCE_HTTPS_ONLY" "HTTPS enforcement flag"
check_content "mobile/android/app/src/main/java/com/finaccai/mobile/Config.kt" \
    'PRIVACY_POLICY_URL = "https' "Privacy policy URL"
check_content "mobile/android/app/src/main/java/com/finaccai/mobile/Config.kt" \
    'VERSION_NAME = "1.0' "Version configured"
check_content "mobile/android/app/build.gradle" \
    "ENABLE_CRASH_REPORTING" "Crash reporting flag"
check_content "mobile/android/app/build.gradle" \
    "ENABLE_ANALYTICS" "Analytics flag"
echo ""

# 9. Build Configuration
echo -e "${BLUE}🔨 Build Configuration${NC}"
check_content "mobile/android/app/build.gradle" "versionName" "Version name in gradle"
check_content "mobile/android/app/build.gradle" "versionCode" "Version code in gradle"
check_content "mobile/android/app/build.gradle" "targetSdkVersion" "Target SDK version"
check_content "mobile/android/app/build.gradle" "minSdkVersion" "Min SDK version"
check_content "mobile/android/app/build.gradle" 'applicationId = "' "Application ID defined"
echo ""

# 10. Network Security
echo -e "${BLUE}🛡️  Network Security${NC}"
check_content "mobile/android/app/src/main/res/xml/data_extraction_rules.xml" \
    'cleartextTrafficPermitted="false"' "Cleartext traffic disabled"
check_content "mobile/android/app/src/main/res/xml/data_extraction_rules.xml" \
    'api.finaccai.com' "Production domain in security rules"
echo ""

# 11. Backend Integration
echo -e "${BLUE}🌐 Backend Integration${NC}"
check_content "mobile/android/app/src/main/java/com/finaccai/mobile/Config.kt" \
    "ENDPOINT_ANALYZE" "Analyze endpoint defined"
check_content "mobile/android/app/src/main/java/com/finaccai/mobile/Config.kt" \
    "ENDPOINT_HEALTH" "Health endpoint defined"
check_content "mobile/android/app/src/main/java/com/finaccai/mobile/AuthInterceptor.kt" \
    "Authorization" "Auth token injection"
echo ""

# Summary
echo -e "${BLUE}════════════════════════════════════════${NC}"
echo -e "${BLUE}Summary${NC}"
echo -e "${BLUE}════════════════════════════════════════${NC}"
echo ""
echo -e "${GREEN}✓ Passed: $PASSED${NC}"
if [ $FAILED -gt 0 ]; then
    echo -e "${RED}✗ Failed: $FAILED${NC}"
fi
if [ $WARNINGS -gt 0 ]; then
    echo -e "${YELLOW}⚠ Warnings: $WARNINGS${NC}"
fi

echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✅ All checks passed! Ready for Play Store submission.${NC}"
    echo ""
    echo -e "${BLUE}Next steps:${NC}"
    echo "1. Create Google Play Developer account (https://play.google.com/console)"
    echo "2. Create new app in Play Console"
    echo "3. Follow: SUBMIT_TO_PLAY_STORE.md"
    echo "4. Build APK: source .env.prod && cd mobile && bash deploy-prod.sh"
    echo "5. Upload APK to Play Console"
    echo "6. Submit for review"
    echo ""
    exit 0
else
    echo -e "${RED}❌ Some checks failed. Review issues above.${NC}"
    echo ""
    echo -e "${BLUE}Common issues:${NC}"
    echo "1. Missing .env.prod - Copy from .env.prod.example and fill in values"
    echo "2. Missing keystore - Run: cd mobile/android && bash generate_keystore.sh"
    echo "3. Missing assets - Run: bash mobile/create_play_store_assets.sh"
    echo ""
    exit 1
fi
