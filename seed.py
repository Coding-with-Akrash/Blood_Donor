import os
import sys
from datetime import date, timedelta
import random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from run import app, db
from app.models import User, DonorProfile, RecipientProfile, Donation, BloodRequest, BloodInventory, BloodGroup

with app.app_context():
    db.create_all()
    from app.services.blood_compatibility import BloodCompatibilityService
    BloodCompatibilityService.seed_blood_groups()
    
    blood_groups = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']
    cities = ['Karachi', 'Lahore', 'Islamabad', 'Rawalpindi', 'Faisalabad', 'Peshawar', 'Quetta']
    
    donors = []
    for i in range(10):
        username = f"donor{i+1}"
        user = User(username=username, email=f"{username}@example.com", role='donor')
        user.set_password('donor123')
        db.session.add(user)
        db.session.flush()
        
        donor = DonorProfile(
            user_id=user.id,
            full_name=f"Donor {i+1}",
            date_of_birth=date(1990, 1, 1) + timedelta(days=random.randint(0, 10000)),
            gender=random.choice(['Male', 'Female']),
            phone=f"03{random.randint(100000000, 999999999)}",
            city=random.choice(cities),
            blood_group=random.choice(blood_groups),
            rh_factor=random.choice(['Positive', 'Negative']),
            weight=random.uniform(50, 100),
            height=random.uniform(150, 190),
            eligibility_status=random.choice(['Eligible', 'Eligible', 'Eligible', 'Temporarily Deferred']),
            availability_status=random.choice(['Available', 'Available', 'Not Available'])
        )
        db.session.add(donor)
        donors.append(donor)
    
    recipients = []
    for i in range(5):
        username = f"recipient{i+1}"
        user = User(username=username, email=f"{username}@example.com", role='recipient')
        user.set_password('recipient123')
        db.session.add(user)
        db.session.flush()
        
        recipient = RecipientProfile(
            user_id=user.id,
            full_name=f"Recipient {i+1}",
            date_of_birth=date(1970, 1, 1) + timedelta(days=random.randint(0, 15000)),
            gender=random.choice(['Male', 'Female']),
            phone=f"03{random.randint(100000000, 999999999)}",
            city=random.choice(cities),
            hospital=f"Hospital {i+1}"
        )
        db.session.add(recipient)
        recipients.append(recipient)
    
    staff_user = User(username='staff1', email='staff1@example.com', role='staff')
    staff_user.set_password('staff123')
    db.session.add(staff_user)
    db.session.flush()
    
    for i in range(15):
        donor = random.choice(donors)
        donation = Donation(
            donor_id=donor.id,
            staff_id=staff_user.id,
            donation_date=date.today() - timedelta(days=random.randint(0, 365)),
            blood_group=donor.blood_group,
            quantity=random.uniform(0.5, 1.5),
            collection_location=random.choice(cities),
            donation_status=random.choice(['Accepted', 'Accepted', 'Available', 'Used'])
        )
        db.session.add(donation)
        db.session.flush()
    
    for i in range(10):
        recipient = random.choice(recipients)
        request = BloodRequest(
            recipient_id=recipient.id,
            required_blood_group=random.choice(blood_groups),
            units_required=random.randint(1, 4),
            hospital=f"Hospital {random.randint(1, 5)}",
            city=random.choice(cities),
            required_date=date.today() + timedelta(days=random.randint(1, 30)),
            urgency=random.choice(['Normal', 'Urgent', 'Critical']),
            status=random.choice(['Pending', 'Under Review', 'Approved', 'Fulfilled'])
        )
        db.session.add(request)
    
    db.session.commit()
    print("Seed data created successfully!")
