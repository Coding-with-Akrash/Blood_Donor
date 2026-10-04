import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from run import app, db
from app.models import User

with app.app_context():
    db.create_all()
    
    username = input("Admin username: ")
    email = input("Admin email: ")
    password = input("Admin password: ")
    
    if User.query.filter_by(username=username).first():
        print(f"User '{username}' already exists.")
    else:
        admin = User(username=username, email=email, role='admin', is_active=True)
        admin.set_password(password)
        db.session.add(admin)
        db.session.commit()
        print(f"Admin user '{username}' created successfully!")
