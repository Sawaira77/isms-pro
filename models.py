from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id            = db.Column(db.Integer, primary_key=True)
    username      = db.Column(db.String(100), unique=True, nullable=False)
    email         = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    role          = db.Column(db.String(20), default='employee')  # admin / employee / auditor
    created_at    = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Risk(db.Model):
    id          = db.Column(db.Integer, primary_key=True)
    name        = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    likelihood  = db.Column(db.Integer, nullable=False)
    impact      = db.Column(db.Integer, nullable=False)
    score       = db.Column(db.Integer)
    level       = db.Column(db.String(20))   # LOW / MEDIUM / HIGH / CRITICAL
    owner       = db.Column(db.String(100))
    created_by  = db.Column(db.String(100))
    created_at  = db.Column(db.DateTime, default=datetime.utcnow)

class Training(db.Model):
    id           = db.Column(db.Integer, primary_key=True)
    employee     = db.Column(db.String(100), nullable=False)
    topic        = db.Column(db.String(200), nullable=False)
    status       = db.Column(db.String(20), default='Pending')  # Pending / Completed
    due_date     = db.Column(db.String(50))
    completed_at = db.Column(db.DateTime)

class Policy(db.Model):
    id          = db.Column(db.Integer, primary_key=True)
    title       = db.Column(db.String(200), nullable=False)
    filename    = db.Column(db.String(200), nullable=False)
    uploaded_by = db.Column(db.String(100))
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)

class AuditLog(db.Model):
    id        = db.Column(db.Integer, primary_key=True)
    user      = db.Column(db.String(100))
    action    = db.Column(db.String(300))
    ip        = db.Column(db.String(50))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
