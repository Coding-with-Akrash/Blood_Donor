from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.models import RecipientProfile, BloodRequest, BloodInventory, Notification, db
from app.auth import log_audit, recipient_required
from app.forms import BloodRequestForm
from datetime import date

recipient_bp = Blueprint('recipient', __name__)

@recipient_bp.route('/dashboard')
@login_required
@recipient_required
def dashboard():
    if current_user.role.value != 'recipient':
        flash('Access denied.', 'danger')
        return redirect(url_for('main.index'))
    
    profile = current_user.recipient_profile
    requests = BloodRequest.query.filter_by(recipient_id=profile.id).order_by(BloodRequest.created_at.desc()).all()
    notifications = Notification.query.filter_by(user_id=current_user.id).order_by(Notification.created_at.desc()).limit(5).all()
    unread_count = Notification.query.filter_by(user_id=current_user.id, is_read=False).count()
    
    return render_template('recipient/dashboard.html', 
                           profile=profile, 
                           requests=requests,
                           notifications=notifications,
                           unread_count=unread_count)

@recipient_bp.route('/profile', methods=['GET', 'POST'])
@login_required
@recipient_required
def profile():
    if current_user.role.value != 'recipient':
        flash('Access denied.', 'danger')
        return redirect(url_for('main.index'))
    
    profile = current_user.recipient_profile
    if request.method == 'POST':
        profile.full_name = request.form.get('full_name', profile.full_name)
        profile.phone = request.form.get('phone', profile.phone)
        profile.city = request.form.get('city', profile.city)
        profile.hospital = request.form.get('hospital', profile.hospital)
        profile.emergency_contact = request.form.get('emergency_contact', profile.emergency_contact)
        db.session.commit()
        log_audit('UPDATE', 'RecipientProfile', profile.id, f'Recipient {current_user.username} updated profile')
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('recipient.profile'))
    return render_template('recipient/profile.html', profile=profile)

@recipient_bp.route('/request-blood', methods=['GET', 'POST'])
@login_required
@recipient_required
def request_blood():
    if current_user.role.value != 'recipient':
        flash('Access denied.', 'danger')
        return redirect(url_for('main.index'))
    
    form = BloodRequestForm()
    if form.validate_on_submit():
        profile = current_user.recipient_profile
        blood_request = BloodRequest(
            recipient_id=profile.id,
            required_blood_group=form.required_blood_group.data,
            units_required=form.units_required.data,
            hospital=form.hospital.data,
            city=form.city.data,
            required_date=form.required_date.data,
            urgency=form.urgency.data,
            notes=form.notes.data
        )
        db.session.add(blood_request)
        db.session.commit()
        log_audit('CREATE', 'BloodRequest', blood_request.id, f'Recipient {current_user.username} created blood request')
        flash('Blood request submitted successfully!', 'success')
        return redirect(url_for('recipient.dashboard'))
    return render_template('recipient/request_blood.html', form=form)

@recipient_bp.route('/requests')
@login_required
@recipient_required
def requests():
    if current_user.role.value != 'recipient':
        flash('Access denied.', 'danger')
        return redirect(url_for('main.index'))
    
    profile = current_user.recipient_profile
    requests = BloodRequest.query.filter_by(recipient_id=profile.id).order_by(BloodRequest.created_at.desc()).all()
    return render_template('recipient/requests.html', requests=requests)
