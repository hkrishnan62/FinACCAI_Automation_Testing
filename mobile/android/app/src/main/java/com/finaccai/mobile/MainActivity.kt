package com.finaccai.mobile

import android.content.ComponentName
import android.content.Intent
import android.net.Uri
import android.os.Bundle
import android.provider.Settings
import android.view.View
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.lifecycleScope
import androidx.recyclerview.widget.LinearLayoutManager
import com.finaccai.mobile.databinding.ActivityMainBinding
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.Job
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
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
    }

    private fun setupUi() {
        binding.reportList.layoutManager = LinearLayoutManager(this)
        binding.reportList.adapter = adapter

        binding.analyzeButton.setOnClickListener { runSampleAnalysis() }
        binding.openReportButton.setOnClickListener { lastReportUrl?.let { openReport(it) } }

        binding.aiSwitch.setOnCheckedChangeListener { _, isChecked ->
            Prefs.setAiEnabled(this, isChecked)
        }
        binding.screenshotSwitch.setOnCheckedChangeListener { _, isChecked ->
            Prefs.setScreenshotEnabled(this, isChecked)
        }
    }

    private fun hydrateFromPrefs() {
        binding.aiSwitch.isChecked = Prefs.isAiEnabled(this)
        binding.screenshotSwitch.isChecked = Prefs.isScreenshotEnabled(this)
    }

    private fun runSampleAnalysis() {
        val baseUrl = Config.getBackendUrl()
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
                    .url(createUrl(baseUrl, "/api/mobile/analyze"))
                    .post(body)
                    .build()
                client.newCall(request).execute().use { response ->
                    val text = response.body?.string() ?: ""
                    if (response.isSuccessful) {
                        val json = JSONObject(text)
                        val data = json.optJSONObject("data")
                        val reportPath = data?.optString("reportUrl")

                        if (reportPath.isNullOrBlank()) {
                            withContext(Dispatchers.Main) {
                                setStatus("Error: Analysis response missing report URL.")
                            }
                            return@use
                        }

                        val issues = data?.optInt("totalIssues", -1)?.takeIf { it >= 0 }
                        val resolvedUrl = createUrl(baseUrl, reportPath)
                        lastReportUrl = resolvedUrl

                        val entry = ReportEntry(
                            title = data?.optString("appName") ?: "Sample Banking App",
                            packageName = data?.optString("packageName") ?: "com.example.bank",
                            reportUrl = resolvedUrl,
                            timestamp = System.currentTimeMillis(),
                            issues = issues
                        )
                        Prefs.addHistoryEntry(this@MainActivity, entry)

                        withContext(Dispatchers.Main) {
                            refreshHistory()
                            setStatus(getString(R.string.status_done))
                        }
                    } else {
                        withContext(Dispatchers.Main) { setStatus("${getString(R.string.status_error)} (${response.code})") }
                    }
                }
            } catch (t: Throwable) {
                withContext(Dispatchers.Main) { setStatus("${getString(R.string.status_error)}: ${t.message}") }
            }
        }
    }

    private fun refreshHistory() {
        lifecycleScope.launch {
            val history = Prefs.loadHistory(this@MainActivity)
            adapter.submitList(history)
            if (history.isNotEmpty()) {
                val last = history.first()
                lastReportUrl = last.reportUrl
                binding.reportUrlText.text = last.reportUrl
            } else {
                binding.reportUrlText.text = getString(R.string.empty_reports)
            }
        }
    }

    private fun setStatus(text: String) {
        binding.statusText.text = text
    }

    private fun openReport(url: String) {
        if (url.isBlank()) {
            setStatus("Cannot open empty report URL.")
            return
        }
        try {
            startActivity(Intent(Intent.ACTION_VIEW, Uri.parse(url)))
        } catch (t: Throwable) {
            setStatus("Error: Could not open report URL.")
        }
    }

    private fun createUrl(base: String, path: String): String {
        return if (path.startsWith("http")) {
            path
        } else {
            "${base.removeSuffix("/")}/${path.removePrefix("/")}"
        }
    }

    companion object {
        private const val DEFAULT_BASE_URL = "https://reports.finaccai.ai"
    }
}
