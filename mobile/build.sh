#!/bin/bash
# Build and test the FinAccAI Android app
set -e

cd "$(dirname "$0")/android"

echo "🔨 Building FinAccAI Mobile..."
echo ""

# Clean
echo "Cleaning build artifacts..."
./gradlew clean

# Build debug for testing
echo "Building debug APK..."
./gradlew assembleDebug
DEBUG_APK="app/build/outputs/apk/dev/debug/app-dev-debug.apk"

# Build release variants
echo "Building release APKs..."
./gradlew assembleProdRelease
./gradlew assembleStagingRelease

echo ""
echo "✅ Build complete!"
echo ""
echo "Output APKs:"
echo "  Debug (dev):       $DEBUG_APK"
echo "  Release (staging): app/build/outputs/apk/staging/release/app-staging-release.apk"
echo "  Release (prod):    app/build/outputs/apk/prod/release/app-release.apk"
echo ""
echo "To install on emulator/device:"
echo "  adb install -r $DEBUG_APK"
echo ""
echo "For Play Store release:"
echo "  1. Sign the prod APK (handled via signingConfigs if env vars are set)"
echo "  2. Upload app/build/outputs/apk/prod/release/app-release.apk to Play Console"
echo "  3. Follow DEPLOYMENT_GUIDE.md for store submission steps"
