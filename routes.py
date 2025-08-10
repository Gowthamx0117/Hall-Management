from flask import render_template, request, redirect, url_for, flash, jsonify
from flask_mail import Message
from app import app, db, mail
from models import Hall, Booking, Settings
from forms import HallForm, BookingForm, SettingsForm
from datetime import datetime
import logging

@app.route('/')
def index():
    """Main dashboard showing all halls and their availability"""
    # Check if setup is complete
    settings = Settings.query.first()
    if not settings or not settings.is_setup_complete:
        return redirect(url_for('setup'))
    
    halls = Hall.query.all()
    # Get today's bookings for each hall
    from datetime import date
    today = date.today()
    hall_bookings = {}
    
    for hall in halls:
        today_bookings = Booking.query.filter(
            Booking.hall_id == hall.id,
            Booking.booking_date == today,
            Booking.status == 'active'
        ).order_by(Booking.start_time).all()
        hall_bookings[hall.id] = today_bookings
    
    # Calculate total bookings for today
    total_bookings = sum(len(bookings) for bookings in hall_bookings.values())
    
    return render_template('dashboard.html', halls=halls, settings=settings, hall_bookings=hall_bookings, today=today, total_bookings=total_bookings)

@app.route('/setup', methods=['GET', 'POST'])
def setup():
    """Initial setup page for admin configuration"""
    settings = Settings.query.first()
    
    if request.method == 'POST':
        form = SettingsForm()
        if form.validate_on_submit():
            # Create or update settings
            if not settings:
                settings = Settings()
                db.session.add(settings)
            
            settings.college_name = form.college_name.data
            settings.college_logo_url = form.college_logo_url.data
            settings.admin_emails = form.admin_emails.data
            settings.is_setup_complete = True
            
            try:
                db.session.commit()
                flash('Setup completed successfully!', 'success')
                return redirect(url_for('admin'))
            except Exception as e:
                db.session.rollback()
                flash(f'Error saving settings: {str(e)}', 'danger')
                logging.error(f'Setup error: {str(e)}')
        else:
            # Show form validation errors
            for field, errors in form.errors.items():
                for error in errors:
                    flash(f'{field}: {error}', 'danger')
    
    form = SettingsForm()
    if settings:
        form.college_name.data = settings.college_name
        form.college_logo_url.data = settings.college_logo_url
        form.admin_emails.data = settings.admin_emails
    
    return render_template('setup.html', form=form)

@app.route('/admin')
def admin():
    """Admin panel for managing halls and settings"""
    settings = Settings.query.first()
    if not settings or not settings.is_setup_complete:
        return redirect(url_for('setup'))
    
    halls = Hall.query.all()
    recent_bookings = Booking.query.order_by(Booking.created_at.desc()).limit(10).all()
    
    return render_template('admin.html', halls=halls, bookings=recent_bookings, settings=settings)

