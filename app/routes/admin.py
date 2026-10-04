from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.models import User, DonorProfile, RecipientProfile, Donation, BloodRequest, BloodInventory, AuditLog, db
from app.auth import log_audit, admin_required
from app.forms import StaffRegistrationForm
from datetime import date

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    total_users = User.query.count()
    total_donors = DonorProfile.query.count()
    total_recipients = RecipientProfile.query.count()
    total_staff = User.query.filter_by(role='staff').count()
    total_donations = Donation.query.count()
    total_requests = BloodRequest.query.count()
    available_inventory = db.session.query(db.func.sum(BloodInventory.units_available)).scalar() or 0
    recent_activity = AuditLog.query.order_by(AuditLog.timestamp.desc()).limit(15).all()
    
    return render_template('admin/dashboard.html',
                           total_users=total_users,
                           total_donors=total_donors,
                           total_recipients=total_recipients,
                           total_staff=total_staff,
                           total_donations=total_donations,
                           total_requests=total_requests,
                           available_inventory=available_inventory,
                           recent_activity=recent_activity)

@admin_bp.route('/staff/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create_staff():
    form = StaffRegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data, role='staff')
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        log_audit('CREATE', 'User', user.id, f'Admin {current_user.username} created staff {user.username}')
        flash('Staff account created successfully!', 'success')
        return redirect(url_for('admin.staff'))
    return render_template('admin/create_staff.html', form=form)

@admin_bp.route('/staff')
@login_required
@admin_required
def staff():
    staff_members = User.query.filter_by(role='staff').all()
    return render_template('admin/staff.html', staff_members=staff_members)

@admin_bp.route('/users')
@login_required
@admin_required
def users():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    role = request.args.get('role', '')
    
    query = User.query
    if search:
        query = query.filter(
            db.or_(
                User.username.contains(search),
                User.email.contains(search)
            )
        )
    if role:
        query = query.filter(User.role == role)
    
    users = query.order_by(User.created_at.desc()).paginate(page=page, per_page=20, error_out=False)
    return render_template('admin/users.html', users=users, search=search, role=role)

@admin_bp.route('/audit-logs')
@login_required
@admin_required
def audit_logs():
    page = request.args.get('page', 1, type=int)
    logs = AuditLog.query.order_by(AuditLog.timestamp.desc()).paginate(page=page, per_page=50, error_out=False)
    return render_template('admin/audit_logs.html', logs=logs)

@admin_bp.route('/users/<int:user_id>/toggle-active', methods=['POST'])
@login_required
@admin_required
def toggle_user_active(user_id):
    user = User.query.get_or_404(user_id)
    if user.role.value == 'admin' and user.is_active:
        admin_count = User.query.filter_by(role='admin', is_active=True).count()
        if admin_count <= 1:
            flash('Cannot deactivate the last active admin.', 'danger')
            return redirect(url_for('admin.users'))
    user.is_active = not user.is_active
    db.session.commit()
    log_audit('UPDATE', 'User', user.id, f'Admin {current_user.username} {"activated" if user.is_active else "deactivated"} user {user.username}')
    flash(f'User {"activated" if user.is_active else "deactivated"} successfully.', 'success')
    return redirect(url_for('admin.users'))
