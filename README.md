<!-- ─────────────────────────────────────────────────────────────── -->
<!--                        ATLAS README                            -->
<!-- ─────────────────────────────────────────────────────────────── -->
<a id="readme-top"></a>

<!-- ── BANNER ──────────────────────────────────────────────────── -->
<p align="center">
  <img src="https://capsule-render.vercel.app/api?type=waving&color=0:0d1b2a,50:1b3a4b,100:01696f&height=220&section=header&text=ATLAS&fontSize=80&fontColor=ffffff&fontAlignY=35&desc=Audit%20Intelligence%20Platform&descSize=20&descColor=a8dadc&descAlignY=55&animation=fadeIn" width="100%" alt="ATLAS Banner"/>
</p>

<!-- ── BADGES ─────────────────────────────────────────────────── -->
<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python"/>
  <img src="https://img.shields.io/badge/Flask-2.x-000000?style=for-the-badge&logo=flask&logoColor=white" alt="Flask"/>
  <img src="https://img.shields.io/badge/Pandas-150458?style=for-the-badge&logo=pandas&logoColor=white" alt="Pandas"/>
  <img src="https://img.shields.io/badge/Chart.js-FF6384?style=for-the-badge&logo=chartdotjs&logoColor=white" alt="Chart.js"/>
  <img src="https://img.shields.io/badge/License-Academic-01696f?style=for-the-badge" alt="License"/>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/COSO_2013-Framework-1b3a4b?style=flat-square" alt="COSO"/>
  <img src="https://img.shields.io/badge/IIA-IPPF_Standards-1b3a4b?style=flat-square" alt="IIA"/>
  <img src="https://img.shields.io/badge/ISA_240-Fraud_Auditing-1b3a4b?style=flat-square" alt="ISA 240"/>
  <img src="https://img.shields.io/badge/ISO_31000-Risk_Mgmt-1b3a4b?style=flat-square" alt="ISO 31000"/>
</p>

<br/>

<p align="center">
  <b>A data-driven internal audit platform that maps 24 risks to the COSO 2013 framework,<br/>runs Monte Carlo simulations, detects anomalies with Benford's Law, and generates IIA-standard reports.</b>
</p>

<p align="center">
  <a href="#-features">Features</a> &nbsp;·&nbsp;
  <a href="#-architecture">Architecture</a> &nbsp;·&nbsp;
  <a href="#-quick-start">Quick Start</a> &nbsp;·&nbsp;
  <a href="#-hosting">Hosting</a> &nbsp;·&nbsp;
  <a href="#-tech-stack">Tech Stack</a>
</p>

<br/>

<!-- ── SCREENSHOT ──────────────────────────────────────────────── -->
<!--
<p align="center">
  <img src=".github/screenshots/dashboard.png" width="80%" alt="Dashboard Screenshot" style="border-radius: 10px; box-shadow: 0 4px 20px rgba(0,0,0,0.15);"/>
</p>
-->

---

## 🔍 Features

<table>
<tr>
<td width="50%">

### Risk Assessment
- 24 risks with full **IIA fields** (Condition, Criteria, Cause, Effect, Recommendation)
- Mapped to all 5 **COSO 2013** components
- Dynamic risk enrichment from live dataset analysis
- 5×5 likelihood-impact scoring matrix

</td>
<td width="50%">

### Monte Carlo Simulation
- **10,000 iterations** per risk using seeded RNG
- Normal distribution with 40% standard deviation factor
- P10 / P50 / P90 financial exposure quantification
- Thread-safe `numpy.random.Generator` implementation

</td>
</tr>
<tr>
<td width="50%">

### Benford's Law Analysis
- Chi-square goodness-of-fit test on first-digit distribution
- Statistical significance threshold at **p < 0.05**
- Automatic flagging of manipulated transaction patterns
- Department-level anomaly breakdown

</td>
<td width="50%">

### Anomaly Detection
- **Duplicate payments** — exact match on vendor + amount within 7-day window
- **Threshold avoidance** — transactions clustered below approval limits (MAD 9,100–9,900 / 48,000–49,800)
- Ghost employee detection via HR-Payroll cross-reference

</td>
</tr>
<tr>
<td width="50%">

### Control Gap Analysis
- PDF policy parsing with **pdfplumber**
- Primary + secondary keyword clustering per control
- Strong / Weak / None classification
- Policy review date extraction and staleness flagging

</td>
<td width="50%">

### Report Generation
- **DOCX** — 11-section IIA-standard report with styled tables and finding blocks
- **PDF** — Summary report with risk matrix and color-coded severity
- **Excel** — Full risk register export with Monte Carlo results

</td>
</tr>
</table>

<br/>

### Additional Capabilities

