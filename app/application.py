import os
from dotenv import load_dotenv
from flask import Flask, render_template, request, jsonify
from flask_wtf import CSRFProtect
from forms import MainForm
from flask import Flask, render_template, request
import pandas as pd
from extractors.tax_form import main as tax_form_main
from extractors.application_form import main as application_form_main
from extractors.extra_info import main as extra_info_main
from utils.reports import (
    create_main_report,
    create_email_report,
    extracted_data,
)
import utils.validation
import logging
from flask import session, redirect, url_for
import json
from forms import UploadForm, MainForm
from extract_data import extract

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
    form = UploadForm()

    if DEV_MODE:
        with open(LOCAL_FILE1, "r", encoding="utf-8") as file1, \
             open(LOCAL_FILE2, "r", encoding="utf-8") as file2:
            sofie_data = file1.read()
            topdesk_data = file2.read()
            data = extract(sofie_data, topdesk_data, dev_mode=True)

    elif form.validate_on_submit():
        # Decode from bytes to string
        sofie_data = form.sofie_file.data.read()
        topdesk_data = form.topdesk_file.data.read()
        data = extract(sofie_data, topdesk_data)

    else:
        return render_template("upload2.html", form=form)

    # Store the extracted data in session
    session["date_ranges"] = json.dumps(data.get("date_ranges", []))
    session["contacts"] = json.dumps(data.get("contacts", []))

    return redirect(url_for('index'))

@app.route('/form', methods=['GET', 'POST'])
def index():
    form = MainForm()
       
    # Only prefill if GET and session data exists
    if request.method == 'GET':
        date_ranges_json = session.pop("date_ranges", "[]")
        contacts_json = session.pop("contacts", "[]")

        date_ranges = json.loads(date_ranges_json)
        contacts = json.loads(contacts_json)

        for item in date_ranges:
            form.date_ranges.append_entry(item)

        for item in contacts:
            form.contacts.append_entry(item) 

    if request.method == 'POST':
        # For dynamic forms, we need to adjust the form before validation
        date_range_count = 0
        contact_count = 0
        
        # Count date ranges
        for key in request.form:
            if key.startswith('date_ranges-') and '-start_date' in key:
                index = int(key.split('-')[1])
                date_range_count = max(date_range_count, index + 1)
        
        # Count contacts
        for key in request.form:
            if key.startswith('contacts-') and '-name' in key:
                index = int(key.split('-')[1])
                contact_count = max(contact_count, index + 1)
        
        # Adjust form with correct number of entries
        while len(form.date_ranges) < date_range_count:
            form.date_ranges.append_entry()
        
        while len(form.contacts) < contact_count:
            form.contacts.append_entry()
        
        if form.validate_on_submit():
            # Process the form data
            date_ranges = form.date_ranges.data
            contacts = form.contacts.data
            
            # Do something with the data (save to database, etc.)
            print("Date Ranges:", date_ranges)
            print("Contacts:", contacts)
            
            return "Form submitted successfully!"
    
    return render_template('form.html', form=form)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)