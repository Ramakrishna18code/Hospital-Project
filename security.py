"""
Authentication and Security utilities
"""

from functools import wraps
from flask import session, jsonify
import logging

logger = logging.getLogger(__name__)

def login_required(f):
    """Decorator to require user login"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Authentication required'}), 401
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    """Decorator to require admin role"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Authentication required'}), 401
        
        from models import User
        user = User.query.get(session['user_id'])
        
        if not user or user.role != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        
        return f(*args, **kwargs)
    return decorated_function


def validate_input(required_fields):
    """Decorator to validate required input fields"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            from flask import request
            data = request.get_json()
            
            if not data:
                return jsonify({'error': 'Request body required'}), 400
            
            missing_fields = [field for field in required_fields if field not in data]
            
            if missing_fields:
                return jsonify({
                    'error': 'Missing required fields',
                    'missing': missing_fields
                }), 400
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def rate_limit(max_requests=100, window_seconds=3600):
    """Rate limiting decorator"""
    from flask import request
    from datetime import datetime, timedelta
    
    request_times = {}
    
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            user_id = session.get('user_id', 'anonymous')
            current_time = datetime.utcnow()
            
            if user_id not in request_times:
                request_times[user_id] = []
            
            # Remove old requests outside the window
            cutoff_time = current_time - timedelta(seconds=window_seconds)
            request_times[user_id] = [
                req_time for req_time in request_times[user_id]
                if req_time > cutoff_time
            ]
            
            # Check if limit exceeded
            if len(request_times[user_id]) >= max_requests:
                logger.warning(f"Rate limit exceeded for user {user_id}")
                return jsonify({'error': 'Rate limit exceeded'}), 429
            
            # Record this request
            request_times[user_id].append(current_time)
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def sanitize_input(data):
    """Sanitize user input to prevent injection attacks"""
    if isinstance(data, str):
        # Remove potentially dangerous characters
        dangerous_chars = ['<', '>', '"', "'", ';', '&', '|']
        for char in dangerous_chars:
            data = data.replace(char, '')
        return data.strip()
    elif isinstance(data, dict):
        return {k: sanitize_input(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [sanitize_input(item) for item in data]
    return data


def log_activity(activity_type, details):
    """Log important activities for audit trail"""
    try:
        from models import User
        user_id = session.get('user_id')
        user = User.query.get(user_id) if user_id else None
        
        log_message = f"[{activity_type}] User: {user.email if user else 'Unknown'} | Details: {details}"
        logger.info(log_message)
    
    except Exception as e:
        logger.error(f"Error logging activity: {str(e)}")
