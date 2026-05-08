from flask import Flask, request, jsonify, send_file, send_from_directory, render_template
import os
import sys
import yaml
import base64
from datetime import datetime
from dotenv import load_dotenv

sys.path.insert(0, os.path.join(os.getcwd(), 'src'))

from clients.jira_client import JiraClient
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML

load_dotenv()

app = Flask(__name__)

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

@app.route('/')
def portal():
    return render_template('portal.html')

@app.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory(os.path.join(os.getcwd(), 'static'), filename)

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok", "timestamp": datetime.now().isoformat()})

@app.route('/api/projects', methods=['GET'])
def get_projects():
    try:
        config = load_config()
        config_projects = config.get('projects', {})
        result = {}
        for k, v in config_projects.items():
            result[k] = {
                'name': v.get('name', k),
                'description': v.get('description', ''),
                'responsable': v.get('responsable', ''),
                'source': 'config'
            }
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/jira-projects', methods=['GET'])
def get_jira_projects():
    try:
        jira = get_jira_client()
        jira_conn = jira.jira
        projects = jira_conn.projects()
        result = {}
        for p in projects:
            key = getattr(p, 'key', '')
            name = getattr(p, 'name', key)
            result[key] = {
                'name': name,
                'description': getattr(p, 'description', ''),
                'lead': str(getattr(p, 'lead', '')),
                'source': 'jira'
            }
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/generate', methods=['POST'])
def generate_report():
    try:
        data = request.json
        project_key = data.get('project_key')
        report_type = data.get('report_type', 'standard')
        
        if not project_key:
            return jsonify({"error": "project_key required"}), 400
        
        config = load_config()
        config_projects = config.get('projects', {})
        
        if project_key not in config_projects:
            jira = get_jira_client()
            jira_conn = jira.jira
            jira_projects = jira_conn.projects()
            matched = None
            for p in jira_projects:
                if getattr(p, 'key', '') == project_key:
                    matched = p
                    break
            if not matched:
                return jsonify({"error": f"Project {project_key} not found in Jira"}), 404
            project_config = {
                'jira_key': project_key,
                'name': getattr(matched, 'name', project_key),
                'description': getattr(matched, 'description', ''),
                'responsable': str(getattr(matched, 'lead', '')),
            }
        else:
            jira = get_jira_client()
            jira_conn = jira.jira
            project_config = config_projects[project_key]
        
        report_types = {
            'standard': generate_standard_report,
            'kickoff': generate_kickoff_report,
            'final': generate_final_report,
        }
        
        if report_type not in report_types:
            return jsonify({"error": f"Invalid report_type: {report_type}. Choose from: {list(report_types.keys())}"}), 400
        
        return report_types[report_type](jira_conn, project_key, project_config)
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

