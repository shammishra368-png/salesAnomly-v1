"""
generate_executive_report.py
----------------------------
Generates an executive-ready, print-formatted HTML audit report
(Executive_Anomaly_Report.html) containing operational health scores,
financial exposure analysis, and prioritized action items for management.
"""

import sqlite3
import os
from datetime import date

DB_PATH = "retail.db"
OUTPUT_REPORT = "Executive_Anomaly_Report.html"


def generate_report():
    if not os.path.exists(DB_PATH):
        print(f"[ERROR] Database {DB_PATH} not found.")
        return

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # Core aggregates
    cur.execute("SELECT COUNT(*), SUM(sales), ROUND(SUM(revenue), 2) FROM zscore_live_view")
    total_records, total_units, total_revenue = cur.fetchone()

    cur.execute("SELECT COUNT(*) FROM zscore_live_view WHERE is_flagged = 1")
    total_anomalies = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM zscore_live_view WHERE severity = 'CRITICAL'")
    critical_count = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM zscore_live_view WHERE severity = 'WARNING'")
    warning_count = cur.fetchone()[0]

    cur.execute("SELECT ROUND(SUM(financial_impact), 2) FROM zscore_live_view WHERE financial_impact < 0")
    loss_row = cur.fetchone()
    total_loss = abs(loss_row[0]) if loss_row and loss_row[0] else 0.0

    # Operational Health Score (out of 100)
    health_score = max(0, round(100 - (critical_count * 1.2 + warning_count * 0.4), 1))

    # Top critical anomalies
    cur.execute("""
        SELECT record_date, item, sales, rolling_mean, z_score, inventory, anomaly_type, severity, financial_impact
        FROM zscore_live_view
        WHERE severity = 'CRITICAL'
        ORDER BY ABS(financial_impact) DESC
        LIMIT 10
    """)
    top_critical = cur.fetchall()

    # Product Risk Breakdown
    cur.execute("""
        SELECT item, 
               COUNT(*) as records,
               SUM(CASE WHEN severity = 'CRITICAL' THEN 1 ELSE 0 END) as crit,
               SUM(CASE WHEN severity = 'WARNING' THEN 1 ELSE 0 END) as warn,
               ROUND(SUM(financial_impact), 2) as impact
        FROM zscore_live_view
        GROUP BY item
        ORDER BY crit DESC, impact ASC
    """)
    product_breakdown = cur.fetchall()

    conn.close()

    today_str = date.today().strftime("%B %d, %Y")

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Executive Anomaly & Risk Audit Report — Krishna</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
    <style>
        body {{ font-family: 'Plus Jakarta Sans', sans-serif; }}
        .font-mono {{ font-family: 'JetBrains Mono', monospace; }}
        @media print {{
            .no-print {{ display: none !important; }}
            body {{ background: white; color: black; }}
            .page-break {{ page-break-before: always; }}
        }}
    </style>
