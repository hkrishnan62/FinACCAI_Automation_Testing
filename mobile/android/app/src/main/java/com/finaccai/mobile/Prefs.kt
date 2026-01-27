package com.finaccai.mobile

import android.content.Context
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import org.json.JSONArray
import org.json.JSONObject

object Prefs {
    private const val FILE = "finaccai_prefs"
    private const val KEY_BASE_URL = "base_url"
    private const val KEY_HISTORY = "report_history"
    private const val KEY_AI = "ai_enabled"
    private const val KEY_SCREENSHOT = "screenshot_enabled"

    fun getBaseUrl(context: Context, default: String): String =
        context.getSharedPreferences(FILE, Context.MODE_PRIVATE)
            .getString(KEY_BASE_URL, default) ?: default

    fun setBaseUrl(context: Context, value: String) {
        context.getSharedPreferences(FILE, Context.MODE_PRIVATE)
            .edit().putString(KEY_BASE_URL, value).apply()
    }

    fun setAiEnabled(context: Context, enabled: Boolean) {
        context.getSharedPreferences(FILE, Context.MODE_PRIVATE)
            .edit().putBoolean(KEY_AI, enabled).apply()
    }

    fun isAiEnabled(context: Context, default: Boolean = true): Boolean =
        context.getSharedPreferences(FILE, Context.MODE_PRIVATE)
            .getBoolean(KEY_AI, default)

    fun setScreenshotEnabled(context: Context, enabled: Boolean) {
        context.getSharedPreferences(FILE, Context.MODE_PRIVATE)
            .edit().putBoolean(KEY_SCREENSHOT, enabled).apply()
    }

    fun isScreenshotEnabled(context: Context, default: Boolean = false): Boolean =
        context.getSharedPreferences(FILE, Context.MODE_PRIVATE)
            .getBoolean(KEY_SCREENSHOT, default)

    suspend fun loadHistory(context: Context): List<ReportEntry> = withContext(Dispatchers.IO) {
        val raw = context.getSharedPreferences(FILE, Context.MODE_PRIVATE)
            .getString(KEY_HISTORY, "[]") ?: "[]"
        val arr = JSONArray(raw)
        val list = mutableListOf<ReportEntry>()
        for (i in 0 until arr.length()) {
            val obj = arr.optJSONObject(i) ?: continue
            list.add(
                ReportEntry(
                    title = obj.optString("title"),
                    packageName = obj.optString("package"),
                    reportUrl = obj.optString("url"),
                    timestamp = obj.optLong("ts"),
                    issues = obj.optInt("issues", -1).takeIf { it >= 0 }
                )
            )
        }
        list
    }

    private suspend fun saveHistory(context: Context, history: List<ReportEntry>) = withContext(Dispatchers.IO) {
        val arr = JSONArray()
        history.forEach { entry ->
            arr.put(
                JSONObject().apply {
                    put("title", entry.title)
                    put("package", entry.packageName)
                    put("url", entry.reportUrl)
                    put("ts", entry.timestamp)
                    entry.issues?.let { put("issues", it) }
                }
            )
        }
        context.getSharedPreferences(FILE, Context.MODE_PRIVATE)
            .edit().putString(KEY_HISTORY, arr.toString()).apply()
    }

    suspend fun addHistoryEntry(context: Context, entry: ReportEntry, limit: Int = 20) {
        val current = loadHistory(context).toMutableList()
        current.add(0, entry)
        val trimmed = current.take(limit)
        saveHistory(context, trimmed)
    }
}
