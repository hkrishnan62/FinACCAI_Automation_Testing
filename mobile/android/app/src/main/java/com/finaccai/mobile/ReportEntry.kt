package com.finaccai.mobile

data class ReportEntry(
    val title: String,
    val packageName: String,
    val reportUrl: String,
    val timestamp: Long,
    val issues: Int?
)
