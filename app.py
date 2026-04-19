from flask import Flask, render_template, redirect, url_for, request, flash, session
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from config import Config
from models import db, User, Risk, Training, Policy, AuditLog
from auth import role_required, log_action
import os, datetime, subprocess
from flask import send_from_directory


import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io, base64


import joblib
import numpy as np


from flask_mail import Mail, Message




app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)


mail = Mail(app)

def send_alert_email(subject, body):
    try:
        msg = Message(subject,
                      sender=app.config['MAIL_USERNAME'],
                      recipients=[app.config['MAIL_USERNAME']])
        msg.body = body
        mail.send(msg)
        return True
    except Exception as e:
        print(f"Email error: {e}")
        return False



login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ── Helper ──────────────────────────────────────────
def classify_risk(score):
    if score >= 20: return 'CRITICAL'
    if score >= 12: return 'HIGH'
    if score >= 6:  return 'MEDIUM'
    return 'LOW'

# ── Auth routes ─────────────────────────────────────
@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form['username']).first()
        if user and user.check_password(request.form['password']):
            login_user(user)
            log_action(db, AuditLog, user.username, 'Logged in',
                       request.remote_addr)
            return redirect(url_for('dashboard'))
        flash('Invalid username or password.', 'danger')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    log_action(db, AuditLog, current_user.username, 'Logged out',
               request.remote_addr)
    logout_user()
    return redirect(url_for('login'))

# ── Dashboard ────────────────────────────────────────
@app.route('/dashboard')
@login_required
def dashboard():
    total_risks     = Risk.query.count()
    critical_risks  = Risk.query.filter_by(level='CRITICAL').count()
    total_training  = Training.query.count()
    pending_training = Training.query.filter_by(status='Pending').count()
    total_policies  = Policy.query.count()
    recent_logs     = AuditLog.query.order_by(AuditLog.timestamp.desc()).limit(5).all()
    return render_template('dashboard.html',
        total_risks=total_risks,
        critical_risks=critical_risks,
        total_training=total_training,
        pending_training=pending_training,
        total_policies=total_policies,
        recent_logs=recent_logs)

# ── Risk Management ──────────────────────────────────
@app.route('/risk', methods=['GET', 'POST'])
@login_required
def risk():
    if request.method == 'POST':
        likelihood = int(request.form['likelihood'])
        impact     = int(request.form['impact'])
        score      = likelihood * impact
        r = Risk(
            name=request.form['name'],
            description=request.form.get('description',''),
            likelihood=likelihood,
            impact=impact,
            score=score,
            level=classify_risk(score),
            owner=request.form.get('owner',''),
            created_by=current_user.username)
        db.session.add(r)
        db.session.commit()
        log_action(db, AuditLog, current_user.username,
                   f"Added risk: {r.name} (score {score})", request.remote_addr)
        if r.level == 'CRITICAL':
            send_alert_email(
                subject='CRITICAL Risk Alert: ' + r.name,
                body='ISMS ALERT\n\nRisk: ' + r.name + '\nLevel: CRITICAL\nScore: ' + str(score) + '/25\nAdded by: ' + current_user.username
            )
        flash('Risk added — level: ' + r.level, 'success')
    risks = Risk.query.order_by(Risk.score.desc()).all()
    return render_template('risk.html', risks=risks)

# ── Training ─────────────────────────────────────────
@app.route('/training', methods=['GET', 'POST'])
@login_required
def training():
    if request.method == 'POST':
        t = Training(
            employee=request.form['employee'],
            topic=request.form['topic'],
            due_date=request.form.get('due_date',''),
            status='Pending')
        db.session.add(t)
        db.session.commit()
        log_action(db, AuditLog, current_user.username,
                   f"Added training for {t.employee}", request.remote_addr)
        flash('Training record added.', 'success')
    records = Training.query.order_by(Training.id.desc()).all()
    return render_template('training.html', records=records)

@app.route('/training/complete/<int:tid>')
@login_required
def complete_training(tid):
    t = Training.query.get_or_404(tid)
    t.status = 'Completed'
    t.completed_at = datetime.datetime.utcnow()
    db.session.commit()
    log_action(db, AuditLog, current_user.username,
               f"Marked training complete: {t.topic} for {t.employee}",
               request.remote_addr)
    flash('Marked as completed.', 'success')
    return redirect(url_for('training'))