| Feature | Description |
|---|---|
| **MUS Sampling** | Monetary Unit Sampling with configurable confidence level and tolerable error rate |
| **Interactive Dashboard** | KPI cards, risk heatmap, exposure charts, COSO coverage radar |
| **Session Management** | LRU cache with 30-minute TTL — supports concurrent users without a database |
| **Gemini AI Integration** | Optional AI-enhanced narrative sections in DOCX reports |

<p align="right">(<a href="#readme-top">back to top</a>)</p>

---

## 🏗 Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     ATLAS Platform                          │
├──────────────────────┬──────────────────────────────────────┤
│                      │                                      │
│   Frontend (HTML5)   │          Backend (Flask)              │
│                      │                                      │
│  ┌────────────────┐  │  ┌──────────────────────────────┐    │
│  │  Upload Page   │──┼──│  /api/analyze  (POST)        │    │
│  │  Dashboard     │──┼──│  /api/dashboard              │    │
│  │  Heatmap       │──┼──│  /api/heatmap                │    │
│  │  Risk Register │──┼──│  /api/register               │    │
│  │  Exposure View │──┼──│  /api/exposure               │    │
│  │  Anomalies     │──┼──│  /api/anomalies              │    │
│  │  Control Gaps  │──┼──│  /api/gaps                   │    │
│  │  MUS Sampling  │──┼──│  /api/sampling               │    │
│  │  Reports       │──┼──│  /api/report/docx | pdf      │    │
│  └────────────────┘  │  └──────────┬───────────────────┘    │
│                      │             │                        │
│   Chart.js           │  ┌──────────▼───────────────────┐    │
│   Vanilla JS         │  │      Analysis Modules        │    │
│   CSS3               │  │                              │    │
│                      │  │  risk_engine   monte_carlo   │    │
│                      │  │  benford       control_gaps  │    │
│                      │  │  sampling      report_gen    │    │
│                      │  │  ingestion                   │    │
│                      │  └──────────────────────────────┘    │
└──────────────────────┴──────────────────────────────────────┘
```

<p align="right">(<a href="#readme-top">back to top</a>)</p>

---

## 🚀 Quick Start

### Prerequisites

- Python 3.10 or higher
- pip

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/YOUR_USERNAME/ATLASP.git
cd ATLASP

# 2. Create a virtual environment
python -m venv venv
source venv/bin/activate        # Linux / Mac
venv\Scripts\activate           # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Generate synthetic demo data
python generate_data.py

# 5. (Optional) Configure environment
cp .env.example .env
# Edit .env to add GEMINI_API_KEY for AI-enhanced report narratives

# 6. Start the server
python run.py
```

Open **http://localhost:5000** → click **Use Demo Data** → full analysis runs automatically.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

---

## 🌐 Hosting

### Deploy to Render (Recommended — Free Tier)

The repo includes `render.yaml` for one-click deployment.

