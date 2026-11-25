import os
import uuid
import time
import tempfile
import shutil
import logging
from collections import OrderedDict

from flask import Flask, jsonify, request, send_file, abort
from flask_cors import CORS
from werkzeug.utils import secure_filename
import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import PatternFill, Font
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

from .config import Config
from .modules.ingestion import load_demo_data
from .modules.risk_engine import get_all_risks, enrich_risks
from .modules.monte_carlo import run_simulation
from .modules.benford import analyze_benford, detect_anomalies
from .modules.control_gaps import analyze_controls
from .modules.report_gen import generate_docx_report
from .modules.sampling import run_mus_sampling

# ── Logging ────────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)
logger = logging.getLogger(__name__)

ALLOWED_EXTENSIONS = {'xlsx', 'xls', 'csv', 'pdf'}


# ── TTL LRU Cache ──────────────────────────────────────────────────────────────
class TTLCache:
    """LRU cache with time-to-live expiry. Max 50 sessions, 30-minute TTL."""

    def __init__(self, maxsize: int = 50, ttl: int = 1800):
        self._cache: OrderedDict = OrderedDict()
        self._timestamps: dict = {}
        self.maxsize = maxsize
        self.ttl = ttl

    def get(self, key):
        if key not in self._cache:
            return None
        if time.time() - self._timestamps[key] > self.ttl:
            del self._cache[key]
            del self._timestamps[key]
            return None
        self._cache.move_to_end(key)
        return self._cache[key]

    def set(self, key, value):
        if key in self._cache:
            self._cache.move_to_end(key)
        else:
            if len(self._cache) >= self.maxsize:
                oldest = next(iter(self._cache))
                del self._cache[oldest]
                del self._timestamps[oldest]
        self._cache[key] = value
        self._timestamps[key] = time.time()

    def __contains__(self, key):
        return self.get(key) is not None


analysis_cache = TTLCache(maxsize=50, ttl=1800)


