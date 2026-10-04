from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_user, logout_user, login_required, current_user
from app.models import User, DonorProfile, RecipientProfile, db
from app.auth import log_audit
from app.forms import LoginForm, DonorRegistrationForm, RecipientRegistrationForm
from app.services.blood_compatibility import EligibilityService
from datetime import date

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = LoginForm()
    if form.validate_on_submit():
        username_or_email = form.username_or_email.data
        password = form.password.data
        user = User.query.filter((User.username == username_or_email) | (User.email == username_or_email)).first()
        if user and user.check_password(password):
            if not user.is_active:
                flash('Your account is deactivated. Please contact support.', 'danger')
                return redirect(url_for('auth.login'))
            login_user(user, remember=form.remember_me.data)
            user.last_login = date.today()
            db.session.commit()
            log_audit('LOGIN', 'User', user.id, f'User {user.username} logged in')
            flash('Login successful!', 'success')
            next_page = request.args.get('next')
            if user.role.value == 'donor':
                return redirect(next_page or url_for('donor.dashboard'))
            elif user.role.value == 'recipient':
                return redirect(next_page or url_for('recipient.dashboard'))
            elif user.role.value == 'staff':
                return redirect(next_page or url_for('staff.dashboard'))
            elif user.role.value == 'admin':
                return redirect(next_page or url_for('admin.dashboard'))
        else:
            flash('Invalid username/email or password.', 'danger')
    return render_template('auth/login.html', form=form)

@auth_bp.route('/register/donor', methods=['GET', 'POST'])
def register_donor():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = DonorRegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data, role='donor')
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.flush()
        
        medical_screening = {
            'not_feeling_healthy': form.not_feeling_healthy.data,
            'recent_surgery': form.recent_surgery.data,
            'medication': form.on_medication.data,
            'medical_condition': form.medical_condition.data,
            'infections_fever': form.infections_fever.data,
            'recent_vaccination': form.recent_vaccination.data
        }
        eligibility = EligibilityService.evaluate_eligibility(medical_screening)
        
        donor_profile = DonorProfile(
            user_id=user.id,
            full_name=form.full_name.data,
            date_of_birth=form.date_of_birth.data,
            gender=form.gender.data,
            phone=form.phone.data,
            address=form.address.data,
            city=form.city.data,
            blood_group=form.blood_group.data,
            rh_factor=form.rh_factor.data,
            weight=form.weight.data,
            height=form.height.data,
            emergency_contact=form.emergency_contact.data,
            last_donation_date=form.last_donation_date.data,
            eligibility_status=eligibility
        )
        
        if form.last_donation_date.data:
            donor_profile.next_eligible_date = EligibilityService.calculate_next_eligible_date(form.last_donation_date.data)
        
        db.session.add(donor_profile)
        db.session.commit()
        log_audit('REGISTER', 'User', user.id, f'Donor {user.username} registered')
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('auth.login'))
    return render_template('auth/register_donor.html', form=form)

@auth_bp.route('/register/recipient', methods=['GET', 'POST'])
def register_recipient():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = RecipientRegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data, role='recipient')
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.flush()
        
        recipient_profile = RecipientProfile(
            user_id=user.id,
            full_name=form.full_name.data,
            date_of_birth=form.date_of_birth.data,
            gender=form.gender.data,
            phone=form.phone.data,
            city=form.city.data,
            hospital=form.hospital.data,
            emergency_contact=form.emergency_contact.data
        )
        
        db.session.add(recipient_profile)
        db.session.commit()
        log_audit('REGISTER', 'User', user.id, f'Recipient {user.username} registered')
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('auth.login'))
    return render_template('auth/register_recipient.html', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    log_audit('LOGOUT', 'User', current_user.id, f'User {current_user.username} logged out')
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.index'))
