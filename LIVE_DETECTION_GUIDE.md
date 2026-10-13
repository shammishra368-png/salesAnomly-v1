# 🚀 Retail Sales & Inventory Live Detection Project
> **Capstone Project — B.Tech CSE (Data Science) 3rd Year**  
> **Student Author:** Krishna  
> **Dual Engine:** SQL Windowed Z-Score (14-Day Rolling) + Scikit-Learn Isolation Forest Outlier Detector + Real-Time WebSocket Streaming

---

## 📌 Project Overview (प्रोजेक्ट का परिचय)

यह प्रोजेक्ट **Retail Sales & Warehouse Inventory** में होने वाली किसी भी असामान्य गतिविधि (Anomaly / Fraud / Operational Failure) को **Real-Time (लाइव)** पकड़ने (Detect) करने के लिए बनाया गया एक संपूर्ण **End-to-End Live Detection System** है।

इसमें दो इंजन एक साथ काम करते हैं:
1. **SQL Windowed Statistical Engine (Z-Score View):** 14-दिनों के रोलिंग मीन (&mu;) और स्टैंडर्ड डेविएशन (&sigma;) के आधार पर गणितीय Z-स्कोर निकालता है।
2. **Machine Learning Outlier Engine (Isolation Forest):** Multi-dimensional फीचर्स (Sales, Inventory, Velocity, Revenue) पर ट्रेंड अनसुपरवाइज्ड मॉडल जो आउटलायर्स को अलग करता है।
3. **Real-Time Streaming & WebSocket Server:** हर नए पॉइंट-ऑफ-सेल (POS) ट्रांजेक्शन को प्रोसेस करता है और लाइव ब्राउज़र डैशबोर्ड पर मिलीसेकंड्स में भेजता है।
4. **Interactive Live Dashboard (`dashboard.html`):** लाइव चार्ट्स, ऑडियो अलर्ट्स (Sound Chime), टोस्ट नोटिफिकेशन्स, और वाइवा / डेमो के लिए **Live Anomaly Testing Lab**।

---

## 🏗️ Live Architecture Pipeline

```
[POS Live Feed Generator] (Simulates POS Cash Register Transactions)
           │
           ▼ (Inserts into SQLite in Real-Time)
    [retail.db] ──► [sales_data table]
           │
           ▼ (Evaluates Instantly via Window Functions)
    [zscore_live_view.sql] (SQL 14-Record Rolling Baseline)
    • Rolling Mean (μ) & Rolling StdDev (σ)
    • Parametric Z-Score: Z = (Sales - μ) / σ
    • Severity Classification: CRITICAL vs WARNING vs NORMAL
    • Financial Impact (₹ Gain / Loss)
           │
           ▼
    [live_detection_engine.py] (Dual-Engine Orchestrator)
    • Runs ML Isolation Forest Online Scoring
    • Automatic Logging to logs/anomaly_log.csv
           │
           ▼ (Asynchronous Low-Latency Push via WebSockets)
    [live_detection_server.py] (aiohttp async server @ port 5000)
           │
    ┌──────┴────────────────────────────────────────────────┐
    ▼                                                       ▼
[WebSocket Broadcast: ws://127.0.0.1:5000/ws]       [REST APIs: /api/stats, /api/inject]
    │                                                       │
    ▼                                                       ▼
[dashboard.html (Next-Gen Live UI)]
• 🟢 Live Engine Connected Radar Indicator
• 🔊 Dual-Tone Audio Alert (Urgent Double Beep on Critical)
• 🍞 Floating Toast Notification Cards
• 📈 Real-Time Live Sales & Z-Score Chart (Auto-updating)
• 📦 Live Warehouse Inventory & Shrinkage Trajectory
• 📑 Real-Time Anomaly Audit Table (Pulsing Row Highlights)
• ⚡ Live Stress-Test Lab (Manual Spike / Drop / Shrinkage / Stockout Injections)
```

---

## 📂 Key Files Created & Upgraded

| File Name | Description |
|---|---|
| **`run_live_detection.bat`** | **1-Click Single Launcher** — ऑटोमैटिकली डेटाबेस चेक करता है, सर्वर स्टार्ट करता है और ब्राउज़र में लाइव डैशबोर्ड खोलता है। |
| **`live_detection_server.py`** | **Async Live Server** — aiohttp आधारित वेब व WebSocket सर्वर जो रियल-टाइम ट्रांजैक्शन स्ट्रीम करता है। |
| **`live_detection_engine.py`** | **Core Detection Engine** — SQL Z-Score + ML Isolation Forest ड्यूल डिटेक्शन पाइपलाइन। |
| **`dashboard.html`** | **Interactive Web Dashboard** — अपग्रेडेड लाइव UI, ऑडियो अलर्ट्स, टोस्ट अलर्ट्स, लाइव चार्ट्स और वाइवा लैब। |
| **`build_html_dashboard.py`** | कंपाइलर स्क्रिप्ट जो नवीनतम डेटा के साथ लाइव-कनेक्टेड `dashboard.html` बनाती है। |
| **`retail.db`** | SQLite डेटाबेस जिसमें 90 दिनों का सेल्स व इन्वेंट्री डेटा और `zscore_live_view` मौजूद है। |
| **`logs/anomaly_log.csv`** | लाइव डिटेक्ट हुई सभी विसंगतियों (Critical/Warning) का ऑटोमैटिक ऑडिट लॉग। |

