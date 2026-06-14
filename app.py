import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash

from config import Config
from db_connection import db_manager
from models.ai_engine import ai_engine

app = Flask(__name__)
app.config.from_object(Config)

# Initialize database tables on server start
with app.app_context():
    try:
        db_manager.init_db()
    except Exception as e:
        print(f"DATABASE INITIALIZATION ERROR: {e}")

# Helper decorator to require login
def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash("Please log in to access this page.", "error")
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def home():
    return render_template("index.html")

@app.route('/register', methods=['GET', 'POST'])
def register():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
        
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        
        if not name or not email or not password:
            flash("All fields are required.", "error")
            return render_template("register.html")
            
        if len(password) < 6:
            flash("Password must be at least 6 characters.", "error")
            return render_template("register.html")
            
        try:
            # Check if user already exists
            existing_user = db_manager.get_user_by_email(email)
            if existing_user:
                flash("An account with this email already exists.", "error")
                return render_template("register.html")
                
            # Hash password securely
            password_hash = generate_password_hash(password, method='scrypt')
            
            # Save user
            db_manager.create_user(name, email, password_hash)
            flash("Registration successful! Please sign in.", "success")
            return redirect(url_for('login'))
        except Exception as e:
            print(f"Registration Error: {e}")
            flash("A database error occurred. Please try again.", "error")
            
    return render_template("register.html")

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
        
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        
        if not email or not password:
            flash("Please enter both email and password.", "error")
            return render_template("login.html")
            
        try:
            user = db_manager.get_user_by_email(email)
            if user and check_password_hash(user['password'], password):
                # Password is correct; establish session
                session['user_id'] = user['id']
                session['user_name'] = user['name']
                session['user_email'] = user['email']
                flash(f"Welcome back, {user['name']}!", "success")
                return redirect(url_for('dashboard'))
            else:
                flash("Incorrect email or password.", "error")
        except Exception as e:
            print(f"Login Error: {e}")
            flash("A database error occurred. Please try again.", "error")
            
    return render_template("login.html")

@app.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out successfully.", "success")
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    try:
        profile = db_manager.get_health_profile(session['user_id'])
        recommendations = None
        
        if profile:
            # Generate recommendations dynamically via AI Engine
            recommendations = ai_engine.get_recommendations(
                age=profile['age'],
                gender=profile['gender'],
                height=profile['height'],
                weight=profile['weight'],
                activity_level=profile['activity_level'],
                goal=profile['goal']
            )
            
        return render_template("dashboard.html", profile=profile, recommendations=recommendations)
    except Exception as e:
        print(f"Dashboard Load Error: {e}")
        flash("Could not load dashboard data.", "error")
        return redirect(url_for('home'))

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    user_id = session['user_id']
    
    if request.method == 'POST':
        try:
            age = int(request.form.get('age'))
            gender = request.form.get('gender')
            height = float(request.form.get('height'))
            weight = float(request.form.get('weight'))
            activity_level = request.form.get('activity_level')
            goal = request.form.get('goal')
            
            # Form validations
            if age < 1 or age > 120 or height < 50 or height > 250 or weight < 20 or weight > 300:
                flash("Please enter logical health metrics.", "error")
                return redirect(url_for('profile'))
                
            db_manager.save_health_profile(user_id, age, gender, height, weight, activity_level, goal)
            flash("Health profile successfully updated!", "success")
            return redirect(url_for('dashboard'))
        except Exception as e:
            print(f"Profile Save Error: {e}")
            flash("Failed to save profile. Make sure all values are numbers.", "error")
            
    try:
        profile = db_manager.get_health_profile(user_id)
        return render_template("profile.html", profile=profile)
    except Exception as e:
        print(f"Profile Retrieval Error: {e}")
        flash("Could not fetch profile details.", "error")
        return redirect(url_for('dashboard'))

@app.route('/bmi')
def bmi():
    profile = None
    if 'user_id' in session:
        try:
            profile = db_manager.get_health_profile(session['user_id'])
        except Exception as e:
            print(f"BMI Profile Error: {e}")
            
    return render_template("bmi.html", profile=profile)

@app.route('/diet')
@login_required
def diet():
    try:
        profile = db_manager.get_health_profile(session['user_id'])
        recommendations = None
        if profile:
            recommendations = ai_engine.get_recommendations(
                age=profile['age'],
                gender=profile['gender'],
                height=profile['height'],
                weight=profile['weight'],
                activity_level=profile['activity_level'],
                goal=profile['goal']
            )
        return render_template("diet.html", profile=profile, recommendations=recommendations)
    except Exception as e:
        print(f"Diet Recommendations Error: {e}")
        flash("Error loading diet plan.", "error")
        return redirect(url_for('dashboard'))

@app.route('/fitness')
@login_required
def fitness():
    try:
        profile = db_manager.get_health_profile(session['user_id'])
        recommendations = None
        if profile:
            recommendations = ai_engine.get_recommendations(
                age=profile['age'],
                gender=profile['gender'],
                height=profile['height'],
                weight=profile['weight'],
                activity_level=profile['activity_level'],
                goal=profile['goal']
            )
        return render_template("fitness.html", profile=profile, recommendations=recommendations)
    except Exception as e:
        print(f"Fitness Recommendations Error: {e}")
        flash("Error loading exercise plan.", "error")
        return redirect(url_for('dashboard'))

@app.route('/water')
def water():
    profile = None
    recommendations = None
    if 'user_id' in session:
        try:
            profile = db_manager.get_health_profile(session['user_id'])
            if profile:
                recommendations = ai_engine.get_recommendations(
                    age=profile['age'],
                    gender=profile['gender'],
                    height=profile['height'],
                    weight=profile['weight'],
                    activity_level=profile['activity_level'],
                    goal=profile['goal']
                )
        except Exception as e:
            print(f"Water Recommendation Error: {e}")
            
    return render_template("water.html", profile=profile, recommendations=recommendations)

@app.route('/sleep')
def sleep():
    profile = None
    recommendations = None
    if 'user_id' in session:
        try:
            profile = db_manager.get_health_profile(session['user_id'])
            if profile:
                recommendations = ai_engine.get_recommendations(
                    age=profile['age'],
                    gender=profile['gender'],
                    height=profile['height'],
                    weight=profile['weight'],
                    activity_level=profile['activity_level'],
                    goal=profile['goal']
                )
        except Exception as e:
            print(f"Sleep Recommendation Error: {e}")
            
    return render_template("sleep.html", profile=profile, recommendations=recommendations)

@app.route('/tips')
def tips():
    return render_template("tips.html")

@app.route('/emergency')
def emergency():
    return render_template("emergency.html")

@app.route('/retry-db')
def retry_db():
    try:
        success = db_manager.check_mysql_connection()
        if success:
            db_manager.init_db()
            flash("Switched database engine successfully to MySQL server!", "success")
        else:
            flash(f"Failed to connect to MySQL database: {db_manager.error_msg}", "error")
    except Exception as e:
        flash(f"Retry error occurred: {e}", "error")
        
    return redirect(url_for('dashboard') if 'user_id' in session else url_for('home'))

if __name__ == '__main__':
    # Get port from environment for production deployment flexibility
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
