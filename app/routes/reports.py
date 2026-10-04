from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.models import DonorProfile, Donation, BloodRequest, BloodInventory, RecipientProfile, User, db
from app.auth import log_audit, staff_required
from datetime import date, datetime

reports_bp = Blueprint('reports', __name__)

@reports_bp.route('/donations')
@login_required
@staff_required
def donation_report():
    total_donations = Donation.query.count()
    monthly_donations = db.session.query(
        db.func.extract('year', Donation.donation_date).label('year'),
        db.func.extract('month', Donation.donation_date).label('month'),
        db.func.count(Donation.id).label('count')
    ).group_by('year', 'month').order_by('year', 'month').all()
    
    donations_by_blood = db.session.query(
        Donation.blood_group,
        db.func.count(Donation.id).label('count')
    ).group_by(Donation.blood_group).all()
    
    accepted = Donation.query.filter_by(donation_status='Accepted').count()
    rejected = Donation.query.filter_by(donation_status='Rejected').count()
    
    return render_template('reports/donations.html',
                           total_donations=total_donations,
                           monthly_donations=monthly_donations,
                           donations_by_blood=donations_by_blood,
                           accepted=accepted,
                           rejected=rejected)

@reports_bp.route('/requests')
@login_required
@staff_required
def request_report():
    total_requests = BloodRequest.query.count()
    pending = BloodRequest.query.filter_by(status='Pending').count()
    fulfilled = BloodRequest.query.filter_by(status='Fulfilled').count()
    critical = BloodRequest.query.filter_by(urgency='Critical').count()
    
    requests_by_blood = db.session.query(
        BloodRequest.required_blood_group,
        db.func.count(BloodRequest.id).label('count')
    ).group_by(BloodRequest.required_blood_group).all()
    
    return render_template('reports/requests.html',
                           total_requests=total_requests,
                           pending=pending,
                           fulfilled=fulfilled,
                           critical=critical,
                           requests_by_blood=requests_by_blood)

@reports_bp.route('/donors')
@login_required
@staff_required
def donor_report():
    total_donors = DonorProfile.query.count()
    eligible = DonorProfile.query.filter_by(eligibility_status='Eligible').count()
    pending = DonorProfile.query.filter_by(eligibility_status='Pending Medical Review').count()
    deferred = DonorProfile.query.filter_by(eligibility_status='Temporarily Deferred').count()
    
    donors_by_blood = db.session.query(
        DonorProfile.blood_group,
        db.func.count(DonorProfile.id).label('count')
    ).group_by(DonorProfile.blood_group).all()
    
    donors_by_city = db.session.query(
        DonorProfile.city,
        db.func.count(DonorProfile.id).label('count')
    ).group_by(DonorProfile.city).all()
    
    return render_template('reports/donors.html',
                           total_donors=total_donors,
                           eligible=eligible,
                           pending=pending,
                           deferred=deferred,
                           donors_by_blood=donors_by_blood,
                           donors_by_city=donors_by_city)
