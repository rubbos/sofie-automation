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
from utils import process

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
        print(session[f"form_{key}"])

    return redirect(url_for('index'))


@app.route('/form', methods=['GET', 'POST'])
def index():
    form = MainForm()

    if request.method == 'GET':
        # Get all the form session data
        form_data = {}
        for key in session:
            if key.startswith("form_"):
                field_name = key[5:]  # Remove "form_" prefix
                form_data[field_name] = session[key]

        # We also need to update the dynamic values from specific fields
        dynamic_keys = ["nl_residence_dates", "nl_worked_dates",
                     "nl_private_dates", "nl_dutch_employer_dates", "places_of_residence"]

        # Process dynamic values
        for key in dynamic_keys:
            raw_data = session.get(f"form_{key}", [])
            if key == "places_of_residence":
                form_data[key] = process.residences(raw_data)
            else:
                form_data[key] = process.date_ranges(raw_data)

        # Create a new form with this data
        form = MainForm(**form_data)

    if request.method == 'POST':

        if form.validate_on_submit():
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
