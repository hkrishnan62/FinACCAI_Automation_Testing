# FinAccAI Mobile — Production Readiness Checklist

## ✅ Pre-Build Checklist

### Branding & Identity
- [ ] Custom app icon created (512x512 PNG minimum)
  - [ ] Placed in `res/mipmap-*/` directories via Image Asset tool
  - [ ] Launcher icon (rounded) and adaptive icon configured
- [ ] App name finalized: `res/values/strings.xml` → `app_name`
- [ ] App short description (80 chars max) ready for Play Store
- [ ] App long description (4000 chars max) highlighting features

### Security & Compliance
- [ ] Privacy Policy published and accessible
  - [ ] URL set in `Config.PRIVACY_POLICY_URL`
  - [ ] Addresses data collection, processing, retention, user controls
- [ ] Terms of Service drafted (if applicable)
- [ ] Accessibility Service justification reviewed and finalized
- [ ] WCAG 2.1 AA compliance verified for the app UI itself

### Backend Configuration
- [ ] Production API endpoint finalized
  - [ ] HTTPS enabled (no cleartext)
  - [ ] Certificate valid and not self-signed
  - [ ] Health check endpoint responsive (`/api/health`)
- [ ] API authentication token generated (if required)
  - [ ] Token securely stored in CI/CD secret manager
  - [ ] NOT hardcoded in app or version control
- [ ] Rate limiting configured on backend
- [ ] CORS headers properly set for mobile clients

### Build Configuration
- [ ] `Config.kt` endpoints updated:
  ```kotlin
  const val BACKEND_URL_PROD = "https://api.finaccai.example.com"
  const val PRIVACY_POLICY_URL = "https://finaccai.example.com/privacy"
  ```
- [ ] Version code incremented (in `app/build.gradle`)
  - [ ] Each Play Store release requires `versionCode` to increase
- [ ] Version name updated (e.g., `1.0.0`)
- [ ] Debug logging disabled (`Config.ENABLE_DEBUG_LOGGING = false`)
- [ ] Crash reporting enabled (Firebase, Sentry, or similar)

### Signing Configuration
- [ ] Keystore generated and securely stored
  ```bash
  export FINACCAI_KEYSTORE_PASSWORD='your-password'
  export FINACCAI_KEY_PASSWORD='your-password'
  ./mobile/android/generate_keystore.sh
  ```
- [ ] Keystore backed up in secure location (encrypted cloud, vault, etc.)
- [ ] Signing environment variables documented and accessible to CI/CD
- [ ] Test release build signed successfully

### Network & Security
- [ ] `data_extraction_rules.xml` updated with production domains
- [ ] Cleartext traffic disabled for production (`cleartextTrafficPermitted="false"`)
- [ ] Certificate pinning considered (for high-security apps)
- [ ] Auth token interceptor working (`AuthInterceptor.kt`)
- [ ] Network timeouts set reasonably (30-60s)

---

## ✅ Build & Test Checklist

### Debug Build (Internal Testing)
```bash
cd mobile/android
./gradlew assembleDebug
adb install -r app/build/outputs/apk/dev/debug/app-dev-debug.apk
```
- [ ] App installs without errors
- [ ] Dashboard displays correctly
- [ ] Backend URL defaults to dev server
- [ ] Sample analysis completes successfully

### Staging Build (Pre-Release Testing)
```bash
./gradlew assembleStagingRelease
```
- [ ] APK signs correctly
- [ ] App runs on multiple devices (different screen sizes, Android versions)
- [ ] Accessibility Service can be enabled
- [ ] Reports save and display properly

### Production Release Build
```bash
export FINACCAI_KEYSTORE_PATH="/path/to/keystore.jks"
export FINACCAI_KEYSTORE_PASSWORD="password"
export FINACCAI_KEY_PASSWORD="password"

./gradlew assembleProdRelease
```
- [ ] APK signed with production key
- [ ] APK size reasonable (<50 MB recommended)
- [ ] ProGuard obfuscation working (verify with `strings app-release.apk | grep -v "^#"`)
- [ ] Resources shrunk successfully

### Device Testing (Physical Devices)
- [ ] Test on Android 7.0 (API 24) - minimum supported
- [ ] Test on Android 14 (API 34) - latest
- [ ] Test on multiple screen sizes (phone, tablet)
- [ ] Test on both WiFi and mobile networks

### Functional Testing
- [ ] **Dashboard loads** without crashes
- [ ] **Settings persist** across app restarts
- [ ] **Sample analysis** completes in <30s
- [ ] **Live analysis** via Accessibility Service works
  - [ ] Enable in Settings → Accessibility
  - [ ] Open another app, observe capture
- [ ] **Reports display** correctly
- [ ] **Privacy policy link** opens
- [ ] **Backend health check** works ("Analyze current app" button)
- [ ] **AI/ML toggle** saves preference
- [ ] **Screenshot toggle** disables capture when off

