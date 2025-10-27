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
from utils import process, calculations
from utils.reports import Applicant, create_main_report, create_email_report

DEV_MODE = False
LOCAL_FILE1 = "temp_files/sofie_data.txt"
LOCAL_FILE2 = "temp_files/topdesk_data.txt"
    
# dynamic fields to be processed separately
dynamic_dates_fields = ["nl_residence_dates", "nl_worked_dates",
                "nl_private_dates", "nl_dutch_employer_dates"]
dynamic_residence_fields = ["places_of_residence"]

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

@app.route("/", methods=["GET", "POST"])
def home():
    return render_template('home.html')

@app.route("/sofie", methods=["GET", "POST"])
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
        try:
            sofie_data = form.sofie_file.data.read()
        except Exception:
            sofie_data = None
        topdesk_data = form.topdesk_file.data.read()
        data = extract(sofie_data, topdesk_data)

    else:
        return render_template("upload.html", form=form)

    print(data)
    for key, value in data.items():
        session[f"form_{key}"] = value
        print(session[f"form_{key}"])

    return redirect(url_for('index'))


@app.route('/sofie/form', methods=['GET', 'POST'])
def index():
    form = MainForm()

    if request.method == 'GET':
        # Get all the form session data
        form_data = {}
        for key in session:
            if key.startswith("form_"):
                field_name = key[5:]  # Remove "form_" prefix
                form_data[field_name] = session[key]

        # Process dynamic values
        for key in dynamic_dates_fields + dynamic_residence_fields:
            raw_data = session.get(f"form_{key}", [])
            if key in dynamic_residence_fields:
                form_data[key] = process.residences(raw_data)
            else:
                form_data[key] = process.date_ranges(raw_data)

        # Create a new form with this data
        form = MainForm(**form_data)

    if request.method == 'POST':

        if form.validate_on_submit():
            # Process form data and update session
            data = {}

            for field in form:
                if field.name not in ['csrf_token', 'submit']:
                    data[field.name] = field.data
        

            applicant = Applicant(**data)
            main_report = create_main_report(applicant)
            email_report = create_email_report(applicant)

            return render_template('results.html', main_report=main_report, email_report=email_report)
        else:
            print("Validation failed. Errors:", form.errors)

    return render_template('form.html', form=form)

@app.route("/calculate", methods=["GET", "POST"])
@csrf.exempt
def calculate():
    result = None
    taxable = None
    if request.method == "POST":
        try:
            salary = float(request.form["salary"])
            age = float(request.form["age"])
            taxable = calculations.adjusted_salary(salary)
            result = calculations.salary_percentage(salary, age)
        except ValueError:
            result, taxable = "Invalid input"
    return render_template('calculate.html', result=result, taxable=taxable)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
