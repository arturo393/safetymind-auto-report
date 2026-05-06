from flask import Flask, request, jsonify, send_file
import os
import sys
import yaml
from datetime import datetime
from dotenv import load_dotenv

# Add src to path so we can import modules
sys.path.insert(0, os.path.join(os.getcwd(), 'src'))

from clients.jira_client import JiraClient
from reporting.report_context import ReportContext
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML
import markdown

# Load Env
load_dotenv()

app = Flask(__name__)

# Configuration
TEMPLATES_DIR = os.path.join(os.getcwd(), 'templates')
REPORTS_DIR = os.path.join(os.getcwd(), 'reports')
os.makedirs(REPORTS_DIR, exist_ok=True)

def load_config(config_path="config/projects.yaml"):
    with open(config_path, 'r') as file:
        return yaml.safe_load(file)

def get_jira_client():
    jira_url = os.getenv("JIRA_URL")
    jira_email = os.getenv("JIRA_EMAIL")
    jira_token = os.getenv("JIRA_API_TOKEN")
    client = JiraClient(jira_url, jira_email, jira_token)
    if not client.connect():
        raise Exception("Failed to connect to Jira")
    return client

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok", "timestamp": datetime.now().isoformat()})

@app.route('/api/projects', methods=['GET'])
def get_projects():
    try:
        config = load_config()
        projects = config.get('projects', {})
        result = {k: v.get('name', k) for k, v in projects.items()}
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/generate', methods=['POST'])
def generate_report():
    try:
        data = request.json
        project_key = data.get('project_key')
        report_type = data.get('report_type', 'progress')
        use_ai = data.get('use_ai', False)
        
        if not project_key:
            return jsonify({"error": "project_key required"}), 400
        
        # Load config
        config = load_config()
        if project_key not in config.get('projects', {}):
            return jsonify({"error": f"Project {project_key} not found"}), 404
        
        project_config = config['projects'][project_key]
        
        # Connect to Jira
        jira = get_jira_client()
        
        # Build context
        context_builder = ReportContext(jira, project_config)
        context = context_builder.build(report_type)
        
        # Add AI description if requested
        if use_ai:
            # TODO: Implement AI summary
            context['description'] = "Resumen generado por IA (TODO)"
        
        # Render template
        template_dir = TEMPLATES_DIR
        env = Environment(loader=FileSystemLoader(template_dir))
        template = env.get_template(f"{report_type}.html")
        html_content = template.render(context)
        
        # Generate output filename
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        pdf_filename = f"{project_key}_{report_type}_{timestamp}.pdf"
        pdf_path = os.path.join(REPORTS_DIR, pdf_filename)
        
        # Generate PDF
        HTML(string=html_content).write_pdf(pdf_path)
        
        return jsonify({
            "status": "success",
            "message": f"Report generated for {project_key}",
            "filename": pdf_filename,
            "job_id": f"job_{timestamp}",
            "engine": "html"
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/reports/list', methods=['GET'])
def list_reports():
    try:
        reports = []
        if os.path.exists(REPORTS_DIR):
            for filename in os.listdir(REPORTS_DIR):
                if filename.endswith('.pdf'):
                    file_path = os.path.join(REPORTS_DIR, filename)
                    stat = os.stat(file_path)
                    reports.append({
                        "name": filename,
                        "size": f"{stat.st_size // 1024} KB",
                        "date": datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d")
                    })
        return jsonify(reports)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/reports/download/<filename>', methods=['GET'])
def download_report(filename):
    try:
        file_path = os.path.join(REPORTS_DIR, filename)
        if not os.path.exists(file_path):
            return jsonify({"error": "File not found"}), 404
        return send_file(file_path, as_attachment=True)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
