from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import Form, StringField, FieldList, FormField, DateField, SelectField, SubmitField
from wtforms.validators import DataRequired, Optional

class UploadForm(FlaskForm):
    sofie_file = FileField('Sofie form', validators=[FileAllowed(['pdf']), FileRequired()])
    topdesk_file = FileField('Topdesk form', validators=[FileAllowed(['pdf']), FileRequired()])
    submit = SubmitField('Upload')

class DateRangeForm(Form):
    start_date = DateField('Start Date', format='%Y-%m-%d', render_kw={"type": "date"}, validators=[DataRequired()])
    end_date = DateField('End Date', format='%Y-%m-%d', render_kw={"type": "date"}, validators=[DataRequired()])
    
class ResidenceForm(Form):
    start_date = DateField('Start Date', format='%Y-%m-%d', render_kw={"type": "date"}, validators=[DataRequired()])
    end_date = DateField('End Date', format='%Y-%m-%d', render_kw={"type": "date"}, validators=[DataRequired()])
    city = StringField('City', validators=[DataRequired()])
    country = StringField('Country', validators=[DataRequired()])

class MainForm(FlaskForm):
    request_type = SelectField('Request type', choices=[('regular', 'Regular Application'), ('promovendus', 'Promovendus Exception'), ('returning_expat', 'Returning Expat Exception'), ('change_of_employer', 'Change of Employer Exception')], validators=[DataRequired()])
    name = StringField('Name', validators=[DataRequired()])
    arrival_date = DateField('Arrival date', format='%Y-%m-%d', render_kw={"type": "date"}, validators=[DataRequired()])
    first_work_date = DateField('First work date', format='%Y-%m-%d', render_kw={"type": "date"}, validators=[DataRequired()])
    places_of_residence = FieldList(FormField(ResidenceForm), label='Place of residence', min_entries=1)
    nl_residence_dates = FieldList(FormField(DateRangeForm), label='NL residence dates', min_entries=0, validators=[Optional()])
    nl_deregister_date = DateField('Deregister date', format='%Y-%m-%d', render_kw={"type": "date"}, validators=[Optional()])
    nl_private_dates = FieldList(FormField(DateRangeForm), label='NL private dates', min_entries=0, validators=[Optional()])
    nl_dutch_employer_dates = FieldList(FormField(DateRangeForm), label='NL dutch employer dates', min_entries=0, validators=[Optional()])
    nl_worked_dates = FieldList(FormField(DateRangeForm), label='NL worked dates', min_entries=0, validators=[Optional()])
    employer = StringField('Employer', validators=[DataRequired()])
    payroll_tax_number = StringField('Loonheffingsnummer', validators=[DataRequired()])
    employer_type = StringField('Public or Private', validators=[DataRequired()])
    date_of_birth = DateField('Date of birth', format='%Y-%m-%d', render_kw={"type": "date"}, validators=[DataRequired()])
    bsn = StringField('BSN', validators=[DataRequired()])
    job_title = StringField('Job title', validators=[DataRequired()])
    contract_start_date = DateField('Contract start', format='%Y-%m-%d', render_kw={"type": "date"}, validators=[DataRequired()])
    ufo_code = StringField('UFO code', validators=[DataRequired()])
    application_date = DateField('Application submitted', format='%Y-%m-%d', render_kw={"type": "date"}, validators=[DataRequired()])
    contract_signed_date = DateField('Contract signed', format='%Y-%m-%d', render_kw={"type": "date"}, validators=[DataRequired()])
    willagreement_info = StringField('Explain wilsovereenkomst', validators=[Optional()])
    willagreement_signed_date = DateField('Willagreement signed', format='%Y-%m-%d', render_kw={"type": "date"}, validators=[Optional()])
    previous_jobs = StringField('Previous jobs', validators=[DataRequired()])
    nl_info = StringField('Explain periods in NL', validators=[Optional()])
    submit = SubmitField('Submit')  