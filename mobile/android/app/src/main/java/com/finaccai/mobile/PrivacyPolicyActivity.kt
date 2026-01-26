package com.finaccai.mobile

import android.app.Activity
import android.content.Intent
import android.net.Uri
import android.os.Bundle
import android.webkit.WebView
import androidx.appcompat.app.AppCompatActivity
import androidx.browser.customtabs.CustomTabsIntent

class PrivacyPolicyActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_privacy_policy)

        val url = intent.getStringExtra("url") ?: Config.PRIVACY_POLICY_URL
        val method = intent.getStringExtra("method") ?: "custom_tabs" // "webview" or "custom_tabs"

        if (method == "webview") {
            openInWebView(url)
        } else {
            openInCustomTabs(url)
            finish()
        }
    }

    private fun openInWebView(url: String) {
        val webView = findViewById<WebView>(R.id.webview)
        webView.settings.apply {
            javaScriptEnabled = true
            domStorageEnabled = true
        }
        webView.loadUrl(url)
    }

    private fun openInCustomTabs(url: String) {
        try {
            val customTabsIntent = CustomTabsIntent.Builder().build()
            customTabsIntent.launchUrl(this, Uri.parse(url))
        } catch (t: Throwable) {
            startActivity(Intent(Intent.ACTION_VIEW, Uri.parse(url)))
        }
    }

    companion object {
        fun launch(activity: Activity) {
            val intent = Intent(activity, PrivacyPolicyActivity::class.java)
            intent.putExtra("url", Config.PRIVACY_POLICY_URL)
            intent.putExtra("method", "custom_tabs")
            activity.startActivity(intent)
        }
    }
}