def create_app():
    app = Flask(__name__, static_folder='../frontend')
    app.config.from_object(Config)
    CORS(app)

    # ── Helpers ─────────────────────────────────────────────────────────────

    def allowed_file(filename):
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

    def get_session_data():
        """Return cached analysis or abort 400 — never re-run silently."""
        session_id = request.args.get('session_id')
        if not session_id:
            abort(400, description='session_id is required. Please run analysis first.')
        data = analysis_cache.get(session_id)
        if data is None:
            abort(400, description='Session expired or not found. Please re-run analysis.')
        return data

    def run_full_analysis(data_dir=None):
        if data_dir is None:
            data_dir = app.config['DATA_DIR']

        logger.info("Starting full analysis from: %s", data_dir)
        datasets = load_demo_data(data_dir)
        risks = get_all_risks()
        risks = enrich_risks(risks, datasets)

        mc_results = run_simulation(risks)
        for r in risks:
            sim = mc_results.get(r['risk_id'], {})
            r['min_exposure'] = sim.get('min_exposure', 0)
            r['expected_exposure'] = sim.get('expected_exposure', 0)
            r['max_exposure'] = sim.get('max_exposure', 0)

        gl_df = datasets.get('general_ledger')
        benford = analyze_benford(gl_df) if gl_df is not None else {}
        anoms = detect_anomalies(gl_df) if gl_df is not None else {}

        rules_path = os.path.join(app.config['BASE_DIR'], 'backend', 'data', 'control_rules.json')
        proc_pdf = os.path.join(data_dir, 'procurement_policy.pdf')
        it_pdf = os.path.join(data_dir, 'it_security_policy.pdf')

        gaps_proc = analyze_controls(proc_pdf, "Procurement", rules_path)
        gaps_it = analyze_controls(it_pdf, "IT", rules_path)
        gaps_hr = _compute_hr_gaps_from_risks(risks)

        session_id = str(uuid.uuid4())
        cache_data = {
            "datasets": datasets,
            "risks": risks,
            "mc_results": mc_results,
            "benford": benford,
            "anomalies": anoms,
            "gaps": {"Procurement": gaps_proc, "IT": gaps_it, "HR": gaps_hr}
        }
        analysis_cache.set(session_id, cache_data)
        logger.info("Analysis complete. session_id=%s", session_id)
        return cache_data, session_id

    def _compute_hr_gaps_from_risks(risks):
        """Derive HR gap summary from risk data — no HR PDF needed."""
        hr_risks = [r for r in risks if r.get('department') == 'HR']
        hr_controls = [
            "payroll reconciliation control",
            "ghost employee detection",
            "duplicate payment prevention",
            "termination access revocation",
            "hr-payroll system integration"
        ]
        results = {}
        for ctrl in hr_controls:
            has_none = any(r.get('control_status') == 'None' for r in hr_risks)
            results[ctrl] = 'None' if has_none else 'Weak'
        return {
            "results": results,
            "gaps": [k for k, v in results.items() if v in ('None', 'Weak')],
            "policy_date": None,
            "policy_date_flag": False
        }

    def _compute_coso_coverage(risks):
        """Compute % of risks controlled per COSO component."""
        components = [
            "Control Environment", "Risk Assessment",
            "Control Activities", "Information & Communication", "Monitoring Activities"
        ]
        buckets = {c: [] for c in components}
        for r in risks:
            comp = r.get('coso_component', '')
            if comp in buckets:
                status = r.get('control_status', 'None')
                score = 1.0 if status == 'Strong' else (0.5 if status == 'Weak' else 0.0)
                buckets[comp].append(score)
        result = []
        for comp in components:
            vals = buckets[comp]
            pct = int(sum(vals) / len(vals) * 100) if vals else 0
            result.append({"label": comp, "pct": pct})
        return result

    # ── Frontend routes ──────────────────────────────────────────────────────

    @app.route('/')
    def serve_index():
        return app.send_static_file('upload.html')

    @app.route('/<path:path>')
    def serve_pages(path):
        full = os.path.join(app.static_folder, path)
        if os.path.isfile(full):
            return app.send_static_file(path)
        if os.path.isfile(full + '.html'):
            return app.send_static_file(path + '.html')
        abort(404)

    # ── Error handlers ───────────────────────────────────────────────────────

    @app.errorhandler(400)
    def bad_request(e):
        return jsonify({"error": str(e.description), "redirect": "/upload"}), 400

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"error": "Not found"}), 404

    @app.errorhandler(500)
    def server_error(e):
        logger.exception("Internal server error")
        return jsonify({"error": "Internal server error. Check server logs."}), 500

    # ── API: Analyze ─────────────────────────────────────────────────────────

    @app.route('/api/analyze', methods=['POST'])
    def analyze():
        temp_dir = None
        try:
            body = request.get_json(silent=True, force=True) or {}
            is_demo = body.get('demo', False)

            if not is_demo and request.files:
                temp_dir = tempfile.mkdtemp()
                for f in request.files.getlist('files'):
                    filename = secure_filename(f.filename or '')
                    if filename and allowed_file(filename):
                        f.save(os.path.join(temp_dir, filename))
                _, session_id = run_full_analysis(data_dir=temp_dir)
            else:
                _, session_id = run_full_analysis()

            return jsonify({"status": "success", "session_id": session_id})
        except Exception:
            logger.exception("Analysis failed")
            return jsonify({"status": "error", "message": "Analysis failed. Check server logs."}), 500
        finally:
            if temp_dir and os.path.exists(temp_dir):
                shutil.rmtree(temp_dir, ignore_errors=True)

    # ── API: Dashboard ────────────────────────────────────────────────────────

    @app.route('/api/dashboard', methods=['GET'])
    def dashboard():
        data = get_session_data()
        risks = data['risks']
        mc_results = data['mc_results']
        benford = data['benford']
        gaps = data['gaps']

        max_exposure = sum(r['max_exposure'] for r in mc_results.values())
        critical_count = sum(1 for r in risks if r['risk_level'] == 'Critical')
        high_count = sum(1 for r in risks if r['risk_level'] == 'High')
        fraud_ids = {'R04', 'R05', 'R07', 'R16'}
        fraud_indicators = sum(
            1 for r in risks
            if r['risk_id'] in fraud_ids and r['risk_level'] in ('High', 'Critical')
        )

        total_controls = present_controls = 0
        for cat_data in gaps.values():
            for v in cat_data.get('results', {}).values():
                total_controls += 1
                if v in ('Strong', 'Weak'):
                    present_controls += 1
        coverage = round(present_controls / total_controls * 100, 1) if total_controls else 0

        benford_anoms = 0
        if benford and 'actual_frequencies' in benford and 'expected_frequencies' in benford:
            benford_anoms = sum(
                1 for a, e in zip(benford['actual_frequencies'], benford['expected_frequencies'])
                if abs(a - e) > 2.0
            )

        return jsonify({
            "risks_identified": len(risks),
            "max_exposure": round(max_exposure, 2),
            "control_coverage": coverage,
            "benford_anomalies": benford_anoms,
            "critical_count": critical_count,
            "high_count": high_count,
            "fraud_indicators": fraud_indicators
        })

    @app.route('/api/heatmap', methods=['GET'])
    def heatmap():
        return jsonify(get_session_data()['risks'])

    @app.route('/api/register', methods=['GET'])
    def register():
        return jsonify(get_session_data()['risks'])

    @app.route('/api/exposure', methods=['GET'])
    def exposure():
        data = get_session_data()
        formatted = []
        for r in data['risks']:
            exp = r.get('expected_exposure', 0)
            cv = round((r['max_exposure'] - r['min_exposure']) / exp, 2) if exp > 0 else 0
            formatted.append({
                "risk_id": r['risk_id'], "name": r['name'],
                "category": r['category'], "risk_level": r['risk_level'],
                "min_exposure": r['min_exposure'], "expected_exposure": exp,
                "max_exposure": r['max_exposure'], "cv": cv,
                "likelihood": r['likelihood'], "impact": r['impact']
            })
        return jsonify(formatted)

    @app.route('/api/anomalies', methods=['GET'])
    def anomalies():
        data = get_session_data()
        return jsonify({"benford": data['benford'], "anomalies": data['anomalies']})

    @app.route('/api/gaps', methods=['GET'])
    def gaps():
        data = get_session_data()
        gaps_data = data['gaps']
        risks = data['risks']

        total_controls = present_controls = gaps_count = 0
        matrix = []
        policy_flags = []

        for cat, cat_data in gaps_data.items():
            results = cat_data.get('results', {})
            for ctrl, status in results.items():
                total_controls += 1
                if status in ('Strong', 'Weak'):
                    present_controls += 1
                if status in ('None', 'Weak'):
                    gaps_count += 1
                matrix.append({
                    "category": cat, "control": ctrl,
                    "status": status,
                    "policy_source": f"{cat.lower()}_policy.pdf"
                })
            if cat_data.get('policy_date_flag'):
                policy_flags.append({
                    "file": f"{cat}_policy.pdf",
                    "last_reviewed": cat_data.get('policy_date'),
                    "flag": True
                })

        coso_coverage = _compute_coso_coverage(risks)

        return jsonify({
            "summary": {"tested": total_controls, "present": present_controls, "gaps": gaps_count},
            "matrix": matrix,
            "policy_flags": policy_flags,
            "coso_coverage": coso_coverage
        })

    @app.route('/api/report/preview', methods=['GET'])
    def report_preview():
        data = get_session_data()
        return jsonify({
            "risks": data['risks'],
            "critical_count": sum(1 for r in data['risks'] if r['risk_level'] == 'Critical'),
            "max_exposure": sum(r['max_exposure'] for r in data['risks'])
        })

    @app.route('/api/report/docx', methods=['GET'])
    def report_docx():
        data = get_session_data()
        session_id = request.args.get('session_id')
        try:
            filename = os.path.join(
                app.config['OUTPUTS_DIR'],
                f'Audit_Report_{session_id[:8]}.docx'
            )
            api_key = app.config.get('GEMINI_API_KEY')
            generate_docx_report(data['risks'], filename, api_key)
            return send_file(filename, as_attachment=True)
        except Exception as e:
            logger.exception("DOCX generation failed")
            return jsonify({"error": f"Report generation failed: {e}"}), 500

    @app.route('/api/report/pdf', methods=['GET'])
    def report_pdf():
        data = get_session_data()
        session_id = request.args.get('session_id')
        try:
            filename = os.path.join(
                app.config['OUTPUTS_DIR'],
                f'Audit_Report_{session_id[:8]}.pdf'
            )
            doc = SimpleDocTemplate(filename, pagesize=letter)
            styles = getSampleStyleSheet()
            story = []
            story.append(Paragraph("ATLAS Internal Audit Report", styles['Title']))
            story.append(Paragraph("Meridian Cables Maroc SA — FY 2024", styles['Heading2']))
            story.append(Paragraph("Confidential", styles['Italic']))
            story.append(Spacer(1, 24))
            story.append(Paragraph("Executive Summary", styles['Heading1']))
            criticals = sum(1 for r in data['risks'] if r['risk_level'] == 'Critical')
            story.append(Paragraph(
                f"This audit identified {len(data['risks'])} risks, including {criticals} Critical risks.",
                styles['Normal']
            ))
            story.append(PageBreak())
            story.append(Paragraph("Risk Assessment Results", styles['Heading1']))
            table_data = [["ID", "Name", "Level", "Component"]]
            for r in data['risks']:
                table_data.append([r['risk_id'], r['name'][:40], r['risk_level'], r['coso_component']])
            t = Table(table_data)
            t.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a2f32')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f7f6f2')]),
            ]))
            story.append(t)
            doc.build(story)
            return send_file(filename, as_attachment=True)
        except Exception as e:
            logger.exception("PDF generation failed")
            return jsonify({"error": f"PDF generation failed: {e}"}), 500

    @app.route('/api/register/export', methods=['GET'])
    def register_export():
        data = get_session_data()
        session_id = request.args.get('session_id')
        try:
            filename = os.path.join(
                app.config['OUTPUTS_DIR'],
                f'ATLAS_Risk_Register_{session_id[:8]}.xlsx'
            )
            wb = Workbook()
            ws1 = wb.active
            ws1.title = "Risk Register"
            headers1 = ["ID", "Name", "Category", "COSO Component", "Likelihood",
                        "Impact", "Score", "Level", "Condition", "Criteria"]
            ws1.append(headers1)
            for c in range(1, len(headers1) + 1):
                ws1.cell(row=1, column=c).fill = PatternFill(
                    start_color="1a2f32", end_color="1a2f32", fill_type="solid")
                ws1.cell(row=1, column=c).font = Font(color="FFFFFF", bold=True)
            for r in data['risks']:
                row = [r['risk_id'], r['name'], r['category'], r['coso_component'],
                       r['likelihood'], r['impact'], r['risk_score'], r['risk_level'],
                       r['condition'], r['criteria']]
                ws1.append(row)
                if r['risk_level'] == 'Critical':
                    fill = PatternFill(start_color="FFCCCC", fill_type="solid")
                elif r['risk_level'] == 'High':
                    fill = PatternFill(start_color="FFE5B4", fill_type="solid")
                else:
                    fill = None
                if fill:
                    for col_idx in range(1, len(row) + 1):
                        ws1.cell(row=ws1.max_row, column=col_idx).fill = fill

            ws2 = wb.create_sheet("Monte Carlo Results")
            ws2.append(["ID", "Name", "P10 Min", "P50 Expected", "P90 Max"])
            for r in data['risks']:
                ws2.append([r['risk_id'], r['name'], r['min_exposure'],
                             r['expected_exposure'], r['max_exposure']])

            ws3 = wb.create_sheet("Anomaly Summary")
            ws3.append(["Duplicate Payments", len(data['anomalies'].get('duplicates', []))])
            ws3.append(["Threshold Avoidance", data['anomalies'].get('threshold_avoidance', 0)])

            wb.save(filename)
            return send_file(filename, as_attachment=True)
        except Exception as e:
            logger.exception("Excel export failed")
            return jsonify({"error": f"Export failed: {e}"}), 500

    @app.route('/api/sampling', methods=['GET'])
    def sampling():
        data = get_session_data()
        dataset_name = request.args.get('dataset', 'general_ledger')
        try:
            conf_level = float(request.args.get('confidence_level', 0.95))
            tol_err    = float(request.args.get('tolerable_error',   0.05))
        except ValueError:
            return jsonify({"error": "confidence_level and tolerable_error must be numeric"}), 400

        if not (0 < conf_level < 1):
            return jsonify({"error": "confidence_level must be between 0 and 1 (e.g. 0.95)"}), 400
        if not (0 < tol_err < 1):
            return jsonify({"error": "tolerable_error must be between 0 and 1 (e.g. 0.05)"}), 400

        df = data['datasets'].get(dataset_name)
        if df is None:
            return jsonify({"error": f"Dataset '{dataset_name}' not found"}), 400

        col = 'Amount_MAD' if 'Amount_MAD' in df.columns else df.columns[-1]
        res = run_mus_sampling(df, column_name=col,
                               confidence_level=conf_level, tolerable_error=tol_err)
        if "error" in res:
            return jsonify(res), 400

        res['selected_transactions'] = res['selected_transactions'][:20]
        pop = res['population_value']
        n = res['sample_size']
        res['conclusion'] = (
            f"Based on MUS sampling at {int(conf_level * 100)}% confidence with "
            f"{int(tol_err * 100)}% tolerable error, a sample of {n} transactions "
            f"was selected from a population of MAD {pop:,.2f}. "
            f"Sampling interval: MAD {res['sampling_interval']:,.2f}. "
            f"Results support reliance on this population subject to substantive testing "
            f"of the {n} selected items."
        )
        return jsonify(res)

    @app.route('/api/settings/apikey', methods=['POST'])
    def set_apikey():
        try:
            import dotenv
            req_data = request.json or {}
            key = req_data.get('key', '').strip()
            if not key:
                return jsonify({"status": "error", "message": "API key cannot be empty"}), 400
            env_path = os.path.join(app.config['BASE_DIR'], '.env')
            if not os.path.exists(env_path):
                open(env_path, 'w').close()
            dotenv.set_key(env_path, "GEMINI_API_KEY", key)
            app.config['GEMINI_API_KEY'] = key
            return jsonify({"status": "success"})
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 500

    return app
