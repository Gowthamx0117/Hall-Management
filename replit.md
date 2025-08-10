# Hall Management System

## Overview

A Flask-based web application for managing college hall bookings. The system allows administrators to add and manage halls while enabling students to book available halls for events and activities. Features include real-time availability tracking, email notifications, and a responsive dashboard interface.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture
- **Template Engine**: Jinja2 templates with Bootstrap 5 for responsive UI
- **Styling**: Custom CSS with dark theme support and hover effects
- **JavaScript**: Vanilla JavaScript for form validation, tooltips, and auto-refresh functionality
- **UI Framework**: Bootstrap 5 with Font Awesome icons for consistent design

### Backend Architecture
- **Web Framework**: Flask with modular route organization
- **Database ORM**: SQLAlchemy with declarative base model
- **Form Handling**: Flask-WTF with comprehensive validation
- **Email System**: Flask-Mail for booking notifications
- **Session Management**: Flask sessions with configurable secret keys

### Data Models
- **Hall Model**: Manages hall information (name, capacity, location, availability)
- **Booking Model**: Tracks student bookings with foreign key relationships
- **Settings Model**: Stores application configuration and admin preferences
- **Database Relationships**: One-to-many between halls and bookings with cascade deletion

### Authentication & Authorization
- **Admin Access**: Simple admin panel without complex user authentication
- **Setup Process**: Initial configuration wizard for system setup
- **Email Configuration**: SMTP integration for automated notifications

### Application Flow
- **Setup-First Design**: Redirects to setup page if configuration incomplete
- **Dashboard-Centric**: Main interface shows all halls with real-time availability
- **Modal-Based Interactions**: Uses Bootstrap modals for adding halls and bookings
- **Form Validation**: Client-side and server-side validation with user feedback

## External Dependencies

### Core Dependencies
- **Flask**: Web application framework
- **SQLAlchemy**: Database ORM and migrations
- **Flask-Mail**: Email functionality for notifications
- **Flask-WTF**: Form handling and CSRF protection
- **WTForms**: Form validation and rendering

### Frontend Libraries
- **Bootstrap 5**: CSS framework with dark theme support
- **Font Awesome 6**: Icon library for UI elements
- **Vanilla JavaScript**: No additional JS frameworks

### Database
- **SQLite**: Default database for development (configurable via DATABASE_URL)
- **PostgreSQL Ready**: Can be configured for production deployment

### Email Services
- **SMTP Configuration**: Supports Gmail and other SMTP providers
- **Environment Variables**: Configurable email settings for different environments

### Development Tools
- **Werkzeug ProxyFix**: Production deployment support
- **Python Logging**: Debug and error tracking
- **Environment Variables**: Configuration management for different environments