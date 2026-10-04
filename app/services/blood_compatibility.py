from datetime import date, timedelta
from app.models import db, BloodGroup
from config import Config

class BloodCompatibilityService:
    
    COMPATIBILITY = {
        'O-': {'can_donate_to': ['O-', 'O+', 'A-', 'A+', 'B-', 'B+', 'AB-', 'AB+'], 'can_receive_from': ['O-']},
        'O+': {'can_donate_to': ['O+', 'A+', 'B+', 'AB+'], 'can_receive_from': ['O-', 'O+']},
        'A-': {'can_donate_to': ['A-', 'A+', 'AB-', 'AB+'], 'can_receive_from': ['O-', 'A-']},
        'A+': {'can_donate_to': ['A+', 'AB+'], 'can_receive_from': ['O-', 'O+', 'A-', 'A+']},
        'B-': {'can_donate_to': ['B-', 'B+', 'AB-', 'AB+'], 'can_receive_from': ['O-', 'B-']},
        'B+': {'can_donate_to': ['B+', 'AB+'], 'can_receive_from': ['O-', 'O+', 'B-', 'B+']},
        'AB-': {'can_donate_to': ['AB-', 'AB+'], 'can_receive_from': ['O-', 'A-', 'B-', 'AB-']},
        'AB+': {'can_donate_to': ['AB+'], 'can_receive_from': ['O-', 'O+', 'A-', 'A+', 'B-', 'B+', 'AB-', 'AB+']},
    }
    
    @classmethod
    def get_compatible_donors(cls, blood_group):
        donors = []
        for bg, compat in cls.COMPATIBILITY.items():
            if blood_group in compat['can_donate_to']:
                donors.append(bg)
        return donors
    
    @classmethod
    def get_compatible_recipients(cls, blood_group):
        recipients = []
        compat = cls.COMPATIBILITY.get(blood_group)
        if compat:
            recipients = compat['can_donate_to']
        return recipients
    
    @classmethod
    def can_donate_to(cls, donor_bg, recipient_bg):
        compat = cls.COMPATIBILITY.get(donor_bg)
        if compat:
            return recipient_bg in compat['can_donate_to']
        return False
    
    @classmethod
    def seed_blood_groups(cls):
        groups = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']
        for g in groups:
            if not BloodGroup.query.filter_by(name=g).first():
                bg = BloodGroup(name=g)
                db.session.add(bg)
        db.session.commit()
        print(f"Seeded {len(groups)} blood groups.")

class EligibilityService:
    
    @staticmethod
    def calculate_next_eligible_date(last_donation_date):
        if not last_donation_date:
            return date.today()
        return last_donation_date + timedelta(days=90)
    
    @staticmethod
    def calculate_age(date_of_birth):
        if not date_of_birth:
            return None
        today = date.today()
        return today.year - date_of_birth.year - ((today.month, today.day) < (date_of_birth.month, date_of_birth.day))
    
    @staticmethod
    def evaluate_eligibility(medical_screening):
        if not medical_screening:
            return 'Pending Medical Review'
        
        screening = medical_screening if isinstance(medical_screening, dict) else {}
        
        if screening.get('recent_surgery') or screening.get('infections_fever') or screening.get('medical_condition'):
            return 'Temporarily Deferred'
        
        if screening.get('medication') or screening.get('recent_vaccination'):
            return 'Pending Medical Review'
        
        if screening.get('not_feeling_healthy'):
            return 'Temporarily Deferred'
        
        return 'Eligible'