### Permission Testing
- [ ] **INTERNET** permission granted automatically
- [ ] **BIND_ACCESSIBILITY_SERVICE** prompts in system settings
- [ ] Accessibility Service can be enabled/disabled without crashes
- [ ] No unusual permission requests

### Performance Testing
- [ ] App launches in <3s
- [ ] Dashboard scrolling smooth (60 FPS)
- [ ] Analysis completes within timeout
- [ ] No ANRs (Application Not Responding) over 5 minutes
- [ ] Memory usage stable (<100 MB typical)

### Security Testing
- [ ] All network traffic goes through HTTPS
- [ ] No sensitive data logged to Logcat
- [ ] No hardcoded credentials in APK
- [ ] Keystore password not stored in code/version control
- [ ] Privacy policy link doesn't leak referrer data

---

## ✅ Play Store Submission Checklist

### Create Play Console App
- [ ] Google Play Developer account active ($25 lifetime fee)
- [ ] App created in Play Console
- [ ] Package name matches signing config: `com.finaccai.mobile`

### Store Listing
- [ ] **Title**: FinAccAI (max 50 chars)
- [ ] **Short description**: "On-device accessibility auditing with AI" (80 chars)
- [ ] **Full description** (4000 chars):
  - [ ] Key features highlighted
  - [ ] WCAG compliance mentioned
  - [ ] AI/ML capabilities explained
  - [ ] Rule-based checks listed
  - [ ] Real-time live analysis noted
  - [ ] Privacy/data handling explained
- [ ] **Category**: Tools
- [ ] **Content rating**: Non-rated or age appropriate
  - [ ] IARC questionnaire completed if required

### Branding
- [ ] **App icon** (512x512 PNG): professional, clear
- [ ] **Feature graphic** (1024x500 PNG): showcase app functionality
- [ ] **Screenshots** (2-8 required, 1080x1920 min):
  - [ ] Dashboard overview
  - [ ] Sample analysis result
  - [ ] Accessibility Service setup
  - [ ] Live analysis in action
  - [ ] Report viewing
- [ ] **Video** (optional): 30s demo

### Legal & Compliance
- [ ] **Privacy Policy URL** set and publicly accessible
- [ ] **Terms of Service** (if required)
- [ ] **Accessibility** compliance claimed:
  - [ ] WCAG 2.1 AA
  - [ ] No barriers to usage
- [ ] **Content Rating** submitted (IARC if needed)
- [ ] **Data Safety** form completed:
  - [ ] Declare data collected (view hierarchies, optional screenshots)
  - [ ] Declare encryption in transit (HTTPS)
  - [ ] Declare retention policy
  - [ ] Declare no third-party sharing

### APK/AAB Upload
- [ ] Production APK signed with correct keystore
- [ ] APK uploaded to Play Console
  - [ ] **Release type**: Production (or Closed Testing for beta)
  - [ ] **Release notes**: "v1.0: Initial release with AI-powered accessibility analysis"
- [ ] **Minimum API**: 24 (Android 7.0)
- [ ] **Target API**: 34 (Android 14)

### Review & Approval
- [ ] All required fields completed
- [ ] No warnings in Play Console
- [ ] Submission reviewed for compliance
- [ ] Wait for Google Play review (typically 2-4 hours)

---

## ✅ Post-Launch Checklist

### Monitoring
- [ ] **Play Console Analytics** checked daily for first week
  - [ ] Installation numbers
  - [ ] Crash reports (keep crash-free rate >95%)
  - [ ] Ratings and reviews
  - [ ] User retention
- [ ] **Backend logs** monitored for errors
  - [ ] API error rates <1%
  - [ ] Response times <2s p99
- [ ] **Crash reporting service** active (Firebase, Sentry, etc.)

### User Support
- [ ] Support email set up and monitored
- [ ] FAQ prepared for common issues
- [ ] Respond to reviews professionally
- [ ] Track feature requests

### Updates & Maintenance
- [ ] Plan for regular updates (quarterly minimum)
- [ ] Security patches applied immediately
- [ ] User feedback incorporated into roadmap

---

## 🚀 Final Sign-Off

**Before submitting to Google Play, sign off on:**

- [ ] **Build Owner** (Developer/Lead): _______________ Date: _____
- [ ] **Security Review** (Security Lead): _______________ Date: _____
- [ ] **QA Sign-Off** (QA Lead): _______________ Date: _____
- [ ] **Product Owner** (PM): _______________ Date: _____

---

## 📞 Emergency Contacts

If issues arise post-launch, contact:
- **Backend Support**: [Your backend team contact]
- **Google Play Support**: [Your Google Play Console admin]
- **Security Incident**: [Your security contact]

---

## 📚 Additional Resources

- [Play Store Developer Program Policies](https://play.google.com/about/developer-content-policy/)
- [Android Security & Privacy Best Practices](https://developer.android.com/privacy-and-security)
- [WCAG 2.1 Accessibility Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)
- [Android App Architecture Guide](https://developer.android.com/jetpack/guide)

---

**Status**: Ready for Production ✅  
**Last Updated**: January 25, 2026  
**Version**: 1.0.0
