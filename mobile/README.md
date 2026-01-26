# FinAccAI Mobile (Android)

This folder contains the complete production-ready Android app for shipping FinAccAI on Google Play.

## What's Included
- Full-featured native Android app with SeeTest-inspired dashboard UI
- Real-time accessibility analysis via rule-based + AI pipelines
- AccessibilityService for live app auditing in the foreground
- Report history and persistence with SharedPreferences
- Secure network stack with token-based auth and HTTPS enforcement
- Build variants (dev/staging/prod) with environment-specific endpoints
- Signing configuration and release build tooling
- Privacy policy and accessibility service justification

## Quick Start (Development)
```bash
# 1. Backend: start the analyzer
python browser-extension/api_server.py

# 2. Open Android Studio and load mobile/android/
# 3. Edit baseUrl in MainActivity.kt to match your backend (e.g., http://10.0.2.2:5000 for emulator)
# 4. Build & run the app

# Or use CLI:
cd mobile/android
./gradlew assembleDebug
adb install -r app/build/outputs/apk/dev/debug/app-dev-debug.apk
```

## Dashboard Features
- **Hero Banner**: Service status chip + feature toggles (AI, screenshots)
- **Analyzer Card**: Configure backend URL, run sample analysis
- **Live Analysis**: Button to verify backend health and enable accessibility service
- **Recent Reports**: RecyclerView of past analyses with timestamps and issue counts
- **Report Viewer**: Tap any report to open in Custom Tabs or Chrome

## Architecture
```
app/
├── src/main/
│   ├── java/com/finaccai/mobile/
│   │   ├── MainActivity.kt               # Main dashboard
│   │   ├── FinAccAIAccessibilityService.kt  # Background analyzer
│   │   ├── ReportEntry.kt               # Data model
│   │   ├── ReportAdapter.kt             # Report list adapter
│   │   ├── Prefs.kt                     # Shared preferences helper
│   │   ├── Config.kt                    # Environment config
│   │   ├── AuthInterceptor.kt           # Secure network stack
│   │   └── PrivacyPolicyActivity.kt     # Privacy policy viewer
│   ├── res/
│   │   ├── layout/                      # UI layouts
│   │   │   ├── activity_main.xml        # Dashboard
│   │   │   ├── item_report.xml          # Report list item
│   │   │   └── activity_privacy_policy.xml
│   │   ├── values/                      # Resources
│   │   │   ├── colors.xml               # SeeTest palette
│   │   │   ├── strings.xml              # UI text
│   │   │   └── themes.xml               # Material 3 theme
│   │   ├── drawable/                    # Drawables
│   │   │   └── hero_bg.xml              # Gradient backgrounds
│   │   └── xml/                         # Config files
│   │       ├── accessibility_service_config.xml
│   │       ├── data_extraction_rules.xml   # Network security
│   │       └── backup_rules.xml
│   └── AndroidManifest.xml
├── build.gradle                         # App config + signing
└── proguard-rules.pro                   # Code obfuscation
```

## Build Variants

### Dev (Local Testing)
```bash
./gradlew assembleDebug
# Package: com.finaccai.mobile.dev
# Backend: http://10.0.2.2:5000 (emulator default)
```

### Staging (Pre-Release Testing)
```bash
./gradlew assembleStagingRelease
# Package: com.finaccai.mobile.staging
# Backend: https://staging.finaccai.example.com
```

### Production (Play Store)
```bash
./gradlew assembleProdRelease
# Package: com.finaccai.mobile
# Backend: https://api.finaccai.example.com
```

## Secure Network Stack

- **AuthInterceptor**: Automatically injects `Authorization: Bearer <token>` if `Config.AUTH_TOKEN` is set
- **Data Extraction Rules** (`data_extraction_rules.xml`): Enforces HTTPS for production domains
- **No Cleartext Traffic**: Disables HTTP for production, allows only for dev/emulator

Set auth token:
```bash
export FINACCAI_AUTH_TOKEN='your-api-token'
```

## Signing Configuration

### Generate Keystore (one-time)
```bash
export FINACCAI_KEYSTORE_PASSWORD='your-secure-password'
export FINACCAI_KEY_PASSWORD='your-secure-password'
./android/generate_keystore.sh
```

### Build Signed Release
```bash
export FINACCAI_KEYSTORE_PATH=/path/to/keystore.jks
export FINACCAI_KEYSTORE_PASSWORD='your-password'
export FINACCAI_KEY_PASSWORD='your-password'

cd mobile/android
./gradlew assembleProdRelease
```

Signed APK: `app/build/outputs/apk/prod/release/app-release.apk`

## Play Store Deployment

See **[DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md)** for step-by-step instructions:
1. Prepare branding (icon, name, description)
2. Setup signing configuration
3. Security hardening (HTTPS, auth tokens, privacy policy)
4. Play Store listing (screenshots, content rating, etc.)
5. Testing (internal, open beta, production rollout)

### Quick Build & Deploy
```bash
./build.sh
```

## Configuration

Edit [mobile/android/app/src/main/java/com/finaccai/mobile/Config.kt](android/app/src/main/java/com/finaccai/mobile/Config.kt):

```kotlin
const val BACKEND_URL_DEV = "http://10.0.2.2:5000"
const val BACKEND_URL_STAGING = "https://staging.finaccai.example.com"
const val BACKEND_URL_PROD = "https://api.finaccai.example.com"
const val PRIVACY_POLICY_URL = "https://finaccai.example.com/privacy"
```

## Permissions

- `INTERNET`: Backend communication
- `BIND_ACCESSIBILITY_SERVICE`: Accessibility analyzer

