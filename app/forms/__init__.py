from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, DateField, TextAreaField, FloatField, IntegerField, BooleanField, HiddenField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError, Optional, NumberRange
from app.models import User, DonorProfile, RecipientProfile, BloodRequest, BloodGroup
from config import Config

class LoginForm(FlaskForm):
    username_or_email = StringField('Username or Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')

class DonorRegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    full_name = StringField('Full Name', validators=[DataRequired(), Length(max=120)])
    date_of_birth = DateField('Date of Birth', validators=[DataRequired()])
    gender = SelectField('Gender', choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')], validators=[DataRequired()])
    phone = StringField('Phone Number', validators=[DataRequired(), Length(max=20)])
    address = StringField('Address', validators=[Optional(), Length(max=200)])
    city = StringField('City', validators=[DataRequired(), Length(max=100)])
    emergency_contact = StringField('Emergency Contact', validators=[Optional(), Length(max=20)])
    blood_group = SelectField('Blood Group', choices=[(g, g) for g in Config.BLOOD_GROUPS], validators=[DataRequired()])
    rh_factor = SelectField('Rh Factor', choices=[('Positive', 'Positive'), ('Negative', 'Negative')], validators=[DataRequired()])
    weight = FloatField('Weight (kg)', validators=[Optional(), NumberRange(min=30, max=300)])
    height = FloatField('Height (cm)', validators=[Optional(), NumberRange(min=100, max=250)])
    last_donation_date = DateField('Last Donation Date', validators=[Optional()])
    not_feeling_healthy = BooleanField('Are you currently not feeling healthy?')
    recent_surgery = BooleanField('Have you recently undergone surgery?')
    on_medication = BooleanField('Are you currently taking medication?')
    medical_condition = BooleanField('Do you have any condition that may prevent donation?')
    infections_fever = BooleanField('Have you recently had an infection/fever?')
    recent_vaccination = BooleanField('Have you received a recent vaccination?')
    
    def validate_username(self, username):
        if User.query.filter_by(username=username.data).first():
            raise ValidationError('Username already taken.')
    
    def validate_email(self, email):
        if User.query.filter_by(email=email.data).first():
            raise ValidationError('Email already registered.')

class RecipientRegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    full_name = StringField('Full Name', validators=[DataRequired(), Length(max=120)])
    date_of_birth = DateField('Date of Birth', validators=[DataRequired()])
    gender = SelectField('Gender', choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')], validators=[DataRequired()])
    phone = StringField('Phone Number', validators=[DataRequired(), Length(max=20)])
    city = StringField('City', validators=[DataRequired(), Length(max=100)])
    hospital = StringField('Hospital', validators=[Optional(), Length(max=200)])
    emergency_contact = StringField('Emergency Contact', validators=[Optional(), Length(max=20)])
    
    def validate_username(self, username):
        if User.query.filter_by(username=username.data).first():
            raise ValidationError('Username already taken.')
    
    def validate_email(self, email):
        if User.query.filter_by(email=email.data).first():
            raise ValidationError('Email already registered.')

class BloodRequestForm(FlaskForm):
    required_blood_group = SelectField('Required Blood Group', choices=[(g, g) for g in Config.BLOOD_GROUPS], validators=[DataRequired()])
    units_required = IntegerField('Units Required', validators=[DataRequired(), NumberRange(min=1, max=10)])
    hospital = StringField('Hospital', validators=[DataRequired(), Length(max=200)])
    city = StringField('City', validators=[DataRequired(), Length(max=100)])
    required_date = DateField('Required Date', validators=[DataRequired()])
    urgency = SelectField('Urgency', choices=[(u, u) for u in Config.URGENCY_LEVELS], validators=[DataRequired()])
    notes = TextAreaField('Additional Notes', validators=[Optional(), Length(max=500)])

class DonationForm(FlaskForm):
    donor_id = SelectField('Donor', coerce=int, validators=[DataRequired()])
    donation_date = DateField('Donation Date', validators=[DataRequired()])
    blood_group = SelectField('Blood Group', choices=[(g, g) for g in Config.BLOOD_GROUPS], validators=[DataRequired()])
    quantity = FloatField('Quantity (units)', validators=[DataRequired(), NumberRange(min=0.5, max=2.0)])
    collection_location = StringField('Collection Location', validators=[Optional(), Length(max=200)])
    screening_status = SelectField('Screening Status', choices=[('Passed', 'Passed'), ('Failed', 'Failed'), ('Pending', 'Pending')], validators=[DataRequired()])
    donation_status = SelectField('Donation Status', choices=[(s, s) for s in Config.DONATION_STATUSES], validators=[DataRequired()])
    component_type = SelectField('Component Type', choices=[(c, c) for c in Config.COMPONENT_TYPES], validators=[DataRequired()])
    notes = TextAreaField('Notes', validators=[Optional(), Length(max=500)])

class StaffRegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    full_name = StringField('Full Name', validators=[DataRequired(), Length(max=120)])
    
    def validate_username(self, username):
        if User.query.filter_by(username=username.data).first():
            raise ValidationError('Username already taken.')
    
    def validate_email(self, email):
        if User.query.filter_by(email=email.data).first():
            raise ValidationError('Email already registered.')
