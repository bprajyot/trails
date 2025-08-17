import re
from marshmallow import ValidationError

def validate_email(email):
    """Validate email format."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, email):
        raise ValidationError('Invalid email format')
    return email

def validate_password(password):
    """Validate password strength."""
    if len(password) < 6:
        raise ValidationError('Password must be at least 6 characters long')
    
    if len(password) > 128:
        raise ValidationError('Password must be less than 128 characters')
    
    # Optional: Add more password strength requirements
    # if not re.search(r'[A-Z]', password):
    #     raise ValidationError('Password must contain at least one uppercase letter')
    # 
    # if not re.search(r'[a-z]', password):
    #     raise ValidationError('Password must contain at least one lowercase letter')
    # 
    # if not re.search(r'\d', password):
    #     raise ValidationError('Password must contain at least one digit')
    
    return password

def validate_username(username):
    """Validate username format."""
    if len(username) < 3:
        raise ValidationError('Username must be at least 3 characters long')
    
    if len(username) > 50:
        raise ValidationError('Username must be less than 50 characters')
    
    if not re.match(r'^[a-zA-Z0-9_-]+$', username):
        raise ValidationError('Username can only contain letters, numbers, underscores, and hyphens')
    
    return username

def validate_problem_title(title):
    """Validate problem title."""
    if not title or len(title.strip()) < 3:
        raise ValidationError('Problem title must be at least 3 characters long')
    
    if len(title) > 200:
        raise ValidationError('Problem title must be less than 200 characters')
    
    return title.strip()

def validate_problem_difficulty(difficulty):
    """Validate problem difficulty."""
    valid_difficulties = ['Easy', 'Medium', 'Hard']
    if difficulty not in valid_difficulties:
        raise ValidationError(f'Difficulty must be one of: {", ".join(valid_difficulties)}')
    
    return difficulty

def validate_programming_language(language):
    """Validate programming language."""
    valid_languages = ['python', 'javascript', 'java', 'cpp', 'go']
    if language not in valid_languages:
        raise ValidationError(f'Language must be one of: {", ".join(valid_languages)}')
    
    return language

def validate_code_length(code):
    """Validate code length."""
    if not code or len(code.strip()) < 1:
        raise ValidationError('Code cannot be empty')
    
    if len(code) > 100000:  # 100KB limit
        raise ValidationError('Code is too long (maximum 100KB)')
    
    return code

def validate_contest_dates(start_time, end_time):
    """Validate contest start and end times."""
    from datetime import datetime
    
    if start_time >= end_time:
        raise ValidationError('Contest start time must be before end time')
    
    if start_time < datetime.utcnow():
        raise ValidationError('Contest start time must be in the future')
    
    # Maximum contest duration: 7 days
    max_duration = 7 * 24 * 60 * 60  # 7 days in seconds
    if (end_time - start_time).total_seconds() > max_duration:
        raise ValidationError('Contest duration cannot exceed 7 days')
    
    return start_time, end_time

def sanitize_html(text):
    """Basic HTML sanitization."""
    if not text:
        return text
    
    # Remove potentially dangerous HTML tags
    dangerous_tags = ['script', 'iframe', 'object', 'embed', 'form', 'input']
    for tag in dangerous_tags:
        text = re.sub(f'<{tag}[^>]*>.*?</{tag}>', '', text, flags=re.IGNORECASE | re.DOTALL)
        text = re.sub(f'<{tag}[^>]*/?>', '', text, flags=re.IGNORECASE)
    
    return text

def validate_pagination(page, per_page, max_per_page=100):
    """Validate pagination parameters."""
    try:
        page = int(page) if page else 1
        per_page = int(per_page) if per_page else 20
    except (ValueError, TypeError):
        raise ValidationError('Page and per_page must be integers')
    
    if page < 1:
        raise ValidationError('Page must be greater than 0')
    
    if per_page < 1:
        raise ValidationError('Per page must be greater than 0')
    
    if per_page > max_per_page:
        raise ValidationError(f'Per page cannot exceed {max_per_page}')
    
    return page, per_page