from functools import wraps
from flask import request, redirect, url_for, flash, abort
from flask_login import current_user
from app.models import AuditLog, db

def role_required(*roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash('Please log in to access this page.', 'warning')
                return redirect(url_for('auth.login'))
            if current_user.role.value not in roles:
                flash('You do not have permission to access this page.', 'danger')
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def admin_required(f):
    return role_required('admin')(f)

def staff_required(f):
    return role_required('staff', 'admin')(f)

def donor_required(f):
    return role_required('donor', 'staff', 'admin')(f)

def recipient_required(f):
    return role_required('recipient', 'staff', 'admin')(f)

def log_audit(action, entity_type, entity_id, description):
    if current_user and current_user.is_authenticated:
        log = AuditLog(
            user_id=current_user.id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            description=description,
            ip_address=request.remote_addr
        )
        db.session.add(log)
        try:
            db.session.commit()
        except Exception:
            db.session.rollback()
