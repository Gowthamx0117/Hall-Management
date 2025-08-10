from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, IntegerField, DateTimeLocalField, SelectField
from wtforms.validators import DataRequired, Email, NumberRange, Length
from wtforms.widgets import TextArea

class HallForm(FlaskForm):
    """Form for adding/editing halls"""
    name = StringField('Hall Name', validators=[
        DataRequired(message='Hall name is required'),
        Length(min=2, max=100, message='Hall name must be between 2 and 100 characters')
    ])
    capacity = IntegerField('Capacity', validators=[
        DataRequired(message='Capacity is required'),
        NumberRange(min=1, max=10000, message='Capacity must be between 1 and 10,000')
    ])
    location = StringField('Location', validators=[
        DataRequired(message='Location is required'),
        Length(min=2, max=200, message='Location must be between 2 and 200 characters')
    ])
    description = TextAreaField('Description', validators=[
        Length(max=1000, message='Description cannot exceed 1000 characters')
    ])

class BookingForm(FlaskForm):
    """Form for booking halls"""
    student_name = StringField('Your Name', validators=[
        DataRequired(message='Name is required'),
        Length(min=2, max=100, message='Name must be between 2 and 100 characters')
    ])
    department = StringField('Department', validators=[
        DataRequired(message='Department is required'),
        Length(min=2, max=100, message='Department must be between 2 and 100 characters')
    ])
    purpose = TextAreaField('Purpose of Booking', validators=[
        DataRequired(message='Purpose is required'),
        Length(min=10, max=1000, message='Purpose must be between 10 and 1000 characters')
    ])
    booking_date = DateTimeLocalField('Date & Time', validators=[
        DataRequired(message='Date and time are required')
    ])

class SettingsForm(FlaskForm):
    """Form for application settings"""
    college_name = StringField('College Name', validators=[
        DataRequired(message='College name is required'),
        Length(min=2, max=200, message='College name must be between 2 and 200 characters')
    ])
    college_logo_url = StringField('College Logo URL (optional)', validators=[
        Length(max=500, message='Logo URL cannot exceed 500 characters')
    ])
    admin_emails = TextAreaField('Admin Email Addresses (comma-separated)', validators=[
        DataRequired(message='At least one admin email is required'),
        Length(min=5, max=1000, message='Email addresses field must be between 5 and 1000 characters')
    ])