# ── Policies ─────────────────────────────────────────
@app.route('/policies', methods=['GET', 'POST'])
@login_required
def policies():
    if request.method == 'POST':
        f = request.files.get('file')
        if f and f.filename:
            filename = f.filename
            f.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            p = Policy(
                title=request.form.get('title', filename),
                filename=filename,
                uploaded_by=current_user.username)
            db.session.add(p)
            db.session.commit()
            log_action(db, AuditLog, current_user.username,
                       f"Uploaded policy: {filename}", request.remote_addr)
            flash('Policy uploaded.', 'success')
    docs = Policy.query.order_by(Policy.uploaded_at.desc()).all()
    return render_template('policies.html', docs=docs)

# ── Audit Log ────────────────────────────────────────
@app.route('/auditlog')
@login_required
@role_required('admin', 'auditor')
def auditlog():
    logs = AuditLog.query.order_by(AuditLog.timestamp.desc()).all()
    return render_template('auditlog.html', logs=logs)

# ── Admin panel ──────────────────────────────────────
@app.route('/admin')
@login_required
@role_required('admin')
def admin_panel():
    users = User.query.all()
    return render_template('admin.html', users=users)


@app.route('/uploads/<filename>')
@login_required
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


@app.route('/scan', methods=['GET', 'POST'])
@login_required
def scan():
    result = None
    target = None
    scan_type = None
    if request.method == 'POST':
        target = request.form.get('target', '127.0.0.1')
        scan_type = request.form.get('scan_type', 'basic')

        if scan_type == 'basic':
            cmd = ['nmap', '-F', '--open', target]
        elif scan_type == 'os':
            cmd = ['nmap', '-O', '--open', target]
        elif scan_type == 'ports':
            cmd = ['nmap', '-p', '1-1000', target]
        elif scan_type == 'vuln':
            cmd = ['nmap', '--script', 'vuln', '-F', target]
        else:
            cmd = ['nmap', '-F', target]

        try:
            proc = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            result = proc.stdout or proc.stderr
        except subprocess.TimeoutExpired:
            result = 'Scan timed out after 60 seconds.'
        except FileNotFoundError:
            result = 'nmap not found. Run: sudo apt install nmap'

        log_action(db, AuditLog, current_user.username,
                   f"Ran {scan_type} scan on {target}", request.remote_addr)

    return render_template('scan.html', result=result, target=target, scan_type=scan_type)