def generate_standard_report(jira_conn, project_key, project_config):
    all_issues = jira_conn.search_issues(f'project = "{project_key}" ORDER BY created ASC', maxResults=500)
    
    # Group by Epic
    epics_data = {}
    for issue in all_issues:
        fields = getattr(issue, 'fields', None)
        if not fields:
            continue
        epic_name = "Sin Hito"
        
        # Try customfield_10014 (Classic projects)
        epic_link = getattr(fields, 'customfield_10014', None)
        # Try parent field (Team-managed projects)
        parent = getattr(fields, 'parent', None)
        
        if epic_link:
            try:
                epic_obj = jira_conn.issue(epic_link.key) if hasattr(epic_link, 'key') else None
                if epic_obj:
                    epic_name = getattr(epic_obj.fields, 'summary', epic_link.key)
                else:
                    epic_name = getattr(epic_link, 'key', 'Sin Hito')
            except:
                epic_name = str(epic_link)
        elif parent:
            try:
                # In Jira Cloud, 'parent' usually has the summary directly or can be fetched
                if isinstance(parent, dict):
                    epic_name = parent.get('fields', {}).get('summary', 'Sin Hito')
                else:
                    epic_name = getattr(parent.fields, 'summary', 'Sin Hito')
            except:
                epic_name = "Sin Hito"
        
        if epic_name not in epics_data:
            epics_data[epic_name] = {'all': [], 'done': [], 'in_progress': [], 'todo': [], 'blocked': []}
        
        status = getattr(fields, 'status', None)
        status_name = getattr(status, 'name', '') if status else ''
        
        issue_data = {
            'key': issue.key,
            'summary': fields.summary,
            'status': status_name,
            'priority': getattr(fields, 'priority', None),
            'epic': epic_name,
            'updated': str(getattr(fields, 'updated', ''))[:10],
            'duedate': getattr(fields, 'duedate', None),
        }
        
        epics_data[epic_name]['all'].append(issue_data)
        if status_name in ['Done', 'Completado', 'Cerrado']:
            epics_data[epic_name]['done'].append(issue_data)
        elif status_name in ['In Progress', 'En Progreso', 'En curso']:
            epics_data[epic_name]['in_progress'].append(issue_data)
        elif status_name in ['Blocked', 'Bloqueado']:
            epics_data[epic_name]['blocked'].append(issue_data)
        else:
            epics_data[epic_name]['todo'].append(issue_data)
    
    # Calculate epic progress
    epics = []
    total_done = 0
    total_all = 0
    for epic_name, issues in epics_data.items():
        done_count = len(issues['done'])
        total_count = len(issues['all'])
        pct = round((done_count / total_count * 100) if total_count > 0 else 0, 1)
        epics.append({
            'name': epic_name,
            'percentage': pct,
            'done_count': done_count,
            'total_count': total_count,
        })
        total_done += done_count
        total_all += total_count
    
    global_percentage = round((total_done / total_all * 100) if total_all > 0 else 0, 1)
    
    # Completed items
    completed_items = []
    for epic_name, issues in epics_data.items():
        for item in issues['done']:
            completed_items.append({
                'key': item['key'],
                'epic': item['epic'],
                'summary': item['summary'],
                'date': item['updated'],
            })
    completed_items.sort(key=lambda x: x['date'], reverse=True)
    
    # In progress items
    in_progress_items = []
    for epic_name, issues in epics_data.items():
        for item in issues['in_progress']:
            in_progress_items.append({
                'key': item['key'],
                'epic': item['epic'],
                'summary': item['summary'],
                'status': item['status'],
            })
    
    # Overdue items (active + past due date)
    today = datetime.now()
    overdue_items = []
    for epic_name, issues in epics_data.items():
        for item in issues['all']:
            if item['status'] in ['Done', 'Completado', 'Cerrado']:
                continue
            if item['duedate']:
                try:
                    due = datetime.strptime(item['duedate'], "%Y-%m-%d")
                    if due < today:
                        overdue_items.append(item)
                except:
                    pass
            priority = item.get('priority')
            priority_name = getattr(priority, 'name', '') if priority else ''
            if priority_name in ['High', 'Highest', 'Critical'] and item['status'] not in ['Done', 'Completado', 'Cerrado']:
                if item not in overdue_items:
                    overdue_items.append(item)
    
    # Blocked items
    blocked_items = []
    for epic_name, issues in epics_data.items():
        for item in issues['blocked']:
            comment = "Sin comentarios recientes."
            try:
                jira_issue = jira_conn.issue(item['key'])
                comments = jira_issue.fields.comment.comments
                if comments:
                    latest = comments[-1]
                    comment = str(latest.body)[:100]
            except:
                pass
            blocked_items.append({
                'key': item['key'],
                'epic': item['epic'],
                'summary': item['summary'],
                'comment': comment,
            })
    
    # Planned items (To Do)
    planned_items = []
    for epic_name, issues in epics_data.items():
        for item in issues['todo']:
            priority = item.get('priority')
            priority_name = getattr(priority, 'name', 'Medium') if priority else 'Medium'
            planned_items.append({
                'key': item['key'],
                'epic': item['epic'],
                'summary': item['summary'],
                'priority': priority_name,
            })
    
    # Evidence items (attachments from completed issues)
    evidence_items = []
    for epic_name, issues in epics_data.items():
        for item in issues['done'][:20]:
            try:
                jira_issue = jira_conn.issue(item['key'])
                attachments = getattr(jira_issue.fields, 'attachment', [])
                for att in attachments:
                    filename = getattr(att, 'filename', '').lower()
                    if any(filename.endswith(ext) for ext in ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp']):
                        ext = filename.split('.')[-1]
                        if ext == 'jpg':
                            ext = 'jpeg'
                        try:
                            content = att.get()
                            if content:
                                image_b64 = base64.b64encode(content).decode()
                                evidence_items.append({
                                    'key': item['key'],
                                    'summary': item['summary'],
                                    'image_b64': image_b64,
                                    'ext': ext,
                                })
                                if len(evidence_items) >= 8:
                                    break
                        except:
                            pass
                if len(evidence_items) >= 8:
                    break
            except:
                pass
        if len(evidence_items) >= 8:
            break
    
    # AI Diagnosis
    ai_diagnosis = generate_ai_diagnosis(epics_data, global_percentage, overdue_items, blocked_items)
    
    context = {
        'project_key': project_key,
        'project_name': project_config.get('name', project_key),
        'report_date': datetime.now().strftime('%Y-%m-%d'),
        'responsable': project_config.get('responsable', ''),
        'global_percentage': global_percentage,
        'ai_diagnosis': ai_diagnosis,
        'epics': sorted(epics, key=lambda x: x['percentage']),
        'completed_items': completed_items[:15],
        'in_progress_items': in_progress_items[:10],
        'overdue_items': overdue_items[:10],
        'blocked_items': blocked_items[:15],
        'planned_items': planned_items[:10],
        'evidence_items': evidence_items[:8],
    }
    
    env = Environment(loader=FileSystemLoader(TEMPLATES_DIR))
    template = env.get_template('standard.html')
    html_content = template.render(context)
    
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    pdf_filename = f"SafetyMind_{project_key}_{datetime.now().strftime('%Y-%m-%d')}_Standard.pdf"
    pdf_path = os.path.join(REPORTS_DIR, pdf_filename)
    
    HTML(string=html_content, base_url=TEMPLATES_DIR).write_pdf(pdf_path)
    
    return jsonify({
        "status": "success",
        "message": f"Standard report generated for {project_key}",
        "filename": pdf_filename,
        "job_id": f"job_{timestamp}",
        "engine": "html"
    })

def generate_ai_diagnosis(epics_data, global_pct, overdue, blocked):
    low_epics = [e['name'] for e_name, issues in epics_data.items() 
                 for e in [{'name': e_name, 'pct': round(len(issues['done'])/len(issues['all'])*100, 1) if issues['all'] else 0}]
                 if e['pct'] < 30]
    high_epics = [e['name'] for e_name, issues in epics_data.items()
                  for e in [{'name': e_name, 'pct': round(len(issues['done'])/len(issues['all'])*100, 1) if issues['all'] else 0}]
                  if e['pct'] >= 50]
    
    diag = f"La situación actual del proyecto SafetyMind presenta un avance general del {global_pct}%. "
    if low_epics:
        diag += f"Los hitos con menor progreso son: {', '.join(low_epics[:3])}. "
    if high_epics:
        diag += f"Los hitos con mayor avance son: {', '.join(high_epics[:3])}. "
    if overdue:
        diag += f"Existen {len(overdue)} items vencidos que requieren atención inmediata. "
    if blocked:
        diag += f"Se reportan {len(blocked)} bloqueos activos. "
    diag += "Se recomienda revisar la asignación de recursos y priorizar los hitos críticos para mantener el cronograma."
    
    return diag

def generate_kickoff_report(jira_conn, project_key, project_config):
    all_issues = jira_conn.search_issues(f'project = "{project_key}" ORDER BY created ASC', maxResults=500)
    
    epics_data = {}
    for issue in all_issues:
        fields = getattr(issue, 'fields', None)
        if not fields:
            continue
        epic_name = "Sin Hito"
        epic_link = getattr(fields, 'customfield_10014', None)
        parent = getattr(fields, 'parent', None)
        if epic_link:
            try:
                epic_obj = jira_conn.issue(epic_link.key) if hasattr(epic_link, 'key') else None
                if epic_obj:
                    epic_name = getattr(epic_obj.fields, 'summary', epic_link.key)
                else:
                    epic_name = getattr(epic_link, 'key', 'Sin Hito')
            except:
                epic_name = str(epic_link)
        elif parent:
            try:
                if isinstance(parent, dict):
                    epic_name = parent.get('fields', {}).get('summary', 'Sin Hito')
                else:
                    epic_name = getattr(parent.fields, 'summary', 'Sin Hito')
            except:
                epic_name = "Sin Hito"
        if epic_name not in epics_data:
            epics_data[epic_name] = {'all': [], 'done': []}
        epics_data[epic_name]['all'].append({'key': issue.key, 'summary': fields.summary})
        status = getattr(fields, 'status', None)
        status_name = getattr(status, 'name', '') if status else ''
        if status_name in ['Done', 'Completado', 'Cerrado']:
            epics_data[epic_name]['done'].append({'key': issue.key, 'summary': fields.summary})
    
    epics = []
    for epic_name, issues in epics_data.items():
        done_count = len(issues['done'])
        total_count = len(issues['all'])
        pct = round((done_count / total_count * 100) if total_count > 0 else 0, 1)
        epics.append({'name': epic_name, 'percentage': pct, 'done_count': done_count, 'total_count': total_count})
    
    context = {
        'project_key': project_key,
        'project_name': project_config.get('name', project_key),
        'report_date': datetime.now().strftime('%Y-%m-%d'),
        'responsable': project_config.get('responsable', ''),
        'total_issues': len(all_issues),
        'epics': sorted(epics, key=lambda x: x['percentage']),
        'scope': project_config.get('scope', ''),
        'team_members': project_config.get('team', []),
        'risks': project_config.get('risks', []),
    }
    
    env = Environment(loader=FileSystemLoader(TEMPLATES_DIR))
    template = env.get_template('kickoff.html')
    html_content = template.render(context)
    
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    pdf_filename = f"SafetyMind_{project_key}_{datetime.now().strftime('%Y-%m-%d')}_Kickoff.pdf"
    pdf_path = os.path.join(REPORTS_DIR, pdf_filename)
    
    HTML(string=html_content, base_url=TEMPLATES_DIR).write_pdf(pdf_path)
    
    return jsonify({
        "status": "success",
        "message": f"Kickoff report generated for {project_key}",
        "filename": pdf_filename,
        "job_id": f"job_{timestamp}",
        "engine": "html",
        "report_type": "kickoff"
    })

def generate_final_report(jira_conn, project_key, project_config):
    all_issues = jira_conn.search_issues(f'project = "{project_key}" ORDER BY created ASC', maxResults=500)
    
    epics_data = {}
    for issue in all_issues:
        fields = getattr(issue, 'fields', None)
        if not fields:
            continue
        epic_name = "Sin Hito"
        epic_link = getattr(fields, 'customfield_10014', None)
        parent = getattr(fields, 'parent', None)
        if epic_link:
            try:
                epic_obj = jira_conn.issue(epic_link.key) if hasattr(epic_link, 'key') else None
                if epic_obj:
                    epic_name = getattr(epic_obj.fields, 'summary', epic_link.key)
                else:
                    epic_name = getattr(epic_link, 'key', 'Sin Hito')
            except:
                epic_name = str(epic_link)
        elif parent:
            try:
                if isinstance(parent, dict):
                    epic_name = parent.get('fields', {}).get('summary', 'Sin Hito')
                else:
                    epic_name = getattr(parent.fields, 'summary', 'Sin Hito')
            except:
                epic_name = "Sin Hito"
        if epic_name not in epics_data:
            epics_data[epic_name] = {'all': [], 'done': [], 'in_progress': [], 'blocked': []}
        status = getattr(fields, 'status', None)
        status_name = getattr(status, 'name', '') if status else ''
        issue_data = {'key': issue.key, 'summary': fields.summary, 'status': status_name}
        epics_data[epic_name]['all'].append(issue_data)
        if status_name in ['Done', 'Completado', 'Cerrado']:
            epics_data[epic_name]['done'].append(issue_data)
        elif status_name in ['In Progress', 'En Progreso', 'En curso']:
            epics_data[epic_name]['in_progress'].append(issue_data)
        elif status_name in ['Blocked', 'Bloqueado']:
            epics_data[epic_name]['blocked'].append(issue_data)
    
    total_done = sum(len(i['done']) for i in epics_data.values())
    total_all = sum(len(i['all']) for i in epics_data.values())
    global_pct = round((total_done / total_all * 100) if total_all > 0 else 0, 1)
    
    epics = []
    for epic_name, issues in epics_data.items():
        done_count = len(issues['done'])
        total_count = len(issues['all'])
        pct = round((done_count / total_count * 100) if total_count > 0 else 0, 1)
        epics.append({'name': epic_name, 'percentage': pct, 'done_count': done_count, 'total_count': total_count})
    
    context = {
        'project_key': project_key,
        'project_name': project_config.get('name', project_key),
        'report_date': datetime.now().strftime('%Y-%m-%d'),
        'responsable': project_config.get('responsable', ''),
        'global_percentage': global_pct,
        'total_issues': total_all,
        'completed_count': total_done,
        'epics': sorted(epics, key=lambda x: x['percentage']),
        'lessons_learned': project_config.get('lessons_learned', []),
    }
    
    env = Environment(loader=FileSystemLoader(TEMPLATES_DIR))
    template = env.get_template('final.html')
    html_content = template.render(context)
    
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    pdf_filename = f"SafetyMind_{project_key}_{datetime.now().strftime('%Y-%m-%d')}_Final.pdf"
    pdf_path = os.path.join(REPORTS_DIR, pdf_filename)
    
    HTML(string=html_content, base_url=TEMPLATES_DIR).write_pdf(pdf_path)
    
    return jsonify({
        "status": "success",
        "message": f"Final report generated for {project_key}",
        "filename": pdf_filename,
        "job_id": f"job_{timestamp}",
        "engine": "html",
        "report_type": "final"
    })

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
