import os
from dotenv import load_dotenv
from flask import Flask, render_template, request, jsonify
from flask_wtf import CSRFProtect
from forms import MainForm
from flask import Flask, render_template, request
import pandas as pd
from flask import session, redirect, url_for
from forms import UploadForm, MainForm
from extract_data import main as extract 
from pprint import pprint
from datetime import datetime

# Load environment variables from .env file (in development)
load_dotenv()

app = Flask(__name__)

# Get secret key from environment variable
app.config['SECRET_KEY'] = os.environ.get('FLASK_SECRET_KEY')

# Ensure secret key is set
if not app.config['SECRET_KEY']:
    if app.debug:
        # For development only, generate a temporary key
        import secrets
        app.config['SECRET_KEY'] = secrets.token_hex(16)
        print("WARNING: Using temporary secret key")
    else:
        raise RuntimeError("No secret key set for Flask application")

# Initialize CSRF protection
csrf = CSRFProtect(app)

# Skip the upload with DEV_MODE
DEV_MODE = True
LOCAL_FILE1 = "temp_files/sofie_data.txt"
LOCAL_FILE2 = "temp_files/topdesk_data.txt"

global data

@app.route("/", methods=["GET", "POST"])
def upload_files():
    """Upload files, extract data and redirect to the prefilled form."""
    form = UploadForm()

    if DEV_MODE:
        with open(LOCAL_FILE1, "r", encoding="utf-8") as file1, \
             open(LOCAL_FILE2, "r", encoding="utf-8") as file2:
            sofie_data = file1.read()
            topdesk_data = file2.read()
            data = extract(sofie_data, topdesk_data, dev_mode=True)

    elif form.validate_on_submit():
        sofie_data = form.sofie_file.data.read()
        topdesk_data = form.topdesk_file.data.read()
        data = extract(sofie_data, topdesk_data)

    else:
        return render_template("upload2.html", form=form)

    for key, value in data.items():
        session[f"form_{key}"] = value

    return redirect(url_for('index'))

@app.route('/form', methods=['GET', 'POST'])
def index():
    form = MainForm()

    if request.method == 'GET':
        # Prefill regular fields from session
        for field in form:
            if field.name not in ['csrf_token', 'submit', 'nl_residence_dates']:
                session_key = f"form_{field.name}"
                if session_key in session:
                    field.data = session.get(session_key)

        # Special handling for nl_residence_dates (list of lists format)
        nl_residence_data = session.get("form_nl_residence_dates", [])
        form.nl_residence_dates.entries = []  # Clear existing entries

        for date_range in nl_residence_data:
            if isinstance(date_range, list) and len(date_range) == 2:
                form.nl_residence_dates.append_entry({
                    'start_date': date_range[0],
                    'end_date': date_range[1]
                })
            elif isinstance(date_range, dict):
                # Fallback for dict format if it ever changes
                form.nl_residence_dates.append_entry(date_range)

    if request.method == 'POST':
        if form.validate_on_submit():
            # Print the session before updating it
            print("\n=== SESSION BEFORE UPDATE ===")
            for key, value in session.items():
                print(f"{key}: {value}")

            # Process form data and save to session
            for field in form:
                if field.name not in ['csrf_token', 'submit']:
                    session[f"form_{field.name}"] = field.data

            # Save nl_residence_dates in the list of lists format
            residence_dates = []
            for entry in form.nl_residence_dates.entries:
                residence_dates.append([
                    entry.start_date.data,
                    entry.end_date.data
                ])
            session["form_nl_residence_dates"] = residence_dates
            
            # Print the updated session
            print("\n=== SESSION AFTER UPDATE ===")
            for key, value in session.items():
                print(f"{key}: {value}")

            return render_template('results2.html', form=form)    
        else:
            print("Validation failed. Errors:", form.errors)
    
    return render_template('form.html', form=form)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)