---

## 🚀 How to Run the Project (प्रोजेक्ट कैसे चलाएं)

### तरीका 1: 1-Click Launcher (सबसे आसान तरीका)
प्रोजेक्ट फोल्डर में मौजूद **`run_live_detection.bat`** फाइल पर डबल-क्लिक (Double Click) करें।
1. टर्मिनल में बैकग्राउंड लाइव सर्वर शुरू हो जाएगा।
2. आपका डिफॉल्ट ब्राउज़र अपने आप **`http://127.0.0.1:5000/dashboard.html`** खोल देगा।
3. डैशबोर्ड पर ऊपर **🟢 LIVE FEED ACTIVE** दिखने लगेगा और रियल-टाइम ट्रांजैक्शंस आने लगेंगे!

---

### तरीका 2: कमांड लाइन (PowerShell / Command Prompt)
अगर आप मैन्युअली कमांड से चलाना चाहते हैं:
```powershell
# Live Detection Server स्टार्ट करें:
python live_detection_server.py --port 5000
```
*(अगर पाइथन PATH में नहीं है, तो `%LOCALAPPDATA%\Python\pythoncore-3.14-64\python.exe live_detection_server.py` चलाएं)*

---

## 🎓 Viva & Presentation Demonstration (टीचर्स / एग्जामिनर के सामने कैसे दिखाएं)

जब आप प्रोजेक्ट प्रेजेंट या वाइवा दे रहे हों, तो इन 4 स्टेप्स को दिखाएं:

### 1. Live Feed का प्रदर्शन:
- डैशबोर्ड के टॉप हेडर में **🟢 LIVE FEED ACTIVE** इंडिकेटर दिखाएं।
- दिखाएं कि कैसे हर 1.5 सेकंड में नया ट्रांजेक्शन टेबल में सबसे ऊपर जुड़ रहा है और KPI काउंटर्स (Total Revenue, Health Score, Total Anomalies) रियल-टाइम में अपडेट हो रहे हैं।

### 2. Live Anomaly Injection Lab (Stress Test) का प्रदर्शन:
- हेडर के ठीक नीचे बने **"Live Viva & Stress-Test Lab"** सेक्शन को दिखाएं।
- किसी प्रोडक्ट को सेलेक्ट करें (जैसे `Milk (1L)`) और **`⚡ Spike (+400%)`** बटन पर क्लिक करें।
- **परिणाम तुरंत देखें:**
  - 🔔 तुरंत हाई-पिच अलार्म बीप सुनाई देगा।
  - 🍞 ऊपर दाईं ओर लाल रंग का **CRITICAL Anomaly Toast Notification** स्लाइड होकर आएगा।
  - 📈 Sales Trend Chart पर लाल रंग का आउटलायर पॉइंट दिखेगा (Z-Score > 3.0&sigma;)।
  - 📑 टेबल में सबसे ऊपर नई पंक्ति नीले/बैंगनी ग्लो के साथ इंसर्ट हो जाएगी।
  - 📝 बैकग्राउंड में `logs/anomaly_log.csv` फाइल में यह रिकॉर्ड तुरंत सेव हो जाएगा।

### 3. अन्य 3 प्रकार की विसंगतियों को इंजेक्ट करके दिखाएं:
- **`📉 Drop (0 Sales)`:** सप्लाई चेन रुकावट या POS मशीन खराबी का डिटेक्शन।
- **`🚨 Theft/Shrinkage`:** इन्वेंट्री में बिना बिक्री के 100 यूनिट्स का अचानक कम होना (चोरी / डैमेज डिटेक्शन)।
- **`📦 Stockout`:** स्टॉक 0 होने पर तुरंत अलर्ट ट्रिगर होना।

### 4. Dual Engine (SQL vs Machine Learning Benchmark) टैब:
- ऊपर टैब में **"🤖 ML Benchmark (Isolation Forest)"** पर क्लिक करें।
- एग्जामिनर को समझाएं कि कैसे SQL Z-Score 15ms में रियल-टाइम इन-डेटाबेस कैलकुलेशन करता है, जबकि Scikit-Learn का Isolation Forest मल्टी-फीचर बाउंड्रीज के जरिए नॉन-लिनियर पैटर्न्स को वेरीफाई करता है।

---

## 🧮 Theoretical & Mathematical Model (गणितीय सूत्र)

1. **Z-Score Formulation:**
   $$Z = \frac{X - \mu_{14}}{\sigma_{14}}$$
   - $|Z| \le 2.5$: Normal Operation (~98.8% Confidence)
   - $2.5 < |Z| \le 3.0$: Warning Alert (P-value < 0.01)
   - $|Z| > 3.0$: Critical Anomaly (P-value < 0.003, 3-Sigma Rule)

2. **Variance Expansion in SQL Window View:**
   $$\text{Var}(X) = E[X^2] - (E[X])^2$$
   $$\text{StdDev}(X) = \sqrt{\text{Var}(X)}$$
