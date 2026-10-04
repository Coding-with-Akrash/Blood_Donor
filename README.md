# LifeBlood - Blood Donation Management System

A full-stack web application for managing blood donations, connecting donors with recipients, and streamlining blood bank operations.

## Features

- **Donor Registration**: Register as a blood donor with complete profile and medical screening
- **Recipient Registration**: Register as a blood recipient to request blood
- **Blood Requests**: Create and track blood requests with urgency levels
- **Donor Matching**: System matches compatible donors with blood requests
- **Donation Records**: Staff can create and manage donation records
- **Dashboard**: Separate dashboards for donors, recipients, staff, and admins
- **Reports**: Generate donation and request reports
- **Audit Logging**: Track all system activities
- **Notifications**: Internal notification system
- **REST API**: API endpoints for integrations
- **Blood Compatibility**: Educational blood compatibility information

## Technology Stack

- **Backend**: Python Flask
- **Database**: PostgreSQL (production), SQLite (development)
- **ORM**: Flask-SQLAlchemy
- **Authentication**: Flask-Login
- **Forms**: Flask-WTF
- **Frontend**: Bootstrap 5, JavaScript, Chart.js
- **Deployment**: Gunicorn, Render/Railway compatible

## Project Structure

```
blood-donation-system/
├── app/
│   ├── __init__.py
│   ├── models/
│   ├── routes/
│   ├── services/
│   ├── forms/
│   ├── templates/
│   └── static/
├── migrations/
├── tests/
├── run.py
├── config.py
├── requirements.txt
├── .env.example
├── Procfile
├── runtime.txt
└── seed.py
```

## Installation

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate  # Windows
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Copy `.env.example` to `.env` and configure
5. Initialize the database:
   ```bash
   flask init_db
   ```
6. Create admin account:
   ```bash
   python create_admin.py
   ```

## Running the Application

```bash
flask run
# or
python run.py
```

Visit `http://localhost:5000` in your browser.

## Testing

```bash
python -m pytest tests/
```

## Deployment

1. Create a PostgreSQL database (Neon, Supabase, etc.)
2. Set `DATABASE_URL` environment variable
3. Push to GitHub
4. Deploy on Render or similar platform
5. Run `flask db upgrade` to apply migrations
6. Create admin with `python create_admin.py`

## User Roles

- **Donor**: Register, manage profile, view donation history
- **Recipient**: Register, request blood, track requests
- **Staff**: Manage donations, review requests, manage donors
- **Admin**: Full system control, staff management, audit logs

## Security

- Password hashing with Werkzeug
- CSRF protection
- SQL injection protection via SQLAlchemy
- Role-based access control
- Secure session management
- Environment variables for secrets

## License

MIT License
