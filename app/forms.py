from flask_wtf import FlaskForm
from wtforms import StringField, FieldList, FormField
from wtforms.validators import DataRequired
from flask_wtf.file import FileField, FileAllowed
from wtforms import SubmitField

class UploadForm(FlaskForm):
    sofie_file = FileField('Sofie form', validators=[FileAllowed(['pdf'])])
    topdesk_file = FileField('Topdesk form', validators=[FileAllowed(['pdf'])])
    submit = SubmitField('Upload')

class DateRangeForm(FlaskForm):
    start_date = StringField('Start Date', validators=[DataRequired()])
    end_date = StringField('End Date', validators=[DataRequired()])
    
class ContactInfoForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired()])
    phone = StringField('Phone')
    address = StringField('Address')

class MainForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    date_ranges = FieldList(FormField(DateRangeForm), min_entries=0)
    contacts = FieldList(FormField(ContactInfoForm), min_entries=0)