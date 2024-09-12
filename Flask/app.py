"""This program using Flask to generate a simple website with login and password features"""
#Ayman Karam

import re
from datetime import datetime
import logging
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash


app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

logging.basicConfig(filename='failed_logins.log', level=logging.INFO)
users_db = {}

categories = {
    "chest": [
        {
            "name": "Bench Press",
            "url": "https://www.healthline.com/health/exercise-fitness/bench-press-muscles-worked#how-toche"
        },
        {
            "name": "Chest Fly",
            "url": "https://www.muscleandstrength.com/exercises/dumbbell-flys.html"
        },
        {
            "name": "Push-Up",
            "url": "https://www.verywellfit.com/the-push-up-exercise-3120574"
        },
    ],
    "back": [
        {
            "name": "Pull-Up",
            "url": "https://www.healthline.com/health/exercise-fitness/benefit-of-pull-up"
        },
        {
            "name": "Rows",
            "url": "https://blog.goodlifefitness.com/article/5-effective-row-variations-to-target-your-back"
        },
        {
            "name": "Pull-Downs",
            "url": "https://www.verywellfit.com/how-to-do-the-lat-pulldown-3498309"
        },
    ],
    "legs": [
        {
            "name": "Squats",
            "url": "https://www.healthline.com/health/exercise-fitness/squats-benefits"
        },
        {
            "name": "Hamstring Curls",
            "url": "https://www.healthline.com/health/hamstring-curls"
        },
        {
            "name": "Lunges",
            "url": "https://www.verywellfit.com/how-to-lunge-variations-modifications-and-mistakes-1231320"
        },
    ],
    "arms": [
        {
            "name": "Bicep Curl",
            "url": "https://www.menshealth.com/uk/how-tos/a748583/dumbbell-bicep-curls/"
        },
        {
            "name": "Tricep Extension",
            "url": "https://barbend.com/triceps-extension-variations/"
        },
        {
            "name": "Hammer Curl",
            "url": "https://www.menshealth.com/fitness/a28105652/dumbbell-hammer-curl/"
        },
    ]
}


@app.route('/')
def index():
    """Function that generates a splash page with all categories and the current date & time."""
    if 'username' in session:
        now = datetime.now()
        date_time = now.strftime("%m/%d/%y, %H:%M:%S")
        return render_template('index.html', categories=categories, date_time=date_time,
                       username=session['username'])
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    """This functon handles user registration"""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Check password complexity
        if not re.match(r'(?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?=.*\W).{12,}', password):
            flash('Password does not meet complexity requirements.')
            return redirect(url_for('register'))

        # Hash password and save user
        hashed_password = generate_password_hash(password)
        users_db[username] = hashed_password
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """This function handles user login"""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user_password_hash = users_db.get(username)
        if user_password_hash and check_password_hash(user_password_hash, password):
            session['username'] = username
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password.')
    return render_template('login.html')

def load_common_passwords():
    """Function that loads the list of common passwords"""
    with open('CommonPassword.txt', encoding='utf-8') as f:
        return f.read().splitlines()

common_passwords = load_common_passwords()

@app.route('/update_password', methods=['GET', 'POST'])
def update_password():
    """Function that allows user to update their password"""
    if 'username' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        new_password = request.form['new_password']
        # Complexity check (length, uppercase, lowercase, digit, special character)
        if (len(new_password) < 12 or
            not any(char.isdigit() for char in new_password) or
            not any(char.isupper() for char in new_password) or
            not any(char.islower() for char in new_password) or
            new_password in common_passwords):
            flash('Your password must be at least 12 characters long, include upper and '
      'lowercase letters, a number, and not be a common password.')
            return render_template('update_password.html')
        username = session['username']
        hashed_password = generate_password_hash(new_password)
        users_db[username] = hashed_password  # Update the user's password
        flash('Your password has been updated successfully.')
        return redirect(url_for('index'))  # Redirect to a confirmation or home page
    return render_template('update_password.html')



def log_failed_login(username):
    """Log a failed login attempt to a log file"""
    ip_address = request.remote_addr
    logging.info(
    "Failed login attempt for %s from IP %s on %s", 
    username, ip_address,
    datetime.now().strftime('%Y-%m-%d %H:%M:%S')
)



@app.route('/logout')
def logout():
    """This function handles user logout."""
    session.pop('username', None)
    return redirect(url_for('login'))


@app.route("/workout/<category>")
def workout_category(category):
    """Function that generates a home page for a specific workout category."""
    items = categories.get(category.lower(), [])
    return render_template('list-display.html', category=category.capitalize(), items=items)

@app.route("/now")
def show_datetime():
    """Function that displays the current date and time."""
    now = datetime.now()
    date_time = now.strftime("%m/%d/%y, %H:%M:%S")
    return render_template('date-time.html', date_time=date_time)

if __name__ =="__main__":
    app.run(debug=True)
