from functools import wraps
from flask import redirect, url_for, flash
from flask_login import current_user

def role_required(*roles):
    def wrapper(func):
        @wraps(func)
        def decorated(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for('login'))
            if current_user.role not in roles:
                flash('Access denied — insufficient permissions.', 'danger')
                return redirect(url_for('dashboard'))
            return func(*args, **kwargs)
        return decorated
    return wrapper

def log_action(db, AuditLog, user, action, ip='unknown'):
    entry = AuditLog(user=user, action=action, ip=ip)
    db.session.add(entry)
    db.session.commit()
