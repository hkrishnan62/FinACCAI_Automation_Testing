package com.finaccai.mobile

import android.accessibilityservice.AccessibilityService
import android.accessibilityservice.AccessibilityServiceInfo
import android.graphics.Bitmap
import android.graphics.PixelFormat
import android.media.ImageReader
import android.util.Base64
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
import java.io.ByteArrayOutputStream

class FinAccAIAccessibilityService : AccessibilityService() {
    private val client = OkHttpClient()
    private val scope = CoroutineScope(Dispatchers.IO + Job())

    // TODO: set this to your running FinAccAI backend (e.g., http://10.0.2.2:5000)
    private val apiBaseUrl = "http://localhost:5000"

    override fun onServiceConnected() {
        super.onServiceConnected()
        serviceInfo = AccessibilityServiceInfo().apply {
            eventTypes = AccessibilityEvent.TYPE_WINDOW_STATE_CHANGED or AccessibilityEvent.TYPE_WINDOW_CONTENT_CHANGED
            feedbackType = AccessibilityServiceInfo.FEEDBACK_VISUAL
            flags = AccessibilityServiceInfo.FLAG_REPORT_VIEW_IDS or AccessibilityServiceInfo.FLAG_RETRIEVE_INTERACTIVE_WINDOWS
        }
        Log.i(TAG, "FinAccAI AccessibilityService connected")
    }

    override fun onAccessibilityEvent(event: AccessibilityEvent?) {
        if (event?.packageName == packageName) return // skip our own app
        val root = rootInActiveWindow ?: return

        scope.launch {
            try {
                val payload = JSONObject().apply {
                    put("app_name", event?.packageName ?: "Unknown")
                    put("package_name", event?.packageName ?: "unknown")
                    put("level", "AAA")
                    put("view_hierarchy_json", nodeToJson(root))
                    // Optional screenshot support (requires MediaProjection): put("screenshot", captureScreenBase64())
                }

                val body = payload.toString().toRequestBody("application/json".toMediaType())
                val request = Request.Builder()
                    .url("$apiBaseUrl/api/mobile/analyze")
                    .post(body)
                    .build()

                client.newCall(request).execute().use { response ->
                    if (!response.isSuccessful) {
                        Log.w(TAG, "FinAccAI call failed: ${response.code}")
                    } else {
                        Log.i(TAG, "FinAccAI analysis submitted for ${event?.packageName}")
                    }
                }
            } catch (t: Throwable) {
                Log.e(TAG, "Failed to send FinAccAI payload", t)
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

    // Placeholder: capturing screenshots requires a MediaProjection session set up by your Activity.
    private fun captureScreenBase64(): String? {
        try {
            // Wire this to an ImageReader you manage via MediaProjection in your Activity.
            val reader: ImageReader? = null
            val image = reader?.acquireLatestImage() ?: return null
            val plane = image.planes.first()
            val buffer = plane.buffer
            val width = image.width
            val height = image.height
            val pixelStride = plane.pixelStride
            val rowStride = plane.rowStride
            val rowPadding = rowStride - pixelStride * width

            val bitmap = Bitmap.createBitmap(
                width + rowPadding / pixelStride,
                height,
                Bitmap.Config.ARGB_8888
            )
            bitmap.copyPixelsFromBuffer(buffer)
            image.close()

            val out = ByteArrayOutputStream()
            bitmap.compress(Bitmap.CompressFormat.PNG, 100, out)
            return Base64.encodeToString(out.toByteArray(), Base64.NO_WRAP)
        } catch (t: Throwable) {
            Log.w(TAG, "Screenshot capture failed", t)
        }
        return null
    }

    companion object {
        private const val TAG = "FinAccAI-Mobile"
    }
}
