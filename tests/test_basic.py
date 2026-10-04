import unittest
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from run import app, db
from app.models import User, DonorProfile, RecipientProfile

class BasicTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app.config['WTF_CSRF_ENABLED'] = False
        self.client = self.app.test_client()
        with self.app.app_context():
            db.create_all()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_home_page(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_login_page(self):
        response = self.client.get('/auth/login')
        self.assertEqual(response.status_code, 200)

    def test_donor_registration(self):
        response = self.client.post('/auth/register/donor', data={
            'username': 'testdonor',
            'email': 'test@example.com',
            'password': 'testpass123',
            'confirm_password': 'testpass123',
            'full_name': 'Test Donor',
            'date_of_birth': '1990-01-01',
            'gender': 'Male',
            'phone': '03001234567',
            'city': 'Karachi',
            'blood_group': 'O+',
            'rh_factor': 'Positive'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    def test_recipient_registration(self):
        response = self.client.post('/auth/register/recipient', data={
            'username': 'testrecipient',
            'email': 'recipient@example.com',
            'password': 'testpass123',
            'confirm_password': 'testpass123',
            'full_name': 'Test Recipient',
            'date_of_birth': '1985-05-05',
            'gender': 'Female',
            'phone': '03009876543',
            'city': 'Lahore',
            'hospital': 'Test Hospital'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)

if __name__ == '__main__':
    unittest.main()
