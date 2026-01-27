# FinAccAI Mobile — Play Store Deployment Guide

## Prerequisites
- Android Studio (latest)
- Java 17+
- A Google Play Developer account ($25 one-time)
- Your custom icon/branding files
- A privacy policy URL (required by Play Store)

## Step 1: Prepare App Branding

### App Icon
Replace the placeholder icon in your app. Create a 512x512 PNG or use Android Studio's Image Asset tool:
1. **Right-click** `res/` → **New** → **Image Asset**
2. Set foreground to your logo, background to app color
3. Studio generates all required resolutions

### App Name & Description
- **App Name**: Set in `app/src/main/res/values/strings.xml` `<string name="app_name">`
- **Description**: ~4000 characters in Play Console
- **Short Description**: ~80 characters

## Step 2: Setup Signing Configuration

### Generate a Keystore
```bash
cd mobile/android
export FINACCAI_KEYSTORE_PASSWORD='your-secure-password'
export FINACCAI_KEY_PASSWORD='your-secure-password'
./generate_keystore.sh
```

Store the keystore safely (e.g., encrypted cloud storage or secure CI/CD secret).

### Build Signed Release APK
```bash
cd mobile/android

# Production build
./gradlew assembleProdRelease

# Staging build (for pre-release testing)
./gradlew assembleStagingRelease

# Debug build for testing
./gradlew assembleDebug
```

APKs appear in: `app/build/outputs/apk/<flavor>/<buildType>/`

## Step 3: Security Hardening

### Update API Endpoints
Edit [app/src/main/java/com/finaccai/mobile/Config.kt](../android/app/src/main/java/com/finaccai/mobile/Config.kt):

```kotlin
const val BACKEND_URL_PROD = "https://api.finaccai.example.com"  // Use HTTPS
const val PRIVACY_POLICY_URL = "https://finaccai.example.com/privacy"
```

### Enable Auth Token (Optional)
Before building release:
```bash
export FINACCAI_AUTH_TOKEN='your-secret-api-token'
```

The `AuthInterceptor` automatically adds the token to all requests.

### Network Security
- `data_extraction_rules.xml` enforces HTTPS for production domains
- Disable cleartext traffic for all APIs
- Use certificate pinning for high-security deployments

## Step 4: Privacy & Compliance

### Privacy Policy
Create a clear privacy policy addressing:
- **Data Collected**: View hierarchies, optional screenshots, app names/versions
- **Data Processing**: Sent to your backend for accessibility analysis (rule-based + optional AI)
- **Data Retention**: Specify how long reports are kept
- **User Controls**: Screenshot toggle, opt-out for AI analysis
- **Security**: SSL/TLS in transit, no data shared with third parties

Host on your website and set in `Config.PRIVACY_POLICY_URL`.

### Accessibility Service Justification
The Play Store requires explanation for AccessibilityService. Set in manifest:
```xml
android:description="FinAccAI monitors app screens to analyze accessibility compliance..."
```

(Already configured in the app)

### Permissions
Requested:
- `INTERNET` — for backend communication
- `BIND_ACCESSIBILITY_SERVICE` — for the analyzer service

## Step 5: Play Store Setup

### Create App Listing
1. Go to [Google Play Console](https://play.google.com/console)
2. **Create app** → Fill in name, default language (English), category (Tools)
3. Accept declarations & fill in form

### Content Rating Questionnaire
- **Target Audience**: Professionals, Developers
- **Content**: No ads, no social features, no user-generated content

### App Content
- **APK/AAB upload**: Use the release APK from `app/build/outputs/`
- **Minimum API**: 24 (Android 7.0)
- **Target API**: 34 (Android 14)

### Store Listing
- **Title**: FinAccAI
- **Short Description**: "On-device accessibility auditing tool with rule-based and AI-powered checks"
- **Full Description**: Highlight rule-based checks, AI capabilities, WCAG compliance, real-time analysis
- **Screenshots**: 2–8 mobile screenshots showing the dashboard, report view, service setup
- **Feature Graphic**: 1024×500 PNG
- **Privacy Policy URL**: Required

### Release Management
1. Go to **Release** → **Production** (or **Open Testing** for beta)
2. Upload APK/AAB (recommended: AAB for automatic optimization per device)
3. Review changes, add release notes (e.g., "v1.0: Initial release")
4. **Review and roll out**

## Step 6: Testing Before Release

### Internal Testing
```bash
# Debug variant
./gradlew installDebug

# On device, open app:
# - Set backend to staging: https://staging.finaccai.example.com
# - Run sample analysis
# - Enable accessibility service, test live analysis
```

### Open Testing (Beta)
1. Upload release APK to Play Console → **Open Testing**
2. Create public link for testers
3. Collect feedback for 1–2 weeks

### Production Release
Once testing is complete:
1. Promote from Open Testing to Production
2. Or upload directly to Production with **Gradual rollout** (e.g., 25% → 50% → 100%)

## Step 7: Post-Release

### Monitoring
- **Google Play Console** → **Analytics** → Monitor crash rates, ratings, installation trends
- Set up in-app logging (privacy-respecting) to catch issues early

### Updates
- Increment `versionCode` and `versionName` in `app/build.gradle`
- Re-sign APK, upload to Play Console
- Publish new release with notes

### Support
- Respond to user reviews
- Monitor accessibility service permissions compliance
- Ensure backend uptime and security

## Environment Variants

The app includes three flavors (dev, staging, prod) with separate package IDs and backend URLs:

### Dev (for local testing)
- Package: `com.finaccai.mobile.dev`
- Backend: `http://10.0.2.2:5000` (emulator)
- Build: `./gradlew assembleDebug`

### Staging (for pre-release)
- Package: `com.finaccai.mobile.staging`
- Backend: `https://staging.finaccai.example.com`
- Build: `./gradlew assembleStagingRelease`

### Production (for Play Store)
- Package: `com.finaccai.mobile`
- Backend: `https://api.finaccai.example.com`
- Build: `./gradlew assembleProdRelease`

## Troubleshooting

### APK won't build
- Check SDK version: `compileSdk 34` requires Android SDK 34
- Run `./gradlew clean && ./gradlew assembleProdRelease`

### Signing fails
- Ensure `FINACCAI_KEYSTORE_PATH`, `FINACCAI_KEYSTORE_PASSWORD`, `FINACCAI_KEY_PASSWORD` are set
- Verify keystore exists and password is correct

### Play Store upload fails
- APK must be signed with the same key for all uploads
- Check that package name matches your Play Console app
- Review console error message for specifics

### Backend connectivity
- Verify API endpoint (HTTPS required for production)
- Check auth token is set if the backend requires it
- Ensure Network Security config allows your domain

## Final Checklist
- [ ] App icon finalized and included
- [ ] Privacy policy published and linked in Config
- [ ] HTTPS backend endpoint tested
- [ ] Keystore generated and securely stored
- [ ] Release APK signed and tested on device
- [ ] Accessibility service description in manifest
- [ ] All screens tested (sample analysis, live analysis, report viewing)
- [ ] Play Store listing completed with screenshots
- [ ] Open testing (beta) feedback incorporated
- [ ] Ready for production release
