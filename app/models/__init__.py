from datetime import datetime, date
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import enum
from app import db

class UserRole(enum.Enum):
    DONOR = 'donor'
    RECIPIENT = 'recipient'
    STAFF = 'staff'
    ADMIN = 'admin'

class EligibilityStatus(enum.Enum):
    PENDING_MEDICAL_REVIEW = 'Pending Medical Review'
    ELIGIBLE = 'Eligible'
    TEMPORARILY_DEFERRED = 'Temporarily Deferred'
    PERMANENTLY_DEFERRED = 'Permanently Deferred'

class DonationStatus(enum.Enum):
    PENDING = 'Pending'
    ACCEPTED = 'Accepted'
    REJECTED = 'Rejected'
    TESTED = 'Tested'
    AVAILABLE = 'Available'
    USED = 'Used'
    EXPIRED = 'Expired'

class RequestStatus(enum.Enum):
    PENDING = 'Pending'
    UNDER_REVIEW = 'Under Review'
    APPROVED = 'Approved'
    SEARCHING_FOR_DONOR = 'Searching for Donor'
    DONOR_FOUND = 'Donor Found'
    FULFILLED = 'Fulfilled'
    CANCELLED = 'Cancelled'
    REJECTED = 'Rejected'

class UrgencyLevel(enum.Enum):
    NORMAL = 'Normal'
    URGENT = 'Urgent'
    CRITICAL = 'Critical'

class ComponentType(enum.Enum):
    WHOLE_BLOOD = 'Whole Blood'
    RED_CELLS = 'Red Cells'
    PLASMA = 'Plasma'
    PLATELETS = 'Platelets'

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.Enum(UserRole, values_callable=lambda e: [member.value for member in e]), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    donor_profile = db.relationship('DonorProfile', backref='user', uselist=False, cascade='all, delete-orphan')
    recipient_profile = db.relationship('RecipientProfile', backref='user', uselist=False, cascade='all, delete-orphan')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def get_full_name(self):
        if self.donor_profile:
            return self.donor_profile.full_name
        if self.recipient_profile:
            return self.recipient_profile.full_name
        return self.username

class DonorProfile(db.Model):
    __tablename__ = 'donor_profiles'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    full_name = db.Column(db.String(120), nullable=False)
    date_of_birth = db.Column(db.Date, nullable=False)
    gender = db.Column(db.String(20), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    address = db.Column(db.String(200))
    city = db.Column(db.String(100), nullable=False, index=True)
    blood_group = db.Column(db.String(5), nullable=False, index=True)
    rh_factor = db.Column(db.String(5), nullable=False)
    weight = db.Column(db.Float)
    height = db.Column(db.Float)
    emergency_contact = db.Column(db.String(20))
    last_donation_date = db.Column(db.Date)
    next_eligible_date = db.Column(db.Date)
    eligibility_status = db.Column(db.Enum(EligibilityStatus, values_callable=lambda e: [member.value for member in e]), default=EligibilityStatus.PENDING_MEDICAL_REVIEW)
    availability_status = db.Column(db.String(20), default='Available')
    medical_screening = db.Column(db.JSON)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    donations = db.relationship('Donation', backref='donor', lazy='dynamic')
    
    @property
    def age(self):
        if not self.date_of_birth:
            return None
        today = date.today()
        return today.year - self.date_of_birth.year - ((today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day))

class RecipientProfile(db.Model):
    __tablename__ = 'recipient_profiles'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    full_name = db.Column(db.String(120), nullable=False)
    date_of_birth = db.Column(db.Date, nullable=False)
    gender = db.Column(db.String(20), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    city = db.Column(db.String(100), nullable=False, index=True)
    hospital = db.Column(db.String(200))
    emergency_contact = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    blood_requests = db.relationship('BloodRequest', backref='recipient', lazy='dynamic')
    
    @property
    def age(self):
        if not self.date_of_birth:
            return None
        today = date.today()
        return today.year - self.date_of_birth.year - ((today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day))

class BloodGroup(db.Model):
    __tablename__ = 'blood_groups'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(5), unique=True, nullable=False)
    description = db.Column(db.String(200))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    inventory = db.relationship('BloodInventory', backref='blood_group_ref', lazy='dynamic')

class Donation(db.Model):
    __tablename__ = 'donations'
    
    id = db.Column(db.Integer, primary_key=True)
    donor_id = db.Column(db.Integer, db.ForeignKey('donor_profiles.id'), nullable=False, index=True)
    staff_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    donation_date = db.Column(db.Date, nullable=False, index=True)
    blood_group = db.Column(db.String(5), nullable=False, index=True)
    quantity = db.Column(db.Float, default=1.0)
    collection_location = db.Column(db.String(200))
    screening_status = db.Column(db.String(50))
    donation_status = db.Column(db.Enum(DonationStatus, values_callable=lambda e: [member.value for member in e]), default=DonationStatus.PENDING)
    component_type = db.Column(db.Enum(ComponentType, values_callable=lambda e: [member.value for member in e]), default=ComponentType.WHOLE_BLOOD)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    staff = db.relationship('User', backref='recorded_donations')
    inventory_items = db.relationship('BloodInventory', backref='donation', lazy='dynamic')

class BloodRequest(db.Model):
    __tablename__ = 'blood_requests'
    
    id = db.Column(db.Integer, primary_key=True)
    recipient_id = db.Column(db.Integer, db.ForeignKey('recipient_profiles.id'), nullable=False, index=True)
    required_blood_group = db.Column(db.String(5), nullable=False, index=True)
    units_required = db.Column(db.Integer, nullable=False)
    hospital = db.Column(db.String(200))
    city = db.Column(db.String(100), nullable=False, index=True)
    required_date = db.Column(db.Date, nullable=False, index=True)
    urgency = db.Column(db.Enum(UrgencyLevel, values_callable=lambda e: [member.value for member in e]), default=UrgencyLevel.NORMAL, index=True)
    notes = db.Column(db.Text)
    status = db.Column(db.Enum(RequestStatus, values_callable=lambda e: [member.value for member in e]), default=RequestStatus.PENDING, index=True)
    assigned_staff_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    assigned_staff = db.relationship('User', backref='assigned_requests')

class BloodInventory(db.Model):
    __tablename__ = 'blood_inventory'
    
    id = db.Column(db.Integer, primary_key=True)
    blood_group = db.Column(db.String(5), nullable=False, index=True)
    blood_group_id = db.Column(db.Integer, db.ForeignKey('blood_groups.id'), nullable=True)
    component_type = db.Column(db.Enum(ComponentType, values_callable=lambda e: [member.value for member in e]), default=ComponentType.WHOLE_BLOOD)
    units_available = db.Column(db.Float, default=0.0)
    collection_date = db.Column(db.Date, nullable=False, index=True)
    expiry_date = db.Column(db.Date, nullable=False, index=True)
    status = db.Column(db.String(50), default='Available')
    donation_id = db.Column(db.Integer, db.ForeignKey('donations.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Notification(db.Model):
    __tablename__ = 'notifications'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    notification_type = db.Column(db.String(50))
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    user = db.relationship('User', backref='notifications')

class AuditLog(db.Model):
    __tablename__ = 'audit_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True, index=True)
    action = db.Column(db.String(100), nullable=False)
    entity_type = db.Column(db.String(50), nullable=False)
    entity_id = db.Column(db.Integer)
    description = db.Column(db.Text)
    ip_address = db.Column(db.String(45))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    user = db.relationship('User', backref='audit_logs_list')
