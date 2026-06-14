# A Healthy Life Recommendation System Using Artificial Intelligence

An AI-powered full-stack health recommendation web application. The system analyzes user physical metrics (age, gender, height, weight, activity levels, and health goals) to compute their Body Mass Index (BMI) and predict personalized wellness recommendations (diet plans, exercise regimes, sleep guidelines, and water intake targets) using a Machine Learning Decision Tree model.

## Tech Stack
* **Frontend:** HTML5, CSS3, JavaScript (ES6+), Bootstrap 5 (Responsive Layouts)
* **Backend:** Python Flask
* **Database:** MySQL (Primary) with SQLite (Automatic Fallback for standalone local runs)
* **AI/ML:** Python Scikit-Learn (Decision Tree Classifier) with a native Python rule-based fallback

---

## Features
1. **Secure Authentication:** Sign up, sign in, and secure session management. Password hashing utilizes Werkzeug security.
2. **Dynamic Dashboard:** Consolidated card indicators summarizing current metrics, BMI levels, and wellness routes.
3. **Interactive BMI Gauge:** Real-time client-side BMI calculator that updates a color-coded gauge and suggests health tips instantly.
4. **AI Recommendation Engine:** Categorizes user profiles to suggest Indian simple meals, specific workout targets, water requirements, and sleep cycles.
5. **Interactive Water Tracker:** Log glasses of water and monitor progress.
6. **Sleep Cycle Calculator:** Computes optimal bedtimes based on 90-minute sleep cycle intervals.
7. **Daily Wellness Tips:** Rotates wellness advice across multiple categories.
8. **Emergency Helpline:** Directory of medical and support services with instant copy-to-clipboard functionality.

---

## Directory Structure
```
/health-ai-system
│── app.py                 # Main Flask Server
│── config.py              # Application settings
│── db_connection.py       # DB Connection wrapper (MySQL + SQLite fallback)
│── requirements.txt       # Dependencies
│── README.md              # Documentation
│── /models
│     └── ai_engine.py     # AI recommendation engine (Scikit-Learn model + fallbacks)
│── /database
│     └── db.sql           # MySQL DDL Schema
│── /static
│     ├── css/style.css    # Custom layout stylesheet (Emerald theme)
│     └── js/script.js     # Responsive client-side scripts
│── /templates             # Jinja2 Layout Templates
      ├── base.html        # Shared layout structure
      ├── index.html       # Landing page
      ├── login.html       # Sign-in
      ├── register.html    # Sign-up
      ├── dashboard.html   # Main dashboard summaries
      ├── profile.html     # Physical metric form inputs
      ├── bmi.html         # Interactive BMI calculator
      ├── diet.html        # Detailed dietary plans
      ├── fitness.html     # Workout tables
      ├── water.html       # Water logger progress bar
      ├── sleep.html       # Sleep cycles
      ├── tips.html        # Rotator wellness advice
      └── emergency.html   # Helplines directory
```

---

## Setup & Running Instructions

### 1. Install Dependencies
Make sure you have Python installed, then install the required libraries:
```bash
pip install -r requirements.txt
```
*(If you want to run strictly with MySQL and do not have C++ compilation tools, you can run `pip install flask PyMySQL cryptography python-dotenv scikit-learn` instead.)*

### 2. Database Configurations (Optional)
By default, the application is designed to be **completely standalone**. If MySQL is not running on your computer, the application automatically initializes a local SQLite file (`healthy_life.db`) inside the folder and remains fully functional!

To run with MySQL:
1. Start your local MySQL server.
2. If using custom credentials, create a `.env` file or set the environment variables:
   ```env
   DB_HOST=localhost
   DB_USER=root
   DB_PASSWORD=your_password
   DB_NAME=healthy_life_db
   DB_PORT=3306
   SECRET_KEY=some_unique_secret
   ```
3. The app will automatically initialize the database and tables upon startup. Alternatively, you can import `/database/db.sql` manually.

### 3. Start the Server
Start the Flask app:
```bash
python app.py
```
Open your browser and navigate to `http://127.0.0.1:5000` to interact with the system!
