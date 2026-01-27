package com.finaccai.mobile

import android.accessibilityservice.AccessibilityService
import android.accessibilityservice.AccessibilityServiceInfo
import android.util.Log
import android.view.accessibility.AccessibilityEvent
import android.view.accessibility.AccessibilityNodeInfo
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.Job
import kotlinx.coroutines.launch
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.RequestBody.Companion.toRequestBody
import org.json.JSONArray
import org.json.JSONObject

class FinAccAIAccessibilityService : AccessibilityService() {
    private val client = OkHttpClient.Builder()
        .addInterceptor(AuthInterceptor())
        .connectTimeout(30, java.util.concurrent.TimeUnit.SECONDS)
        .readTimeout(60, java.util.concurrent.TimeUnit.SECONDS)
        .writeTimeout(30, java.util.concurrent.TimeUnit.SECONDS)
        .build()
    private val scope = CoroutineScope(Dispatchers.IO + Job())
    private var baseUrl: String = DEFAULT_BASE_URL

    override fun onServiceConnected() {
        super.onServiceConnected()
        baseUrl = Prefs.getBaseUrl(applicationContext, DEFAULT_BASE_URL)
        serviceInfo = AccessibilityServiceInfo().apply {
            eventTypes = AccessibilityEvent.TYPE_WINDOW_STATE_CHANGED or AccessibilityEvent.TYPE_WINDOW_CONTENT_CHANGED
            feedbackType = AccessibilityServiceInfo.FEEDBACK_VISUAL
            flags = AccessibilityServiceInfo.FLAG_REPORT_VIEW_IDS or AccessibilityServiceInfo.FLAG_RETRIEVE_INTERACTIVE_WINDOWS
        }
        Log.i(TAG, "FinAccAI service connected")
    }

    override fun onAccessibilityEvent(event: AccessibilityEvent?) {
        if (event == null) return
        baseUrl = Prefs.getBaseUrl(applicationContext, DEFAULT_BASE_URL)
        val root = rootInActiveWindow ?: return
        val packageName = event.packageName?.toString() ?: "unknown"
        if (packageName == this.packageName) return

        scope.launch {
            try {
                val aiEnabled = Prefs.isAiEnabled(applicationContext)
                val payload = JSONObject().apply {
                    put("app_name", packageName)
                    put("package_name", packageName)
                    put("level", "AAA")
                    put("view_hierarchy_json", nodeToJson(root))
                    if (!aiEnabled) put("ai_requested", false)
                }
                val body = payload.toString().toRequestBody("application/json".toMediaType())
                val request = Request.Builder()
                    .url("${baseUrl.removeSuffix("/")}/api/mobile/analyze")
                    .post(body)
                    .build()
                client.newCall(request).execute().use { response ->
                    if (!response.isSuccessful) {
                        Log.w(TAG, "FinAccAI call failed: ${response.code}")
                    } else {
                        Log.i(TAG, "FinAccAI report generated for $packageName")
                    }
                }
            } catch (t: Throwable) {
                Log.e(TAG, "Error sending FinAccAI payload", t)
            }
        }
    }

    override fun onInterrupt() {
        // No-op
    }

    private fun nodeToJson(node: AccessibilityNodeInfo?): JSONObject {
        val obj = JSONObject()
        if (node == null) return obj
        obj.put("className", node.className ?: "")
        obj.put("text", node.text ?: "")
        obj.put("contentDescription", node.contentDescription ?: "")
        obj.put("resourceId", node.viewIdResourceName ?: "")
        obj.put("clickable", node.isClickable)
        obj.put("focusable", node.isFocusable)
        obj.put("enabled", node.isEnabled)

        val children = JSONArray()
        for (i in 0 until node.childCount) {
            children.put(nodeToJson(node.getChild(i)))
        }
        obj.put("children", children)
        return obj
    }

    companion object {
        private const val TAG = "FinAccAI-Mobile"
        private const val DEFAULT_BASE_URL = "http://10.0.2.2:5000"
    }
}
