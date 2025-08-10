from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, IntegerField, DateField, TimeField
from wtforms.validators import DataRequired, NumberRange, Length, ValidationError
from datetime import date, time

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
    """Form for booking halls with date and time slots"""
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
    booking_date = DateField('Booking Date', validators=[
        DataRequired(message='Booking date is required')
    ])
    start_time = TimeField('Start Time', validators=[
        DataRequired(message='Start time is required')
    ])
    end_time = TimeField('End Time', validators=[
        DataRequired(message='End time is required')
    ])
    
    def validate_booking_date(self, field):
        """Validate that booking date is not in the past"""
        if field.data < date.today():
            raise ValidationError('Booking date cannot be in the past')
    
    def validate_end_time(self, field):
        """Validate that end time is after start time"""
        if self.start_time.data and field.data:
            if field.data <= self.start_time.data:
                raise ValidationError('End time must be after start time')
    
    def validate_start_time(self, field):
        """Validate minimum booking duration and working hours"""
        if field.data and self.end_time.data:
            # Check for minimum 1 hour duration
            start_minutes = field.data.hour * 60 + field.data.minute
            end_minutes = self.end_time.data.hour * 60 + self.end_time.data.minute
            duration = end_minutes - start_minutes
            
            if duration < 60:  # Less than 1 hour
                raise ValidationError('Minimum booking duration is 1 hour')
            
            if duration > 480:  # More than 8 hours
                raise ValidationError('Maximum booking duration is 8 hours')

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
