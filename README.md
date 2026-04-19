# AI-Enhanced ISO 27001 ISMS Automation Platform
# AI-Enhanced ISO 27001 ISMS Automation Platform

A full-stack web platform built on Kali Linux that automates ISO 27001 information security compliance controls — replacing manual spreadsheets with an intelligent, role-based security governance system.

---

## Features

| Feature | Description | ISO 27001 Clause |
|---|---|---|
| Risk Management | Add, score and classify risks automatically | Clause 6.1.2 |
| AI Risk Scoring | Random Forest ML model predicts risk level with confidence % | Clause 6.1.2 |
| Training Tracker | Assign and track employee security awareness training | Clause 7.2 |
| Policy Manager | Upload and manage security policy documents | Clause 7.5 |
| Security Scan | Real nmap network scans directly from dashboard | Clause 9.1 |
| Audit Log | Every action logged with user, IP and timestamp | Clause 9.1 |
| Analytics | Live charts for risk trends and training completion | Clause 9.1 |
| Email Alerts | Automatic email when CRITICAL risk is detected | Clause 6.1.2 |
| Role Based Access | Admin / Auditor / Employee permission levels | Clause 9.1 |

---

## Tech Stack

- **Backend** — Python, Flask, SQLAlchemy, SQLite
- **AI Module** — scikit-learn Random Forest Classifier
- **Charts** — Matplotlib
- **Security** — Flask-Login, Werkzeug bcrypt password hashing
- **Scanning** — nmap via Python subprocess
- **Deployment** — Gunicorn + Nginx on Kali Linux

---

## ISO 27001 Clauses Automated

- Clause 6.1.2 — Risk Assessment and Treatment
- Clause 7.2 — Competence and Awareness Training
- Clause 7.5 — Documented Information Management
- Clause 9.1 — Monitoring, Measurement and Analysis

---

## Setup

1. Clone the repo
2. Create virtual environment — python3 -m venv venv
3. Activate — source venv/bin/activate
4. Install — pip install flask flask-login flask-sqlalchemy flask-mail matplotlib scikit-learn joblib werkzeug
5. Train AI model — python3 ai_model.py
6. Run — python3 app.py
7. Open browser — http://127.0.0.1:5000

Default login — username: admin / password: Admin@1234

---

## Author

Sawaira — Cybersecurity Student
GitHub: https://github.com/sawaira77

---

## License

MIT License