@app.route('/graphs')
@login_required
def graphs():
    # Risk level chart data
    levels = ['LOW', 'MEDIUM', 'HIGH', 'CRITICAL']
    colors = ['#16a34a', '#2563eb', '#d97706', '#dc2626']
    counts = [Risk.query.filter_by(level=l).count() for l in levels]

    # Bar chart — risk levels
    fig, ax = plt.subplots(figsize=(7, 3.5))
    fig.patch.set_facecolor('#1e293b')
    ax.set_facecolor('#0f172a')
    bars = ax.bar(levels, counts, color=colors, width=0.5)
    ax.set_title('Risks by Level', color='#94a3b8', fontsize=13, pad=12)
    ax.tick_params(colors='#94a3b8')
    ax.spines[:].set_color('#334155')
    for bar, count in zip(bars, counts):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1,
                str(count), ha='center', color='#f1f5f9', fontsize=11)
    plt.tight_layout()
    buf1 = io.BytesIO()
    plt.savefig(buf1, format='png', facecolor='#1e293b')
    buf1.seek(0)
    chart1 = base64.b64encode(buf1.read()).decode('utf-8')
    plt.close()

    # Training pie chart
    completed = Training.query.filter_by(status='Completed').count()
    pending   = Training.query.filter_by(status='Pending').count()
    fig2, ax2 = plt.subplots(figsize=(5, 3.5))
    fig2.patch.set_facecolor('#1e293b')
    ax2.set_facecolor('#1e293b')
    if completed + pending > 0:
        ax2.pie([completed, pending],
                labels=['Completed', 'Pending'],
                colors=['#16a34a', '#d97706'],
                autopct='%1.0f%%',
                textprops={'color': '#f1f5f9', 'fontsize': 11})
    ax2.set_title('Training Status', color='#94a3b8', fontsize=13, pad=12)
    plt.tight_layout()
    buf2 = io.BytesIO()
    plt.savefig(buf2, format='png', facecolor='#1e293b')
    buf2.seek(0)
    chart2 = base64.b64encode(buf2.read()).decode('utf-8')
    plt.close()

    # Risk score trend (all risks ordered by id)
    all_risks = Risk.query.order_by(Risk.id).all()
    risk_names  = [r.name[:15] for r in all_risks]
    risk_scores = [r.score for r in all_risks]

    fig3, ax3 = plt.subplots(figsize=(7, 3.5))
    fig3.patch.set_facecolor('#1e293b')
    ax3.set_facecolor('#0f172a')
    if risk_scores:
        ax3.plot(risk_names, risk_scores, color='#38bdf8',
                 marker='o', linewidth=2, markersize=6)
        ax3.fill_between(range(len(risk_scores)), risk_scores,
                         alpha=0.15, color='#38bdf8')
        ax3.set_xticks(range(len(risk_names)))
        ax3.set_xticklabels(risk_names, rotation=25, ha='right', fontsize=9)
    ax3.set_title('Risk Score Trend', color='#94a3b8', fontsize=13, pad=12)
    ax3.tick_params(colors='#94a3b8')
    ax3.spines[:].set_color('#334155')
    plt.tight_layout()
    buf3 = io.BytesIO()
    plt.savefig(buf3, format='png', facecolor='#1e293b')
    buf3.seek(0)
    chart3 = base64.b64encode(buf3.read()).decode('utf-8')
    plt.close()

    return render_template('graphs.html',
                           chart1=chart1, chart2=chart2, chart3=chart3,
                           total_risks=Risk.query.count(),
                           critical=Risk.query.filter_by(level='CRITICAL').count(),
                           completed=completed, pending=pending)







# Load AI model once at startup
try:
    ai_model = joblib.load('ai_model.pkl')
except:
    ai_model = None

@app.route('/ai', methods=['GET', 'POST'])
@login_required
def ai_risk():
    prediction   = None
    confidence   = None
    likelihood   = None
    impact       = None
    manual_score = None
    advice       = None

    if request.method == 'POST':
        likelihood   = int(request.form['likelihood'])
        impact       = int(request.form['impact'])
        manual_score = likelihood * impact

        if ai_model:
            pred_arr    = ai_model.predict([[likelihood, impact]])
            proba_arr   = ai_model.predict_proba([[likelihood, impact]])
            prediction  = pred_arr[0]
            confidence  = round(max(proba_arr[0]) * 100, 1)
        else:
            # Fallback if model not loaded
            if manual_score >= 20:   prediction = 'CRITICAL'
            elif manual_score >= 12: prediction = 'HIGH'
            elif manual_score >= 6:  prediction = 'MEDIUM'
            else:                    prediction = 'LOW'
            confidence = 100.0

        advice_map = {
            'CRITICAL': 'Immediate action required. Escalate to senior management. Implement emergency controls now.',
            'HIGH':     'Schedule treatment within 2 weeks. Assign risk owner and define mitigation plan.',
            'MEDIUM':   'Monitor closely. Plan treatment within 30 days. Review monthly.',
            'LOW':      'Accept or monitor. Review quarterly. No immediate action needed.'
        }
        advice = advice_map.get(prediction, '')

        log_action(db, AuditLog, current_user.username,
                   f"AI risk assessment: L={likelihood} I={impact} → {prediction} ({confidence}%)",
                   request.remote_addr)

    return render_template('ai.html',
                           prediction=prediction,
                           confidence=confidence,
                           likelihood=likelihood,
                           impact=impact,
                           manual_score=manual_score,
                           advice=advice)









if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        # Create default admin if none exists
        if not User.query.filter_by(username='admin').first():
            admin = User(username='admin',
                         email='sawairagohar3012@gmail.com',
                         role='admin')
            admin.set_password('Admin@1234')
            db.session.add(admin)
            db.session.commit()
            print('Default admin created — username: admin / password: Admin@1234')
    app.run(debug=True)
