from app import db
from datetime import datetime
from sqlalchemy import String, Integer, Text, DateTime, Boolean

class Hall(db.Model):
    """Model for managing college halls"""
    id = db.Column(Integer, primary_key=True)
    name = db.Column(String(100), nullable=False, unique=True)
    capacity = db.Column(Integer, nullable=False)
    location = db.Column(String(200), nullable=False)
    description = db.Column(Text)
    is_available = db.Column(Boolean, default=True, nullable=False)
    created_at = db.Column(DateTime, default=datetime.utcnow)

    # Relationship with bookings
    bookings = db.relationship('Booking', backref='hall', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Hall {self.name}>'

class Booking(db.Model):
    """Model for managing hall bookings"""
    id = db.Column(Integer, primary_key=True)
    hall_id = db.Column(Integer, db.ForeignKey('hall.id'), nullable=False)
    student_name = db.Column(String(100), nullable=False)
    department = db.Column(String(100), nullable=False)
    purpose = db.Column(Text, nullable=False)
    booking_date = db.Column(DateTime, nullable=False)
    created_at = db.Column(DateTime, default=datetime.utcnow)
    status = db.Column(String(20), default='active', nullable=False)  # active, cancelled

    def __repr__(self):
        return f'<Booking {self.student_name}>'

class Settings(db.Model):
    """Model for storing application settings"""
    id = db.Column(Integer, primary_key=True)
    college_name = db.Column(String(200), default='College Name')
    college_logo_url = db.Column(String(500))
    admin_emails = db.Column(Text)  # Comma-separated email addresses
    is_setup_complete = db.Column(Boolean, default=False)
    created_at = db.Column(DateTime, default=datetime.utcnow)
    updated_at = db.Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    @property
    def email_list(self):
        """Return list of admin emails"""
        if self.admin_emails:
            return [email.strip() for email in self.admin_emails.split(',')]
        return []

    def __repr__(self):
        return f'<Settings {self.college_name}>'
