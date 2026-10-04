from flask import Blueprint, render_template, redirect, url_for
from flask_login import current_user, login_required

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    if current_user.is_authenticated:
        if current_user.role.value == 'donor':
            return redirect(url_for('donor.dashboard'))
        elif current_user.role.value == 'recipient':
            return redirect(url_for('recipient.dashboard'))
        else:
            return redirect(url_for('staff.dashboard'))
    return redirect(url_for('auth.login'))

@main_bp.route('/about')
def about():
    return render_template('about.html')

@main_bp.route('/how-it-works')
def how_it_works():
    return render_template('how_it_works.html')

@main_bp.route('/find-blood')
def find_blood():
    return render_template('find_blood.html')

@main_bp.route('/become-donor')
def become_donor():
    return render_template('become_donor.html')

@main_bp.route('/blood-compatibility')
def blood_compatibility():
    return render_template('blood_compatibility.html')

@main_bp.route('/contact')
def contact():
    return render_template('contact.html')