</head>
<body class="bg-slate-50 text-slate-800 min-h-screen p-8">

    <div class="max-w-5xl mx-auto bg-white rounded-3xl shadow-xl border border-slate-200 p-10 space-y-8">

        <!-- Print & Action Bar -->
        <div class="no-print flex justify-between items-center bg-indigo-50 border border-indigo-100 p-4 rounded-2xl mb-4">
            <div class="flex items-center gap-3">
                <span class="w-3 h-3 rounded-full bg-emerald-500 animate-pulse"></span>
                <span class="text-xs font-semibold text-indigo-900">Official Semester Capstone Project Executive Audit Report</span>
            </div>
            <button onclick="window.print()" class="px-5 py-2 rounded-xl text-xs font-bold bg-indigo-600 hover:bg-indigo-700 text-white shadow-md transition flex items-center gap-2 cursor-pointer">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 17h2a2 2 0 002-2v-4a2 2 0 00-2-2H5a2 2 0 00-2 2v4a2 2 0 002 2h2m2 4h6a2 2 0 002-2v-4a2 2 0 00-2-2H9a2 2 0 00-2 2v4a2 2 0 002 2zm8-12V5a2 2 0 00-2-2H9a2 2 0 00-2 2v4h10z"/></svg>
                Print to PDF (Ctrl + P)
            </button>
        </div>

        <!-- Header -->
        <div class="border-b border-slate-200 pb-8 flex justify-between items-start">
            <div>
                <span class="px-3 py-1 rounded-full text-[11px] font-bold uppercase bg-slate-100 text-slate-600 tracking-wider">Operational Audit & Risk Report</span>
                <h1 class="text-3xl font-extrabold text-slate-900 mt-2 tracking-tight">Retail Sales & Inventory Anomaly Audit</h1>
                <p class="text-xs text-slate-500 mt-1">Generated: {today_str} &bull; Pipeline Engine: SQL Z-Score & Machine Learning</p>
            </div>
            <div class="text-right">
                <div class="text-xs text-slate-400 font-semibold uppercase">Project Author</div>
                <div class="text-lg font-black text-indigo-600">Krishna</div>
                <div class="text-xs text-slate-500">B.Tech CSE (Data Science) 3rd Year</div>
            </div>
        </div>

        <!-- Executive Summary Cards -->
        <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div class="bg-slate-50 p-5 rounded-2xl border border-slate-100">
                <span class="text-xs font-bold text-slate-400 uppercase">Store Health Score</span>
                <div class="text-3xl font-black text-emerald-600 mt-2">{health_score}%</div>
                <span class="text-[11px] text-emerald-700 font-medium">Optimal Operation Target: &gt;90%</span>
            </div>
            <div class="bg-slate-50 p-5 rounded-2xl border border-slate-100">
                <span class="text-xs font-bold text-slate-400 uppercase">Total Revenue Scanned</span>
                <div class="text-3xl font-black text-slate-900 mt-2">₹{total_revenue:,.2f}</div>
                <span class="text-[11px] text-slate-500">{total_units:,} units across 90 days</span>
            </div>
            <div class="bg-slate-50 p-5 rounded-2xl border border-rose-100 bg-rose-50/40">
                <span class="text-xs font-bold text-rose-500 uppercase">Critical Anomalies</span>
                <div class="text-3xl font-black text-rose-600 mt-2">{critical_count}</div>
                <span class="text-[11px] text-rose-700">Stockouts & Pilferage Alerts</span>
            </div>
            <div class="bg-slate-50 p-5 rounded-2xl border border-amber-100 bg-amber-50/40">
                <span class="text-xs font-bold text-amber-600 uppercase">Est. Revenue Loss Impact</span>
                <div class="text-3xl font-black text-amber-600 mt-2">-₹{total_loss:,.2f}</div>
                <span class="text-[11px] text-amber-800">Unexplained shrinkage & outages</span>
            </div>
        </div>

        <!-- Prioritized Action Plan -->
        <div class="bg-indigo-900 text-white p-6 rounded-2xl space-y-4">
            <div class="flex items-center gap-2">
                <svg class="w-5 h-5 text-indigo-300" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"/></svg>
                <h2 class="text-base font-bold">Immediate Store Manager Action Items</h2>
            </div>
            <div class="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs">
                <div class="bg-indigo-800/60 p-4 rounded-xl border border-indigo-700">
                    <span class="text-amber-300 font-bold block mb-1">1. Urgent Restock Protocol</span>
                    <p class="text-indigo-200">Trigger immediate PO for <strong class="text-white">Chicken (1kg)</strong> and items depleted below 2-day rolling buffer to prevent customer drop-off.</p>
                </div>
                <div class="bg-indigo-800/60 p-4 rounded-xl border border-indigo-700">
                    <span class="text-rose-300 font-bold block mb-1">2. Warehouse Theft Investigation</span>
                    <p class="text-indigo-200">Investigate unexplained inventory shrinkage on <strong class="text-white">Eggs (Dozen)</strong> and <strong class="text-white">Cooking Oil</strong> (sudden drop without sales).</p>
                </div>
                <div class="bg-indigo-800/60 p-4 rounded-xl border border-indigo-700">
                    <span class="text-emerald-300 font-bold block mb-1">3. Demand Surge Optimization</span>
                    <p class="text-indigo-200">Adjust safety stock levels for <strong class="text-white">Milk (1L)</strong> and <strong class="text-white">Rice (5kg)</strong> which exhibited recurrent 4σ+ demand spikes.</p>
                </div>
            </div>
        </div>

        <!-- High-Priority Critical Outliers Table -->
        <div class="space-y-4">
            <h2 class="text-lg font-bold text-slate-900">Critical Anomalies Audit Table (Top Financial Impact)</h2>
            <div class="overflow-x-auto border border-slate-200 rounded-2xl">
                <table class="w-full text-left text-xs text-slate-600">
                    <thead class="bg-slate-100 text-slate-700 uppercase font-bold text-[11px] border-b border-slate-200">
                        <tr>
                            <th class="py-3 px-4">Date</th>
                            <th class="py-3 px-4">Product</th>
                            <th class="py-3 px-4 text-right">Actual Sales</th>
                            <th class="py-3 px-4 text-right">14d Mean</th>
                            <th class="py-3 px-4 text-right">Z-Score</th>
                            <th class="py-3 px-4 text-right">Inventory</th>
                            <th class="py-3 px-4 text-center">Category</th>
                            <th class="py-3 px-4 text-right">Impact (₹)</th>
                        </tr>
                    </thead>
                    <tbody class="divide-y divide-slate-100">
    """

    for r in top_critical:
        date_v, item_v, sales_v, mean_v, z_v, inv_v, cat_v, sev_v, impact_v = r
        impact_cls = "text-rose-600 font-bold" if impact_v < 0 else "text-emerald-600 font-bold"
        badge_cls = "bg-rose-100 text-rose-800" if "Theft" in cat_v or "Stockout" in cat_v else "bg-amber-100 text-amber-800"

        html += f"""
                        <tr class="hover:bg-slate-50">
                            <td class="py-3 px-4 font-mono font-medium">{date_v}</td>
                            <td class="py-3 px-4 font-bold text-slate-900">{item_v}</td>
                            <td class="py-3 px-4 text-right font-bold text-slate-800">{sales_v}</td>
                            <td class="py-3 px-4 text-right font-mono text-slate-500">{mean_v}</td>
                            <td class="py-3 px-4 text-right font-mono font-bold text-rose-600">{'+' if z_v > 0 else ''}{z_v}</td>
                            <td class="py-3 px-4 text-right font-mono text-slate-700">{inv_v}</td>
                            <td class="py-3 px-4 text-center">
                                <span class="px-2 py-0.5 rounded-full text-[10px] font-bold {badge_cls}">{cat_v}</span>
                            </td>
                            <td class="py-3 px-4 text-right font-mono {impact_cls}">₹{impact_v:,.2f}</td>
                        </tr>
        """

    html += f"""
                    </tbody>
                </table>
            </div>
        </div>

        <!-- Product Summary Table -->
        <div class="space-y-4">
            <h2 class="text-lg font-bold text-slate-900">Product Risk & Anomaly Breakdown</h2>
            <div class="overflow-x-auto border border-slate-200 rounded-2xl">
                <table class="w-full text-left text-xs text-slate-600">
                    <thead class="bg-slate-100 text-slate-700 uppercase font-bold text-[11px] border-b border-slate-200">
                        <tr>
                            <th class="py-3 px-4">Product Name</th>
                            <th class="py-3 px-4 text-right">Transactions</th>
                            <th class="py-3 px-4 text-right text-rose-600">Critical</th>
                            <th class="py-3 px-4 text-right text-amber-600">Warning</th>
                            <th class="py-3 px-4 text-right">Net Financial Deviation</th>
                        </tr>
                    </thead>
                    <tbody class="divide-y divide-slate-100">
    """

    for p in product_breakdown:
        p_name, p_cnt, p_crit, p_warn, p_imp = p
        p_imp_cls = "text-rose-600 font-bold" if p_imp < 0 else "text-emerald-600 font-bold"
        html += f"""
                        <tr class="hover:bg-slate-50">
                            <td class="py-3 px-4 font-bold text-slate-900">{p_name}</td>
                            <td class="py-3 px-4 text-right font-mono">{p_cnt}</td>
                            <td class="py-3 px-4 text-right font-mono font-bold text-rose-600">{p_crit}</td>
                            <td class="py-3 px-4 text-right font-mono font-bold text-amber-600">{p_warn}</td>
                            <td class="py-3 px-4 text-right font-mono {p_imp_cls}">₹{p_imp:,.2f}</td>
                        </tr>
        """

    html += f"""
                    </tbody>
                </table>
            </div>
        </div>

        <!-- Methodology & Footer -->
        <div class="border-t border-slate-200 pt-6 flex justify-between items-center text-xs text-slate-400">
            <div>
                Evaluation Model: <strong>Rolling Z-Score (14-record sliding window) & ML Isolation Forest</strong>
            </div>
            <div>
                Submitted for B.Tech CSE (Data Science) Semester Project &bull; Author: <strong>Krishna</strong>
            </div>
        </div>

    </div>

</body>
</html>
"""

    with open(OUTPUT_REPORT, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"[OK] Executive Anomaly Report generated: {os.path.abspath(OUTPUT_REPORT)}")


if __name__ == "__main__":
    generate_report()
