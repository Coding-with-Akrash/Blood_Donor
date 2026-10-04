from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from app.models import User, DonorProfile, RecipientProfile, Donation, BloodRequest, BloodInventory, Notification, AuditLog, db
from app.auth import log_audit, staff_required
from app.forms import DonationForm
from datetime import date, timedelta

staff_bp = Blueprint('staff', __name__)

@staff_bp.route('/dashboard')
@login_required
@staff_required
def dashboard():
    if current_user.role.value not in ['staff', 'admin']:
        flash('Access denied.', 'danger')
        return redirect(url_for('main.index'))
    
    total_donors = DonorProfile.query.count()
    eligible_donors = DonorProfile.query.filter_by(eligibility_status='Eligible').count()
    pending_donors = DonorProfile.query.filter_by(eligibility_status='Pending Medical Review').count()
    total_donations = Donation.query.count()
    total_requests = BloodRequest.query.count()
    pending_requests = BloodRequest.query.filter_by(status='Pending').count()
    critical_requests = BloodRequest.query.filter_by(urgency='Critical').count()
    available_units = db.session.query(db.func.sum(BloodInventory.units_available)).scalar() or 0
    
    recent_activity = AuditLog.query.order_by(AuditLog.timestamp.desc()).limit(10).all()
    
    return render_template('staff/dashboard.html',
                           total_donors=total_donors,
                           eligible_donors=eligible_donors,
                           pending_donors=pending_donors,
                           total_donations=total_donations,
                           total_requests=total_requests,
                           pending_requests=pending_requests,
                           critical_requests=critical_requests,
                           available_units=available_units,
                           recent_activity=recent_activity)

@staff_bp.route('/donors')
@login_required
@staff_required
def donors():
    if current_user.role.value not in ['staff', 'admin']:
        flash('Access denied.', 'danger')
        return redirect(url_for('main.index'))
    
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    blood_group = request.args.get('blood_group', '')
    city = request.args.get('city', '')
    eligibility = request.args.get('eligibility', '')
    
    query = DonorProfile.query
    
    if search:
        query = query.filter(
            db.or_(
                DonorProfile.full_name.contains(search),
                DonorProfile.phone.contains(search)
            )
        )
    if blood_group:
        query = query.filter(DonorProfile.blood_group == blood_group)
    if city:
        query = query.filter(DonorProfile.city.contains(city))
    if eligibility:
        query = query.filter(DonorProfile.eligibility_status == eligibility)
    
    donors = query.paginate(page=page, per_page=20, error_out=False)
    return render_template('staff/donors.html', donors=donors, search=search, blood_group=blood_group, city=city, eligibility=eligibility)

@staff_bp.route('/donors/<int:donor_id>')
@login_required
@staff_required
def donor_detail(donor_id):
    if current_user.role.value not in ['staff', 'admin']:
        flash('Access denied.', 'danger')
        return redirect(url_for('main.index'))
    
    donor = DonorProfile.query.get_or_404(donor_id)
    donations = Donation.query.filter_by(donor_id=donor.id).order_by(Donation.donation_date.desc()).all()
    return render_template('staff/donor_detail.html', donor=donor, donations=donations)

@staff_bp.route('/donors/<int:donor_id>/update-eligibility', methods=['POST'])
@login_required
@staff_required
def update_donor_eligibility(donor_id):
    if current_user.role.value not in ['staff', 'admin']:
        flash('Access denied.', 'danger')
        return redirect(url_for('main.index'))
    
    donor = DonorProfile.query.get_or_404(donor_id)
    new_status = request.form.get('eligibility_status')
    if new_status:
        donor.eligibility_status = new_status
        db.session.commit()
        log_audit('UPDATE', 'DonorProfile', donor.id, f'Staff {current_user.username} updated eligibility to {new_status}')
        flash(f'Eligibility status updated to {new_status}', 'success')
    return redirect(url_for('staff.donor_detail', donor_id=donor_id))

