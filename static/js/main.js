// Main JavaScript file for Hall Management System

document.addEventListener('DOMContentLoaded', function() {
    console.log('Hall Management System initialized');
    
    // Initialize tooltips
    initializeTooltips();
    
    // Initialize form validation
    initializeFormValidation();
    
    // Initialize auto-refresh functionality
    initializeAutoRefresh();
    
    // Initialize modal handlers
    initializeModals();
});

/**
 * Initialize Bootstrap tooltips
 */
function initializeTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

/**
 * Initialize form validation
 */
function initializeFormValidation() {
    const forms = document.querySelectorAll('.needs-validation');
    
    Array.prototype.slice.call(forms).forEach(function(form) {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        }, false);
    });
    
    // Real-time validation for specific fields
    const emailFields = document.querySelectorAll('input[type="email"]');
    emailFields.forEach(function(field) {
        field.addEventListener('blur', validateEmail);
    });
    
    const dateFields = document.querySelectorAll('input[type="datetime-local"]');
    dateFields.forEach(function(field) {
        field.addEventListener('change', validateBookingDate);
    });
}

/**
 * Validate email format
 */
function validateEmail(event) {
    const email = event.target.value;
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    
    if (email && !emailRegex.test(email)) {
        event.target.setCustomValidity('Please enter a valid email address');
    } else {
        event.target.setCustomValidity('');
    }
}

/**
 * Validate booking date (must be at least 2 hours in future)
 */
function validateBookingDate(event) {
    const selectedDate = new Date(event.target.value);
    const minDate = new Date();
    minDate.setHours(minDate.getHours() + 2);
    
    if (selectedDate <= minDate) {
        event.target.setCustomValidity('Booking must be at least 2 hours in advance');
        showAlert('Booking must be at least 2 hours in advance', 'warning');
    } else {
        event.target.setCustomValidity('');
    }
}

/**
 * Initialize auto-refresh functionality
 */
function initializeAutoRefresh() {
    // Only auto-refresh on dashboard
    if (window.location.pathname === '/' || window.location.pathname === '/dashboard') {
        // Auto-refresh every 5 minutes
        setInterval(function() {
            console.log('Auto-refreshing hall status...');
            refreshHallStatus();
        }, 300000); // 5 minutes
    }
}

/**
 * Refresh hall status via AJAX
 */
function refreshHallStatus() {
    fetch('/api/halls')
        .then(response => response.json())
        .then(data => {
            updateHallCards(data);
            console.log('Hall status updated');
        })
        .catch(error => {
            console.error('Error refreshing hall status:', error);
        });
}

/**
 * Update hall cards with new data
 */
function updateHallCards(halls) {
    halls.forEach(function(hall) {
        const hallCard = document.querySelector(`[data-hall-id="${hall.id}"]`);
        if (hallCard) {
            const statusBadge = hallCard.querySelector('.badge');
            const bookButton = hallCard.querySelector('.btn');
            
            if (hall.is_available) {
                statusBadge.className = 'badge bg-success';
                statusBadge.innerHTML = '<i class="fas fa-check me-1"></i>Available';
                if (bookButton) {
                    bookButton.className = 'btn btn-success w-100';
                    bookButton.innerHTML = '<i class="fas fa-calendar-plus me-1"></i>Book Now';
                    bookButton.disabled = false;
                }
            } else {
                statusBadge.className = 'badge bg-danger';
                statusBadge.innerHTML = '<i class="fas fa-times me-1"></i>Booked';
                if (bookButton) {
                    bookButton.className = 'btn btn-secondary w-100';
                    bookButton.innerHTML = '<i class="fas fa-ban me-1"></i>Currently Booked';
                    bookButton.disabled = true;
                }
            }
        }
    });
}

/**
 * Initialize modal handlers
 */
function initializeModals() {
    // Clear form data when modals are hidden
    const modals = document.querySelectorAll('.modal');
    modals.forEach(function(modal) {
        modal.addEventListener('hidden.bs.modal', function() {
            const forms = modal.querySelectorAll('form');
            forms.forEach(function(form) {
                form.reset();
                form.classList.remove('was-validated');
            });
        });
    });
}

/**
 * Show alert message
 */
function showAlert(message, type = 'info') {
    const alertContainer = document.querySelector('.container');
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.innerHTML = `
        <i class="fas fa-info-circle me-2"></i>
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    alertContainer.insertBefore(alertDiv, alertContainer.firstChild);
    
    // Auto-dismiss after 5 seconds
    setTimeout(function() {
        if (alertDiv.parentNode) {
            alertDiv.remove();
        }
    }, 5000);
}

/**
 * Confirm action with custom message
 */
function confirmAction(message, callback) {
    if (confirm(message)) {
        callback();
    }
}

/**
 * Show loading state for buttons
 */
function showButtonLoading(button, originalText) {
    button.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i>Loading...';
    button.disabled = true;
    button.dataset.originalText = originalText;
}

/**
 * Hide loading state for buttons
 */
function hideButtonLoading(button) {
    const originalText = button.dataset.originalText || 'Submit';
    button.innerHTML = originalText;
    button.disabled = false;
}

/**
 * Format date for display
 */
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

/**
 * Validate form data before submission
 */
function validateFormData(form) {
    const requiredFields = form.querySelectorAll('[required]');
    let isValid = true;
    
    requiredFields.forEach(function(field) {
        if (!field.value.trim()) {
            field.classList.add('is-invalid');
            isValid = false;
        } else {
            field.classList.remove('is-invalid');
        }
    });
    
    return isValid;
}

/**
 * Handle AJAX form submission
 */
function submitFormAjax(form, successCallback, errorCallback) {
    const formData = new FormData(form);
    const submitButton = form.querySelector('button[type="submit"]');
    const originalText = submitButton.innerHTML;
    
    showButtonLoading(submitButton, originalText);
    
    fetch(form.action, {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        hideButtonLoading(submitButton);
        if (data.success) {
            if (successCallback) successCallback(data);
        } else {
            if (errorCallback) errorCallback(data);
        }
    })
    .catch(error => {
        hideButtonLoading(submitButton);
        console.error('Form submission error:', error);
        if (errorCallback) errorCallback({ error: 'Network error occurred' });
    });
}

// Export functions for global use
window.HallManagement = {
    showAlert,
    confirmAction,
    showButtonLoading,
    hideButtonLoading,
    formatDate,
    validateFormData,
    submitFormAjax,
    refreshHallStatus
};
