package com.finaccai.mobile

import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.TextView
import androidx.recyclerview.widget.RecyclerView
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale

class ReportAdapter(
    private val onClick: (ReportEntry) -> Unit
) : RecyclerView.Adapter<ReportAdapter.ReportViewHolder>() {

    private val items = mutableListOf<ReportEntry>()
    private val df = SimpleDateFormat("MMM dd, HH:mm", Locale.US)

    fun submit(list: List<ReportEntry>) {
        items.clear()
        items.addAll(list)
        notifyDataSetChanged()
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ReportViewHolder {
        val view = LayoutInflater.from(parent.context)
            .inflate(R.layout.item_report, parent, false)
        return ReportViewHolder(view)
    }

    override fun onBindViewHolder(holder: ReportViewHolder, position: Int) {
        val item = items[position]
        holder.bind(item, df)
        holder.itemView.setOnClickListener { onClick(item) }
    }

    override fun getItemCount(): Int = items.size

    class ReportViewHolder(itemView: View) : RecyclerView.ViewHolder(itemView) {
        private val title: TextView = itemView.findViewById(R.id.title)
        private val subtitle: TextView = itemView.findViewById(R.id.subtitle)
        private val meta: TextView = itemView.findViewById(R.id.meta)

        fun bind(entry: ReportEntry, df: SimpleDateFormat) {
            title.text = entry.title.ifBlank { entry.packageName }
            subtitle.text = entry.packageName
            val ts = df.format(Date(entry.timestamp))
            val issues = entry.issues?.let { " | Issues: $it" } ?: ""
            meta.text = "$ts$issues"
        }
    }
}