Accessibility service requires user permission via system settings (no code changes needed).

## Testing Checklist

- [ ] Backend running and reachable
- [ ] Sample analysis succeeds (dashboard → "Run sample analysis")
- [ ] Backend health check works ("Analyze current app")
- [ ] AccessibilityService enable button opens system settings
- [ ] Service can be enabled and shows "Service active" chip
- [ ] Live app captures work (open another app, observe in logs/reports)
- [ ] Report history persists across app restarts
- [ ] Reports open via Custom Tabs
- [ ] Privacy policy link works
- [ ] Release APK installs and runs on device

## Architecture Highlights

### Dashboard (MainActivity)
- Persists settings to SharedPreferences via `Prefs` helper
- Loads history on init; adapter auto-updates
- Supports both sample and live analyses
- Health-checks backend before enabling live mode
- Opens reports via Custom Tabs for seamless UX

### Accessibility Service (FinAccAIAccessibilityService)
- Listens for foreground app changes via `TYPE_WINDOW_STATE_CHANGED`
- Serializes the view hierarchy to JSON matching the backend contract
- Posts to `/api/mobile/analyze` with user settings (AI toggle, screenshot)
- Respects user preferences (backend URL, AI enabled)
- Runs on background coroutines to avoid ANR

### Reporting
- Reports saved to app history (max 20 entries)
- Metadata: app name, package, timestamp, issue count
- Opens via `CustomTabsIntent` (Chrome, Edge) or fallback intent
- Can be shared via Android share sheet

## Next Steps

- [ ] Finalize app icon and branding
- [ ] Deploy HTTPS backend (with optional auth token)
- [ ] Publish privacy policy
- [ ] Complete Play Store listing
- [ ] Beta test with internal testers
- [ ] Prepare for production release

---

**Questions?** See [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md) or check the [API contract](./README.md#api-contract-api-mobile-analyze) for backend integration.


## API contract: `/api/mobile/analyze`
- **Method**: POST (JSON)
- **Fields**:
  - `app_name` (string, optional): Display name shown in the report.
  - `package_name` (string, optional): Package id; used to tag the run.
  - `level` ("AA" | "AAA", optional): WCAG level (default AAA).
  - `html` (string, optional): Raw HTML if you already render the screen as HTML.
  - `view_hierarchy_json` (object, optional): Android view tree. Keys read: `className`, `text`, `contentDescription`, `resourceId`, `role`, `clickable`, `focusable`, `enabled`, `children`.
  - `view_hierarchy_xml` (string, optional): UIAutomator XML dump alternative.
  - `screenshot` (string, optional): Base64-encoded PNG/JPEG of the screen (used in the report and vision model).
- **Response** (success):
```json
{
  "success": true,
  "data": {
    "issues": {...},
    "ai_ml_results": {...},
    "ai_ml_enabled": true,
    "totalIssues": 7,
    "reportPath": "mobile_accessibility_report_20260125_123456.html",
    "reportUrl": "/reports/mobile_accessibility_report_20260125_123456.html",
    "appName": "Target App",
    "packageName": "com.example.app"
  }
}
```

### Example payload (JSON tree)
```json
{
  "app_name": "Sample Banking App",
  "package_name": "com.example.bank",
  "level": "AAA",
  "view_hierarchy_json": {
    "className": "android.widget.LinearLayout",
    "children": [
      {
        "className": "android.widget.ImageView",
        "contentDescription": "App logo",
        "resourceId": "com.example.bank:id/logo"
      },
      {
        "className": "android.widget.EditText",
        "resourceId": "com.example.bank:id/username",
        "text": "",
        "hint": "Username"
      },
      {
        "className": "android.widget.Button",
        "text": "Continue",
        "clickable": true
      }
    ]
  },
  "screenshot": "<base64 PNG>"
}
```

## Android AccessibilityService (native)
- File: `android/FinAccAIAccessibilityService.kt`
- Responsibilities:
  1. Listen for `TYPE_WINDOW_CONTENT_CHANGED` / `TYPE_WINDOW_STATE_CHANGED` events.
  2. Walk the `AccessibilityNodeInfo` tree into JSON matching the contract above.
  3. Capture a screenshot via MediaProjection (optional but recommended for AI vision) and Base64-encode it.
  4. POST to `/api/mobile/analyze` on your FinAccAI server.

## React Native / Flutter shell
- Use the native service to collect data, then bridge to JS/Dart to show the returned report URL in a `WebView`.
- Minimal flow (React Native):
  1. Start the native accessibility service (prompt the user for permission).
  2. On demand, call a native module that returns `{ viewHierarchyJson, screenshot }`.
  3. Use `fetch` to POST to the API.
  4. Render the `reportUrl` in a `WebView` or open it in Custom Tabs.

## Google Play readiness checklist
- Request the **AccessibilityService** permission with a clear justification (policy requirement).
- Request **MEDIA_PROJECTION** for screenshots (optional) with user consent.
- Add a privacy policy describing data collection (view trees and screenshots are processed locally/through your server).
- Offer an offline-only mode (rule-based) when the AI models are not available.
- Include an opt-out toggle for screenshot capture.

## Testing
- Local: start the Flask server, send a sample payload (above) with `curl`.
- Device: deploy the native service, open a target app, and trigger a POST. Confirm you get `reportUrl` and the HTML appears in `reports/`.

## Next steps
- Wire the Kotlin service into your Android app shell.
- Optional: add on-device lightweight checks (e.g., use the JSON tree for quick client-side hints before sending to the server).
