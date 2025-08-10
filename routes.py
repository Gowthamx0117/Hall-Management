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
    return render_template('dashboard.html', halls=halls, settings=settings)

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
    """Book a specific hall"""
    hall = Hall.query.get_or_404(hall_id)
    settings = Settings.query.first()
    
    if not hall.is_available:
        flash('This hall is currently not available for booking.', 'warning')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        form = BookingForm()
        if form.validate_on_submit():
            # Check if booking date is in the future
            if form.booking_date.data and form.booking_date.data <= datetime.now():
                flash('Booking date must be in the future.', 'danger')
                return render_template('booking.html', hall=hall, form=form, settings=settings)
            
            booking = Booking()
            booking.hall_id = hall.id
            booking.student_name = form.student_name.data
            booking.department = form.department.data
            booking.purpose = form.purpose.data
            booking.booking_date = form.booking_date.data
            
            # Mark hall as unavailable
            hall.is_available = False
            
            try:
                db.session.add(booking)
                db.session.commit()
                
                # Send email notification
                send_booking_notification(booking)
                
                flash(f'Hall "{hall.name}" booked successfully!', 'success')
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
    from datetime import datetime
    return render_template('booking.html', hall=hall, form=form, settings=settings, now=datetime.now())

@app.route('/admin/booking/<int:booking_id>/cancel', methods=['POST'])
def cancel_booking(booking_id):
    """Cancel a booking and make hall available again"""
    booking = Booking.query.get_or_404(booking_id)
    hall = booking.hall
    
    try:
        booking.status = 'cancelled'
        hall.is_available = True
        db.session.commit()
        flash(f'Booking for "{hall.name}" cancelled successfully!', 'success')
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
        
        subject = f'New Hall Booking - {booking.hall.name}'
        
        body = f"""
        New hall booking received:
        
        Hall: {booking.hall.name}
        Student: {booking.student_name}
        Department: {booking.department}
        Purpose: {booking.purpose}
        Date & Time: {booking.booking_date.strftime('%Y-%m-%d %H:%M')}
        Booking Time: {booking.created_at.strftime('%Y-%m-%d %H:%M')}
        
        Please review the booking in the admin panel.
        
        Best regards,
        {settings.college_name} Hall Management System
        """
        
        msg = Message(
            subject=subject,
            recipients=settings.email_list,
            body=body
        )
        
        mail.send(msg)
        logging.info(f'Booking notification sent for booking ID: {booking.id}')
        
    except Exception as e:
        logging.error(f'Failed to send booking notification: {str(e)}')

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