@staff_bp.route('/donations')
@login_required
@staff_required
def donations():
    if current_user.role.value not in ['staff', 'admin']:
        flash('Access denied.', 'danger')
        return redirect(url_for('main.index'))
    
    page = request.args.get('page', 1, type=int)
    donations = Donation.query.order_by(Donation.donation_date.desc()).paginate(page=page, per_page=20, error_out=False)
    return render_template('staff/donations.html', donations=donations)

@staff_bp.route('/donations/create', methods=['GET', 'POST'])
@login_required
@staff_required
def create_donation():
    if current_user.role.value not in ['staff', 'admin']:
        flash('Access denied.', 'danger')
        return redirect(url_for('main.index'))
    
    form = DonationForm()
    form.donor_id.choices = [(d.id, d.full_name) for d in DonorProfile.query.filter_by(eligibility_status='Eligible').all()]
    
    if form.validate_on_submit():
        donation = Donation(
            donor_id=form.donor_id.data,
            staff_id=current_user.id,
            donation_date=form.donation_date.data,
            blood_group=form.blood_group.data,
            quantity=form.quantity.data,
            collection_location=form.collection_location.data,
            screening_status=form.screening_status.data,
            donation_status=form.donation_status.data,
            component_type=form.component_type.data,
            notes=form.notes.data
        )
        db.session.add(donation)
        db.session.flush()
        
        if form.donation_status.data == 'Available':
            inventory = BloodInventory(
                blood_group=form.blood_group.data,
                component_type=form.component_type.data,
                units_available=form.quantity.data,
                collection_date=form.donation_date.data,
                expiry_date=form.donation_date.data + timedelta(days=42),
                status='Available',
                donation_id=donation.id
            )
            db.session.add(inventory)
        
        db.session.commit()
        log_audit('CREATE', 'Donation', donation.id, f'Staff {current_user.username} created donation record')
        flash('Donation record created successfully!', 'success')
        return redirect(url_for('staff.donations'))
    return render_template('staff/create_donation.html', form=form)

@staff_bp.route('/blood-requests')
@login_required
@staff_required
def blood_requests():
    if current_user.role.value not in ['staff', 'admin']:
        flash('Access denied.', 'danger')
        return redirect(url_for('main.index'))
    
    page = request.args.get('page', 1, type=int)
    status = request.args.get('status', '')
    urgency = request.args.get('urgency', '')
    
    query = BloodRequest.query
    
    if status:
        query = query.filter(BloodRequest.status == status)
    if urgency:
        query = query.filter(BloodRequest.urgency == urgency)
    
    requests = query.order_by(BloodRequest.created_at.desc()).paginate(page=page, per_page=20, error_out=False)
    return render_template('staff/blood_requests.html', requests=requests, status=status, urgency=urgency)

@staff_bp.route('/blood-requests/<int:request_id>')
@login_required
@staff_required
def blood_request_detail(request_id):
    if current_user.role.value not in ['staff', 'admin']:
        flash('Access denied.', 'danger')
        return redirect(url_for('main.index'))
    
    blood_request = BloodRequest.query.get_or_404(request_id)
    return render_template('staff/blood_request_detail.html', request=blood_request)

@staff_bp.route('/blood-requests/<int:request_id>/update-status', methods=['POST'])
@login_required
@staff_required
def update_request_status(request_id):
    if current_user.role.value not in ['staff', 'admin']:
        flash('Access denied.', 'danger')
        return redirect(url_for('main.index'))
    
    blood_request = BloodRequest.query.get_or_404(request_id)
    new_status = request.form.get('status')
    if new_status:
        blood_request.status = new_status
        blood_request.assigned_staff_id = current_user.id
        db.session.commit()
        log_audit('UPDATE', 'BloodRequest', blood_request.id, f'Staff {current_user.username} updated status to {new_status}')
        flash(f'Request status updated to {new_status}', 'success')
    return redirect(url_for('staff.blood_requests'))
