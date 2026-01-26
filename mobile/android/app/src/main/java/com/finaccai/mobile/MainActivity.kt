package com.finaccai.mobile

import android.content.Intent
import android.net.Uri
import android.os.Bundle
import android.provider.Settings
import android.view.View
import androidx.appcompat.app.AppCompatActivity
import androidx.browser.customtabs.CustomTabsIntent
import androidx.recyclerview.widget.LinearLayoutManager
import com.finaccai.mobile.databinding.ActivityMainBinding
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.Job
import kotlinx.coroutines.launch
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.RequestBody.Companion.toRequestBody
import org.json.JSONObject

class MainActivity : AppCompatActivity() {
    private lateinit var binding: ActivityMainBinding
    private val client = OkHttpClient.Builder()
        .addInterceptor(AuthInterceptor())
        .connectTimeout(30, java.util.concurrent.TimeUnit.SECONDS)
        .readTimeout(Config.ANALYZE_TIMEOUT_SECONDS, java.util.concurrent.TimeUnit.SECONDS)
        .writeTimeout(30, java.util.concurrent.TimeUnit.SECONDS)
        .build()
    private val scope = CoroutineScope(Dispatchers.IO + Job())
    private val adapter = ReportAdapter { openReport(it.reportUrl) }
    private var lastReportUrl: String? = null

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityMainBinding.inflate(layoutInflater)
        setContentView(binding.root)

