import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'blood_donation.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-csrf-key-change-in-production'
    
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'True').lower() in ['true', 'on', '1']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER')
    
    APP_NAME = 'LifeBlood'
    
    ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL')
    ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME')
    ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD')
    
    BLOOD_GROUPS = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']
    URGENCY_LEVELS = ['Normal', 'Urgent', 'Critical']
    DONATION_STATUSES = ['Pending', 'Accepted', 'Rejected', 'Tested', 'Available', 'Used', 'Expired']
    REQUEST_STATUSES = ['Pending', 'Under Review', 'Approved', 'Searching for Donor', 'Donor Found', 'Fulfilled', 'Cancelled', 'Rejected']
    ELIGIBILITY_STATUSES = ['Pending Medical Review', 'Eligible', 'Temporarily Deferred', 'Permanently Deferred']
    COMPONENT_TYPES = ['Whole Blood', 'Red Cells', 'Plasma', 'Platelets']
