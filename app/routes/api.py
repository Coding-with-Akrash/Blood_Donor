from flask import Blueprint, jsonify, request, abort
from flask_login import login_required, current_user
from app.models import DonorProfile, BloodRequest, Donation, BloodInventory, db
from app.auth import log_audit, staff_required
from app.services.blood_compatibility import BloodCompatibilityService

api_bp = Blueprint('api', __name__)

def role_check(*roles):
    if current_user.role.value not in roles:
        abort(403)

@api_bp.route('/donors', methods=['GET'])
@login_required
def get_donors():
    role_check('staff', 'admin', 'donor', 'recipient')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    blood_group = request.args.get('blood_group')
    city = request.args.get('city')
    
    query = DonorProfile.query.filter_by(eligibility_status='Eligible', availability_status='Available')
    if blood_group:
        query = query.filter(DonorProfile.blood_group == blood_group)
    if city:
        query = query.filter(DonorProfile.city.contains(city))
    
    donors = query.paginate(page=page, per_page=per_page, error_out=False)
    return jsonify({
        'donors': [{'id': d.id, 'full_name': d.full_name, 'blood_group': d.blood_group, 'city': d.city, 'availability_status': d.availability_status, 'eligibility_status': d.eligibility_status.value} for d in donors.items],
        'total': donors.total,
        'pages': donors.pages,
        'page': donors.page
    })

@api_bp.route('/donors/match/<blood_group>', methods=['GET'])
@login_required
def match_donors(blood_group):
    role_check('staff', 'admin')
    compatible = BloodCompatibilityService.get_compatible_donors(blood_group)
    donors = DonorProfile.query.filter(
        DonorProfile.blood_group.in_(compatible),
        DonorProfile.eligibility_status == 'Eligible',
        DonorProfile.availability_status == 'Available'
    ).limit(20).all()
    return jsonify([{'id': d.id, 'full_name': d.full_name, 'blood_group': d.blood_group, 'city': d.city} for d in donors])

@api_bp.route('/blood-compatibility/<blood_group>', methods=['GET'])
@login_required
def blood_compatibility(blood_group):
    compatible = BloodCompatibilityService.get_compatible_recipients(blood_group)
    donors = BloodCompatibilityService.get_compatible_donors(blood_group)
    return jsonify({'can_donate_to': compatible, 'can_receive_from': donors})

@api_bp.route('/donations', methods=['GET'])
@login_required
@staff_required
def get_donations():
    donations = Donation.query.order_by(Donation.donation_date.desc()).limit(50).all()
    return jsonify([{'id': d.id, 'donor': d.donor.full_name, 'date': d.donation_date.isoformat(), 'blood_group': d.blood_group, 'status': d.donation_status.value} for d in donations])

@api_bp.route('/donations', methods=['POST'])
@login_required
@staff_required
def create_donation():
    data = request.get_json()
    donation = Donation(
        donor_id=data.get('donor_id'),
        staff_id=current_user.id,
        donation_date=data.get('donation_date'),
        blood_group=data.get('blood_group'),
        quantity=data.get('quantity', 1.0),
        collection_location=data.get('collection_location'),
        donation_status=data.get('donation_status', 'Pending')
    )
    db.session.add(donation)
    db.session.commit()
    log_audit('CREATE', 'Donation', donation.id, f'API: Staff {current_user.username} created donation')
    return jsonify({'id': donation.id, 'message': 'Donation created'}), 201

@api_bp.route('/blood-requests', methods=['GET'])
@login_required
def get_requests():
    role_check('staff', 'admin', 'recipient')
    requests = BloodRequest.query.order_by(BloodRequest.created_at.desc()).limit(50).all()
    return jsonify([{'id': r.id, 'blood_group': r.required_blood_group, 'urgency': r.urgency.value, 'status': r.status.value, 'city': r.city} for r in requests])

@api_bp.route('/blood-requests', methods=['POST'])
@login_required
def create_request():
    role_check('recipient', 'staff', 'admin')
    data = request.get_json()
    blood_request = BloodRequest(
        recipient_id=data.get('recipient_id', current_user.id),
        required_blood_group=data.get('required_blood_group'),
        units_required=data.get('units_required'),
        hospital=data.get('hospital'),
        city=data.get('city'),
        required_date=data.get('required_date'),
        urgency=data.get('urgency', 'Normal')
    )
    db.session.add(blood_request)
    db.session.commit()
    log_audit('CREATE', 'BloodRequest', blood_request.id, f'API: User {current_user.username} created blood request')
    return jsonify({'id': blood_request.id, 'message': 'Request created'}), 201

@api_bp.route('/blood-requests/<int:request_id>', methods=['PUT'])
@login_required
@staff_required
def update_request(request_id):
    blood_request = BloodRequest.query.get_or_404(request_id)
    data = request.get_json()
    if 'status' in data:
        blood_request.status = data['status']
    if 'assigned_staff_id' in data:
        blood_request.assigned_staff_id = data['assigned_staff_id']
    db.session.commit()
    log_audit('UPDATE', 'BloodRequest', blood_request.id, f'API: Staff {current_user.username} updated request')
    return jsonify({'message': 'Request updated'})