        setupUi()
        hydrateFromPrefs()
        refreshHistory()
        refreshServiceState()
    }

    private fun setupUi() {
        binding.reportList.layoutManager = LinearLayoutManager(this)
        binding.reportList.adapter = adapter

        binding.analyzeButton.setOnClickListener { runSampleAnalysis() }
        binding.analyzeLiveButton.setOnClickListener { showLiveHint() }
        binding.openReportButton.setOnClickListener { lastReportUrl?.let { openReport(it) } }
        binding.accessibilityButton.setOnClickListener { openAccessibilitySettings() }

        binding.aiSwitch.setOnCheckedChangeListener { _, isChecked ->
            Prefs.setAiEnabled(this, isChecked)
            binding.aiChip.text = if (isChecked) "AI/ML on" else "AI/ML off"
        }
        binding.screenshotSwitch.setOnCheckedChangeListener { _, isChecked ->
            Prefs.setScreenshotEnabled(this, isChecked)
        }
    }

    private fun hydrateFromPrefs() {
        val savedUrl = Prefs.getBaseUrl(this, DEFAULT_BASE_URL)
        binding.baseUrlInput.setText(savedUrl)
        binding.aiSwitch.isChecked = Prefs.isAiEnabled(this)
        binding.screenshotSwitch.isChecked = Prefs.isScreenshotEnabled(this)
        binding.aiChip.text = if (binding.aiSwitch.isChecked) "AI/ML on" else "AI/ML off"
    }

    private fun runSampleAnalysis() {
        val baseUrl = binding.baseUrlInput.text.toString().trim().removeSuffix("/")
        if (baseUrl.isEmpty()) {
            binding.statusText.text = "Set analyzer URL first"
            return
        }
        Prefs.setBaseUrl(this, baseUrl)
        setStatus(getString(R.string.status_running))

        val sampleTree = JSONObject().apply {
            put("className", "android.widget.LinearLayout")
            put("children", listOf(
                JSONObject().apply {
                    put("className", "android.widget.ImageView")
                    put("contentDescription", "Bank logo")
                    put("resourceId", "com.example.bank:id/logo")
                },
                JSONObject().apply {
                    put("className", "android.widget.EditText")
                    put("resourceId", "com.example.bank:id/username")
                    put("text", "")
                },
                JSONObject().apply {
                    put("className", "android.widget.Button")
                    put("text", "Continue")
                    put("clickable", true)
                }
            ))
        }

        val payload = JSONObject().apply {
            put("app_name", "Sample Banking App")
            put("package_name", "com.example.bank")
            put("level", "AAA")
            put("view_hierarchy_json", sampleTree)
            if (!binding.aiSwitch.isChecked) {
                put("ai_requested", false)
            }
        }

        scope.launch {
            try {
                val body = payload.toString().toRequestBody("application/json".toMediaType())
                val request = Request.Builder()
                    .url("$baseUrl/api/mobile/analyze")
                    .post(body)
                    .build()
                client.newCall(request).execute().use { response ->
                    val text = response.body?.string() ?: ""
                    if (response.isSuccessful) {
                        val json = JSONObject(text)
                        val data = json.optJSONObject("data")
                        val reportPath = data?.optString("reportUrl")
                        val issues = data?.optInt("totalIssues", -1)?.takeIf { it >= 0 }
                        val resolvedUrl = if (reportPath?.startsWith("http") == true) reportPath else "$baseUrl$reportPath"
                        lastReportUrl = resolvedUrl

                        val entry = ReportEntry(
                            title = data?.optString("appName") ?: "Sample Banking App",
                            packageName = data?.optString("packageName") ?: "com.example.bank",
                            reportUrl = resolvedUrl ?: "",
                            timestamp = System.currentTimeMillis(),
                            issues = issues
                        )
                        Prefs.addHistoryEntry(this@MainActivity, entry)

                        runOnUiThread {
                            refreshHistory()
                            setStatus(getString(R.string.status_done))
                        }
                    } else {
                        runOnUiThread { setStatus("${getString(R.string.status_error)} (${response.code})") }
                    }
                }
            } catch (t: Throwable) {
                runOnUiThread { setStatus("${getString(R.string.status_error)}: ${t.message}") }
            }
        }
    }

    private fun showLiveHint() {
        val baseUrl = binding.baseUrlInput.text.toString().trim().removeSuffix("/")
        if (baseUrl.isEmpty()) {
            setStatus("Set analyzer URL first")
            return
        }
        Prefs.setBaseUrl(this, baseUrl)
        setStatus("Checking analyzer health…")
        scope.launch {
            try {
                val request = Request.Builder().url("$baseUrl/api/health").get().build()
                client.newCall(request).execute().use { response ->
                    runOnUiThread {
                        if (response.isSuccessful) {
                            setStatus("Live analysis ready. Enable the accessibility service and open your target app.")
                        } else {
                            setStatus("Analyzer unreachable (${response.code})")
                        }
                    }
                }
            } catch (t: Throwable) {
                runOnUiThread { setStatus("Analyzer unreachable: ${t.message}") }
            }
        }
    }

    private fun refreshHistory() {
        val history = Prefs.loadHistory(this)
        adapter.submit(history)
        if (history.isNotEmpty()) {
            val last = history.first()
            lastReportUrl = last.reportUrl
            binding.reportUrlText.text = last.reportUrl
        } else {
            binding.reportUrlText.text = getString(R.string.empty_reports)
        }
    }

    private fun setStatus(text: String) {
        binding.statusText.text = text
    }

    private fun refreshServiceState() {
        val enabled = isAccessibilityServiceEnabled()
        binding.serviceStateChip.text = if (enabled) getString(R.string.service_state_on) else getString(R.string.service_state_off)
        binding.serviceStateChip.chipBackgroundColor =
            resources.getColorStateList(if (enabled) R.color.md_theme_accent else R.color.md_theme_primary_dark, theme)
    }

    private fun isAccessibilityServiceEnabled(): Boolean {
        val expected = ComponentName(this, FinAccAIAccessibilityService::class.java).flattenToString()
        val enabled = Settings.Secure.getString(contentResolver, Settings.Secure.ENABLED_ACCESSIBILITY_SERVICES) ?: return false
        return enabled.split(":").any { it.equals(expected, ignoreCase = true) }
    }

    private fun openReport(url: String) {
        if (url.isBlank()) return
        try {
            val customTabsIntent = CustomTabsIntent.Builder().build()
            customTabsIntent.launchUrl(this, Uri.parse(url))
        } catch (t: Throwable) {
            startActivity(Intent(Intent.ACTION_VIEW, Uri.parse(url)))
        }
    }

    private fun openAccessibilitySettings() {
        startActivity(Intent(Settings.ACTION_ACCESSIBILITY_SETTINGS))
    }

    companion object {
        private const val DEFAULT_BASE_URL = "http://10.0.2.2:5000"
    }
}
