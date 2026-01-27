package com.finaccai.mobile

object Config {
    // Backend configuration (PRODUCTION)
    const val BACKEND_URL_DEV = "https://reports.finaccai.ai"
    const val BACKEND_URL_STAGING = "https://staging.finaccai.example.com"
    const val BACKEND_URL_PROD = "https://api.finaccai.com"

    // Auth token (set via environment variable or secure storage)
    // NEVER hardcode tokens - use environment secrets in CI/CD
    var AUTH_TOKEN: String? = System.getenv("FINACCAI_AUTH_TOKEN")

    // Feature flags (production-ready)
    const val ENABLE_SCREENSHOT_CAPTURE = true
    const val ENABLE_AI_ANALYSIS = true
    val ENABLE_DEBUG_LOGGING = BuildConfig.DEBUG  // false in release builds

    // Crash reporting & analytics
    val ENABLE_CRASH_REPORTING = !BuildConfig.DEBUG
    val ENABLE_ANALYTICS = !BuildConfig.DEBUG

    // API endpoints
    const val ENDPOINT_ANALYZE = "/api/mobile/analyze"
    const val ENDPOINT_HEALTH = "/api/health"

    // Privacy & legal
    const val PRIVACY_POLICY_URL = "https://finaccai.com/privacy"
    const val TERMS_URL = "https://finaccai.com/terms"

    // Service settings
    const val MAX_REPORT_HISTORY = 20
    const val ANALYZE_TIMEOUT_SECONDS = 60L
    const val NETWORK_CONNECT_TIMEOUT_SECONDS = 30L
    const val NETWORK_READ_TIMEOUT_SECONDS = 60L
    const val NETWORK_WRITE_TIMEOUT_SECONDS = 30L

    // Security
    val ENFORCE_HTTPS_ONLY = !BuildConfig.DEBUG
    const val CERTIFICATE_PINNING_ENABLED = false  // Set to true for production if using pinning

    // Version info (synced with build.gradle)
    const val VERSION_NAME = "1.0.0"
    const val VERSION_CODE = 1

    // Logging
    const val LOG_TAG = "FinAccAI"

    fun getBackendUrl(): String = when {
        BuildConfig.DEBUG -> BACKEND_URL_DEV
        BuildConfig.FLAVOR == "staging" -> BACKEND_URL_STAGING
        else -> BACKEND_URL_PROD
    }

    fun isProduction(): Boolean = !BuildConfig.DEBUG && BuildConfig.FLAVOR == "prod"
    fun isStaging(): Boolean = BuildConfig.FLAVOR == "staging"
    fun isDevelopment(): Boolean = BuildConfig.DEBUG
}
