# ATLAS Audit Intelligence Platform

Internal audit platform built on the COSO 2013 framework and IIA standards. Uses Flask (Python) with vanilla HTML/CSS/JS to run risk-based data analytics on financial and operational datasets.

Developed as an end-of-year project (PFA) at ENCG Agadir.

## Features

- **Risk Assessment Engine** — 24 risks mapped to COSO 2013 components with IIA-standard fields (Condition, Criteria, Cause, Effect, Recommendation)
- **Benford's Law Analysis** — Chi-square statistical testing on General Ledger data to detect fraudulent manipulation
- **Monte Carlo Simulation** — 10,000-iteration simulation to quantify P10/P50/P90 financial exposure per risk
- **Monetary Unit Sampling (MUS)** — Statistical audit sampling prioritizing high-value transactions
- **Control Gap Analysis** — Semantic keyword-based PDF analysis against a standard control checklist
- **Anomaly Detection** — Duplicate payment detection (7-day window) and threshold avoidance analysis
- **Report Generation** — Full DOCX and PDF audit reports with IIA-standard finding blocks
- **Interactive Dashboard** — Real-time KPI cards, risk heatmap, exposure charts, and sampling explorer

## Tech Stack

| Layer    | Technology                                 |
|----------|--------------------------------------------|
| Backend  | Python 3.10+, Flask, Pandas, NumPy, SciPy  |
| Frontend | HTML5, CSS3, JavaScript, Chart.js          |
| Reports  | python-docx, ReportLab                     |
| Analysis | pdfplumber, openpyxl                       |

## Project Structure

```
ATLASP/
├── backend/
│   ├── app.py              # Flask application factory
│   ├── config.py            # Configuration and environment
│   └── modules/
│       ├── benford.py       # Benford's Law analysis
│       ├── control_gaps.py  # PDF-based control gap detection
│       ├── ingestion.py     # Data loading and parsing
│       ├── monte_carlo.py   # Monte Carlo simulation engine
│       ├── report_gen.py    # DOCX report generator
│       ├── risk_engine.py   # Risk assessment and enrichment
│       └── sampling.py      # Monetary Unit Sampling
├── frontend/
│   ├── css/                 # Stylesheets
│   ├── js/                  # Client-side scripts
│   ├── dashboard.html       # Main analytics dashboard
│   ├── heatmap.html         # Risk heat map
│   ├── register.html        # Risk register
│   ├── exposure.html        # Monte Carlo exposure view
│   ├── anomalies.html       # Benford & anomaly detection
│   ├── gaps.html            # Control gap analysis
│   ├── sampling.html        # MUS sampling explorer
│   ├── report.html          # Report generation
│   ├── settings.html        # API key configuration
│   └── upload.html          # Data upload / demo launcher
├── data/demo/               # Synthetic demo datasets
├── generate_data.py         # Synthetic data generator
├── run.py                   # Application entry point
├── requirements.txt         # Python dependencies
├── Procfile                 # Deployment process file
└── .env.example             # Environment variable template
```

## Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/YOUR_USERNAME/atlas-audit-platform.git
   cd atlas-audit-platform
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate    # Linux/Mac
   venv\Scripts\activate       # Windows
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Generate synthetic demo data**
   ```bash
   python generate_data.py
   ```

5. **Configure environment** (optional)
   ```bash
   cp .env.example .env
   # Edit .env to add GEMINI_API_KEY for AI-enhanced report narratives
   ```

6. **Start the server**
   ```bash
   python run.py
   ```

7. Open `http://localhost:5000` and click **Use Demo Data** to run the full analysis.

## Hosting

This application can be deployed to any platform that supports Python web applications. See the deployment section below for Render (recommended free option).

### Deploy to Render (Free Tier)

1. Push your code to GitHub
2. Go to [render.com](https://render.com) and create a new **Web Service**
3. Connect your GitHub repository
4. Configure:
   - **Build Command**: `pip install -r requirements.txt && python generate_data.py`
   - **Start Command**: `gunicorn run:app --bind 0.0.0.0:$PORT`
5. Add environment variables in the Render dashboard:
   - `FLASK_SECRET_KEY` = a random secure string
   - `GEMINI_API_KEY` = your key (optional)
6. Deploy

### Other Hosting Options

- **Railway** — `railway up` with the included Procfile
- **Heroku** — `git push heroku main` with the included Procfile
- **VPS (DigitalOcean, etc.)** — Run with gunicorn behind nginx

## License

This project is developed for academic purposes as part of the ENCG Agadir PFA program.
