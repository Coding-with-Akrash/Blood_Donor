import os
from dotenv import load_dotenv
from app import create_app, db
from app.models import User, DonorProfile, RecipientProfile, Donation, BloodRequest, BloodInventory, Notification, AuditLog, BloodGroup

load_dotenv()

app = create_app()

@app.shell_context_processor
def make_shell_context():
    return {
        'db': db,
        'User': User,
        'DonorProfile': DonorProfile,
        'RecipientProfile': RecipientProfile,
        'Donation': Donation,
        'BloodRequest': BloodRequest,
        'BloodInventory': BloodInventory,
        'Notification': Notification,
        'AuditLog': AuditLog,
        'BloodGroup': BloodGroup,
    }

@app.cli.command()
def init_db():
    """Initialize database with default blood groups."""
    db.create_all()
    from app.services.blood_compatibility import BloodCompatibilityService
    BloodCompatibilityService.seed_blood_groups()
    print("Database initialized with default data.")

@app.cli.command()
def create_admin():
    """Create admin account."""
    username = os.environ.get('ADMIN_USERNAME') or input("Admin username: ")
    email = os.environ.get('ADMIN_EMAIL') or input("Admin email: ")
    password = os.environ.get('ADMIN_PASSWORD') or input("Admin password: ")
    
    admin = User(username=username, email=email, role='admin', is_active=True)
    admin.set_password(password)
    db.session.add(admin)
    db.session.commit()
    print(f"Admin user '{username}' created successfully!")

if __name__ == '__main__':
    app.run()