@app.route('/admin/hall/add', methods=['GET', 'POST'])
def add_hall():
    """Add new hall"""
    if request.method == 'POST':
        # Get form data directly from request
        name = request.form.get('name')
        capacity = request.form.get('capacity')
        location = request.form.get('location')
        description = request.form.get('description')
        
        # Basic validation
        if not name or not capacity or not location:
            flash('All required fields must be filled!', 'danger')
            return redirect(url_for('admin'))
        
        try:
            capacity = int(capacity)
        except ValueError:
            flash('Capacity must be a valid number!', 'danger')
            return redirect(url_for('admin'))
        
        # Check if hall name already exists
        existing_hall = Hall.query.filter_by(name=name).first()
        if existing_hall:
            flash('A hall with this name already exists!', 'danger')
            return redirect(url_for('admin'))
        
        hall = Hall()
        hall.name = name
        hall.capacity = capacity
        hall.location = location
        hall.description = description
            
        try:
            db.session.add(hall)
            db.session.commit()
            flash(f'Hall "{hall.name}" added successfully!', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error adding hall: {str(e)}', 'danger')
            logging.error(f'Add hall error: {str(e)}')
    
    return redirect(url_for('admin'))

@app.route('/admin/hall/<int:hall_id>/delete', methods=['POST'])
def delete_hall(hall_id):
    """Delete a hall"""
    hall = Hall.query.get_or_404(hall_id)
    
    try:
        db.session.delete(hall)
        db.session.commit()
        flash(f'Hall "{hall.name}" deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting hall: {str(e)}', 'danger')
        logging.error(f'Delete hall error: {str(e)}')
    
    return redirect(url_for('admin'))

@app.route('/book/<int:hall_id>', methods=['GET', 'POST'])
def book_hall(hall_id):
    """Book a specific hall with date and time conflict checking"""
    hall = Hall.query.get_or_404(hall_id)
    settings = Settings.query.first()
    
    if request.method == 'POST':
        form = BookingForm()
        if form.validate_on_submit():
            # Check for booking conflicts
            conflict_query = db.session.query(Booking).filter(
                Booking.hall_id == hall.id,
                Booking.booking_date == form.booking_date.data,
                Booking.status == 'active',
                Booking.start_time < form.end_time.data,
                Booking.end_time > form.start_time.data
            )
            
            existing_booking = conflict_query.first()
            
            if existing_booking:
                flash('This hall is already booked at the selected date and time. Please choose another slot.', 'danger')
                from datetime import date
                return render_template('booking.html', hall=hall, form=form, settings=settings, today=date.today())
            
            # Create new booking
            booking = Booking()
            booking.hall_id = hall.id
            booking.student_name = form.student_name.data
            booking.department = form.department.data
            booking.purpose = form.purpose.data
            booking.booking_date = form.booking_date.data
            booking.start_time = form.start_time.data
            booking.end_time = form.end_time.data
            
            try:
                db.session.add(booking)
                db.session.commit()
                
                # Send email notification
                send_booking_notification(booking)
                
                flash(f'Hall "{hall.name}" booked successfully for {form.booking_date.data} from {form.start_time.data.strftime("%H:%M")} to {form.end_time.data.strftime("%H:%M")}!', 'success')
                return redirect(url_for('index'))
            except Exception as e:
                db.session.rollback()
                flash(f'Error booking hall: {str(e)}', 'danger')
                logging.error(f'Booking error: {str(e)}')
        else:
            # Show form validation errors
            for field, errors in form.errors.items():
                for error in errors:
                    flash(f'{field}: {error}', 'danger')
    
    form = BookingForm()
    from datetime import date
    return render_template('booking.html', hall=hall, form=form, settings=settings, today=date.today())

@app.route('/admin/booking/<int:booking_id>/cancel', methods=['POST'])
def cancel_booking(booking_id):
    """Cancel a booking"""
    booking = Booking.query.get_or_404(booking_id)
    hall = booking.hall
    
    try:
        booking.status = 'cancelled'
        db.session.commit()
        flash(f'Booking for "{hall.name}" on {booking.booking_date} cancelled successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error cancelling booking: {str(e)}', 'danger')
        logging.error(f'Cancel booking error: {str(e)}')
    
    return redirect(url_for('admin'))

@app.route('/api/halls')
def api_halls():
    """API endpoint to get all halls with their status"""
    halls = Hall.query.all()
    halls_data = []
    
    for hall in halls:
        halls_data.append({
            'id': hall.id,
            'name': hall.name,
            'capacity': hall.capacity,
            'location': hall.location,
            'description': hall.description,
            'is_available': hall.is_available
        })
    
    return jsonify(halls_data)

def send_booking_notification(booking):
    """Send email notification to admin about new booking"""
    try:
        settings = Settings.query.first()
        if not settings or not settings.admin_emails:
            logging.warning('No admin emails configured for notifications')
            return
        
        # Format the booking date and time
        booking_date = booking.booking_date.strftime('%B %d, %Y')
        start_time = booking.start_time.strftime('%I:%M %p')
        end_time = booking.end_time.strftime('%I:%M %p')
        
        subject = f'Request for Hall Booking – {booking.hall.name}'
        
        body = f"""Respected Sir/Madam,

I hope this message finds you well.

I am writing to request the booking of the {booking.hall.name} at {settings.college_name} for our upcoming event scheduled on {booking_date} from {start_time} to {end_time}.

Student Details:
- Name: {booking.student_name}
- Department: {booking.department}

Event Details:
- Hall Requested: {booking.hall.name}
- Date: {booking_date}
- Time: {start_time} to {end_time}
- Duration: {((booking.end_time.hour * 60 + booking.end_time.minute) - (booking.start_time.hour * 60 + booking.start_time.minute)) // 60} hours
- Purpose: {booking.purpose}
- Hall Capacity: {booking.hall.capacity} people
- Location: {booking.hall.location}

This booking request was submitted through the Hall Management System on {booking.created_at.strftime('%B %d, %Y at %I:%M %p')}.

The hall's facilities such as projector, sound system, and seating arrangements would be essential for the smooth conduct of the program.

Kindly confirm the availability of the hall for the mentioned date and time. If approved, please let us know the necessary formalities or documents required to proceed with the booking.

Looking forward to your confirmation.

Thank you for your support and cooperation.

Regards,
{booking.student_name}
{booking.department}
Submitted via {settings.college_name} Hall Management System

---
This is an automated notification from the Hall Management System.
Please review the booking in the admin panel for further actions.
        """
        
        msg = Message(
            subject=subject,
            recipients=settings.email_list,
            body=body
        )
        
        # Try to send email, but don't fail the booking if email fails
        try:
            mail.send(msg)
            logging.info(f'Booking notification sent for booking ID: {booking.id}')
        except Exception as email_error:
            logging.error(f'Failed to send email notification: {str(email_error)}')
            # Don't raise the exception - booking should still succeed
        
    except Exception as e:
        logging.error(f'Error in send_booking_notification: {str(e)}')

@app.errorhandler(404)
def not_found_error(error):
    """Handle 404 errors"""
    flash('The requested page was not found.', 'warning')
    return redirect(url_for('index'))

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    db.session.rollback()
    flash('An internal error occurred. Please try again.', 'danger')
    logging.error(f'Internal error: {str(error)}')
    return redirect(url_for('index'))
