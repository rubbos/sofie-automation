from flask_wtf import FlaskForm
from wtforms import StringField, FieldList, FormField, DateField
from wtforms.validators import DataRequired
from flask_wtf.file import FileField, FileAllowed
from wtforms import SubmitField

class UploadForm(FlaskForm):
    sofie_file = FileField('Sofie form', validators=[FileAllowed(['pdf'])])
    topdesk_file = FileField('Topdesk form', validators=[FileAllowed(['pdf'])])
    submit = SubmitField('Upload')


class DateRangeForm(FlaskForm):
    start_date = DateField('Start Date', format='%d-%m-%Y', validators=[DataRequired()])
    end_date = DateField('End Date', format='%d-%m-%Y', validators=[DataRequired()])
    
class ResidenceForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired()])
    phone = StringField('Phone')
    address = StringField('Address')

class MainForm(FlaskForm):
    request_type = StringField('Request type', validators=[DataRequired()])
    name = StringField('Name', validators=[DataRequired()])
    arrival_date = DateField('Arrival date', format='%Y-%m-%d', render_kw={"type": "date"}, validators=[DataRequired()])
    first_work_date = StringField('First work date', validators=[DataRequired()])
    places_of_residence = StringField('Places of Residence', validators=[DataRequired()])
    nl_residence_dates = FieldList(FormField(DateRangeForm), min_entries=0)
    nl_deregister_date = StringField('NL deregister date', validators=[DataRequired()])
    nl_private_dates = StringField('NL private dates', validators=[DataRequired()])
    nl_dutch_employer_dates = StringField('NL worked for dutch employer', validators=[DataRequired()])
    nl_worked_dates = StringField('NL worked dates', validators=[DataRequired()])
    employer = StringField('Employer', validators=[DataRequired()])
    payroll_tax_number = StringField('Loonheffingsnummer', validators=[DataRequired()])
    employer_type = StringField('Public or Private', validators=[DataRequired()])
    date_of_birth = StringField('Date of birth', validators=[DataRequired()])
    bsn = StringField('BSN', validators=[DataRequired()])
    job_title = StringField('Job title', validators=[DataRequired()])
    contract_start_date = StringField('Contract start date', validators=[DataRequired()])
    ufo_code = StringField('UFO code', validators=[DataRequired()])
    application_date = StringField('Application submit date', validators=[DataRequired()])
    contract_signed_date = StringField('Contract signed date', validators=[DataRequired()])
    explain_will_agreement = StringField('Explain wilsovereenkomst', validators=[DataRequired()])
    previous_jobs = StringField('Previous jobs', validators=[DataRequired()])
    nl_explain = StringField('Explain periods in NL', validators=[DataRequired()])
    submit = SubmitField('Submit')  