| Step | Action |
|------|--------|
| 1 | Push code to GitHub |
| 2 | Go to [render.com](https://render.com) → **New** → **Web Service** |
| 3 | Connect your GitHub repository |
| 4 | Render auto-detects `render.yaml` — confirm settings |
| 5 | Add environment variables: `FLASK_SECRET_KEY`, `GEMINI_API_KEY` (optional) |
| 6 | Click **Deploy** |

> **Note:** The free tier sleeps after 15 min of inactivity. First visit after sleep takes ~30s to wake up.

### Alternative Platforms

| Platform | Command | Free Tier |
|----------|---------|-----------|
| **PythonAnywhere** | Upload + configure WSGI | ✅ Always-on |
| **Railway** | `railway up` | ❌ Paid ($5/mo) |
| **Heroku** | `git push heroku main` | ❌ Paid ($5/mo) |
| **VPS** | gunicorn behind nginx | Varies |

> ⚠️ **Vercel and Netlify** are not compatible — they are designed for frontend/serverless apps and cannot run a Flask server process.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

---

## 🧰 Tech Stack

<table>
<tr>
<td align="center" width="110">
<img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/python/python-original.svg" width="48" height="48" alt="Python" />
<br/><b>Python</b>
</td>
<td align="center" width="110">
<img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/flask/flask-original.svg" width="48" height="48" alt="Flask" />
<br/><b>Flask</b>
</td>
<td align="center" width="110">
<img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/pandas/pandas-original.svg" width="48" height="48" alt="Pandas" />
<br/><b>Pandas</b>
</td>
<td align="center" width="110">
<img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/numpy/numpy-original.svg" width="48" height="48" alt="NumPy" />
<br/><b>NumPy</b>
</td>
<td align="center" width="110">
<img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/javascript/javascript-original.svg" width="48" height="48" alt="JavaScript" />
<br/><b>JavaScript</b>
</td>
<td align="center" width="110">
<img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/html5/html5-original.svg" width="48" height="48" alt="HTML5" />
<br/><b>HTML5</b>
</td>
<td align="center" width="110">
<img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/css3/css3-original.svg" width="48" height="48" alt="CSS3" />
<br/><b>CSS3</b>
</td>
</tr>
</table>

| Category | Libraries |
|----------|-----------|
| **Data Analysis** | Pandas, NumPy, SciPy (chi-square test) |
| **PDF Processing** | pdfplumber |
| **Report Generation** | python-docx (DOCX), ReportLab (PDF) |
| **Spreadsheets** | openpyxl |
| **Visualization** | Chart.js |
| **Server** | gunicorn (production), Flask dev server (local) |

<p align="right">(<a href="#readme-top">back to top</a>)</p>

---

## 📁 Project Structure

<details>
<summary><b>Click to expand</b></summary>
<br/>

```
ATLASP/
│
├── backend/
│   ├── __init__.py              # Package init
│   ├── app.py                   # Flask app factory + all API routes
│   ├── config.py                # Configuration (env vars, paths)
│   └── modules/
│       ├── benford.py           # Benford's Law + anomaly detection
│       ├── control_gaps.py      # PDF policy gap analysis
│       ├── ingestion.py         # Dataset loading (Excel, CSV)
│       ├── monte_carlo.py       # Monte Carlo simulation engine
│       ├── report_gen.py        # DOCX report generator (11 sections)
│       ├── risk_engine.py       # 24 risks + dynamic enrichment
│       └── sampling.py          # Monetary Unit Sampling (MUS)
│
├── frontend/
│   ├── css/                     # Stylesheets
│   ├── js/
│   │   └── api.js               # Fetch utility with session management
│   ├── dashboard.html           # Main analytics dashboard
│   ├── heatmap.html             # Risk heat map
│   ├── register.html            # Risk register table
│   ├── exposure.html            # Monte Carlo exposure view
│   ├── anomalies.html           # Benford & anomaly detection
│   ├── gaps.html                # Control gap analysis
│   ├── sampling.html            # MUS sampling explorer
│   ├── report.html              # Report generation page
│   ├── settings.html            # API key configuration
│   └── upload.html              # Data upload / demo launcher
│
├── data/
│   └── demo/                    # Synthetic datasets (generated)
│
├── backend/data/
│   └── control_rules.json       # Control checklist (21 controls)
│
├── generate_data.py             # Synthetic data generator (seeded)
├── run.py                       # Application entry point
├── requirements.txt             # Python dependencies
├── Procfile                     # gunicorn process file
├── render.yaml                  # Render.com deploy config
├── .env.example                 # Environment variable template
└── .gitignore
```

</details>

<p align="right">(<a href="#readme-top">back to top</a>)</p>

---

## 📊 Methodology

<table>
<tr>
<td>

#### Risk Scoring (ISO 31000)
```
Score = Likelihood × Impact

  ≥ 16  →  Critical
 9–15   →  High
 4–8    →  Moderate
 1–3    →  Low
```

</td>
<td>

#### Monte Carlo Parameters
```
Iterations:   10,000
Distribution: Normal
Std Dev:      40% of base cost
Seed:         42 (reproducible)
Output:       P10 / P50 / P90
```

</td>
<td>

#### MUS Defaults
```
Confidence:   95%
Tolerable:    5%
Factor:       3.00 (Poisson)
Selection:    Systematic with
              random start
```

</td>
</tr>
</table>

<p align="right">(<a href="#readme-top">back to top</a>)</p>

---

## 🔐 Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `FLASK_SECRET_KEY` | Recommended | Session signing key. Set a random string in production. |
| `GEMINI_API_KEY` | Optional | Google Gemini API key for AI-enhanced DOCX report narratives. |
| `PORT` | Auto | Set by hosting platform. Defaults to `5000` locally. |

Copy `.env.example` to `.env` and fill in your values.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

---

## 📄 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/analyze` | Run full analysis (demo or uploaded data) |
| `GET` | `/api/dashboard` | Dashboard KPI summary |
| `GET` | `/api/heatmap` | Risk data for heat map |
| `GET` | `/api/register` | Full risk register |
| `GET` | `/api/exposure` | Monte Carlo exposure results |
| `GET` | `/api/anomalies` | Benford + duplicate + threshold data |
| `GET` | `/api/gaps` | Control gap matrix + COSO coverage |
| `GET` | `/api/sampling` | MUS sampling results |
| `GET` | `/api/report/docx` | Download DOCX audit report |
| `GET` | `/api/report/pdf` | Download PDF audit report |
| `GET` | `/api/register/export` | Download Excel risk register |

> All `GET` endpoints require `?session_id=<uuid>` from a prior `/api/analyze` call.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

---

## 📝 License

This project was developed for academic purposes as part of the **PFA program at ENCG Agadir**.

---

<p align="center">
  <img src="https://capsule-render.vercel.app/api?type=waving&color=0:0d1b2a,50:1b3a4b,100:01696f&height=100&section=footer" width="100%" alt="Footer"/>
</p>
