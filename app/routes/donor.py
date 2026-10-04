from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from app.models import DonorProfile, Donation, BloodInventory, BloodRequest, Notification, db
from app.auth import log_audit, donor_required, role_required
from datetime import date, datetime

donor_bp = Blueprint('donor', __name__)

@donor_bp.route('/available')
@login_required
def available_donors():
    blood_group = request.args.get('blood_group', '')
    city = request.args.get('city', '')
    
    query = DonorProfile.query.filter_by(
        eligibility_status='Eligible',
        availability_status='Available'
    )
    
    if blood_group:
        query = query.filter(DonorProfile.blood_group == blood_group)
    if city:
        query = query.filter(DonorProfile.city.contains(city))
    
    donors = query.limit(50).all()
    blood_groups = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']
    
    return render_template('donor/available.html', 
                           donors=donors, 
                           blood_groups=blood_groups,
                           selected_blood=blood_group,
                           selected_city=city)

@donor_bp.route('/dashboard')
@login_required
@donor_required
def dashboard():
    if current_user.role.value != 'donor':
        flash('Access denied.', 'danger')
        return redirect(url_for('main.index'))
    
    profile = current_user.donor_profile
    donations = Donation.query.filter_by(donor_id=profile.id).order_by(Donation.donation_date.desc()).limit(10).all()
    total_donations = Donation.query.filter_by(donor_id=profile.id).count()
    notifications = Notification.query.filter_by(user_id=current_user.id).order_by(Notification.created_at.desc()).limit(5).all()
    unread_count = Notification.query.filter_by(user_id=current_user.id, is_read=False).count()
    
    compatible_requests = []
    if profile.availability_status == 'Available' and profile.eligibility_status.value == 'Eligible':
        requests = BloodRequest.query.filter(
            BloodRequest.required_blood_group == profile.blood_group,
            BloodRequest.status.in_(['Pending', 'Searching for Donor', 'Under Review'])
        ).limit(5).all()
        compatible_requests = requests
    
    return render_template('donor/dashboard.html', 
                           profile=profile, 
                           donations=donations, 
                           total_donations=total_donations,
                           notifications=notifications,
                           unread_count=unread_count,
                           compatible_requests=compatible_requests)

@donor_bp.route('/profile', methods=['GET', 'POST'])
@login_required
@donor_required
def profile():
    if current_user.role.value != 'donor':
        flash('Access denied.', 'danger')
        return redirect(url_for('main.index'))
    
    profile = current_user.donor_profile
    if request.method == 'POST':
        profile.full_name = request.form.get('full_name', profile.full_name)
        profile.phone = request.form.get('phone', profile.phone)
        profile.address = request.form.get('address', profile.address)
        profile.city = request.form.get('city', profile.city)
        profile.emergency_contact = request.form.get('emergency_contact', profile.emergency_contact)
        profile.weight = float(request.form.get('weight', profile.weight or 0))
        profile.height = float(request.form.get('height', profile.height or 0)) if request.form.get('height') else profile.height
        profile.availability_status = request.form.get('availability_status', profile.availability_status)
        db.session.commit()
        log_audit('UPDATE', 'DonorProfile', profile.id, f'Donor {current_user.username} updated profile')
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('donor.profile'))
    return render_template('donor/profile.html', profile=profile)

@donor_bp.route('/donations')
@login_required
@donor_required
def donations():
    if current_user.role.value != 'donor':
        flash('Access denied.', 'danger')
        return redirect(url_for('main.index'))
    
    profile = current_user.donor_profile
    donations = Donation.query.filter_by(donor_id=profile.id).order_by(Donation.donation_date.desc()).all()
    return render_template('donor/donations.html', donations=donations)

@donor_bp.route('/notifications')
@login_required
@donor_required
def notifications():
    if current_user.role.value != 'donor':
        flash('Access denied.', 'danger')
        return redirect(url_for('main.index'))
    
    notifications = Notification.query.filter_by(user_id=current_user.id).order_by(Notification.created_at.desc()).all()
    for n in notifications:
        n.is_read = True
    db.session.commit()
    return render_template('donor/notifications.html', notifications=notifications)
