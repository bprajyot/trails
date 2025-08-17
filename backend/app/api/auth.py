from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import (
    create_access_token, create_refresh_token, 
    jwt_required, get_jwt_identity, get_jwt
)
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from marshmallow import Schema, fields, ValidationError
from ..models.user import User, db
from ..utils.validators import validate_email, validate_password

auth_bp = Blueprint('auth', __name__)
limiter = Limiter(key_func=get_remote_address)

# Validation schemas
class RegisterSchema(Schema):
    username = fields.Str(required=True, validate=lambda x: len(x) >= 3 and len(x) <= 50)
    email = fields.Email(required=True)
    password = fields.Str(required=True, validate=lambda x: len(x) >= 6)
    first_name = fields.Str(required=False, validate=lambda x: len(x) <= 50)
    last_name = fields.Str(required=False, validate=lambda x: len(x) <= 50)

class LoginSchema(Schema):
    username = fields.Str(required=True)
    password = fields.Str(required=True)

class ChangePasswordSchema(Schema):
    current_password = fields.Str(required=True)
    new_password = fields.Str(required=True, validate=lambda x: len(x) >= 6)

# Token blacklist (in production, use Redis)
blacklisted_tokens = set()

@auth_bp.route('/register', methods=['POST'])
@limiter.limit("5 per minute")
def register():
    """Register a new user."""
    try:
        schema = RegisterSchema()
        data = schema.load(request.get_json() or {})
    except ValidationError as err:
        return {'error': 'Validation failed', 'messages': err.messages}, 400
    
    # Check if username already exists
    if User.find_by_username(data['username']):
        return {'error': 'Username already exists'}, 400
    
    # Check if email already exists
    if User.find_by_email(data['email']):
        return {'error': 'Email already registered'}, 400
    
    try:
        # Create new user
        user = User.create_user(
            username=data['username'],
            email=data['email'],
            password=data['password'],
            first_name=data.get('first_name'),
            last_name=data.get('last_name')
        )
        
        # Create tokens
        access_token = create_access_token(identity=user.id)
        refresh_token = create_refresh_token(identity=user.id)
        
        return {
            'message': 'User registered successfully',
            'user': user.to_dict(),
            'access_token': access_token,
            'refresh_token': refresh_token
        }, 201
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Registration error: {str(e)}")
        return {'error': 'Registration failed'}, 500

@auth_bp.route('/login', methods=['POST'])
@limiter.limit("10 per minute")
def login():
    """Authenticate user and return tokens."""
    try:
        schema = LoginSchema()
        data = schema.load(request.get_json() or {})
    except ValidationError as err:
        return {'error': 'Validation failed', 'messages': err.messages}, 400
    
    # Find user by username or email
    user = User.find_by_username(data['username'])
    if not user:
        user = User.find_by_email(data['username'])
    
    # Verify credentials
    if not user or not user.check_password(data['password']):
        return {'error': 'Invalid credentials'}, 401
    
    if not user.is_active:
        return {'error': 'Account is deactivated'}, 401
    
    # Create tokens
    access_token = create_access_token(identity=user.id)
    refresh_token = create_refresh_token(identity=user.id)
    
    return {
        'message': 'Login successful',
        'user': user.to_dict(include_sensitive=True),
        'access_token': access_token,
        'refresh_token': refresh_token
    }

@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """Logout user by blacklisting token."""
    jti = get_jwt()['jti']
    blacklisted_tokens.add(jti)
    
    return {'message': 'Successfully logged out'}

@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """Refresh access token."""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user or not user.is_active:
        return {'error': 'User not found or inactive'}, 404
    
    new_token = create_access_token(identity=current_user_id)
    return {'access_token': new_token}

@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """Get current user information."""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        return {'error': 'User not found'}, 404
    
    return {'user': user.to_dict(include_sensitive=True)}

@auth_bp.route('/me', methods=['PUT'])
@jwt_required()
def update_profile():
    """Update user profile."""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        return {'error': 'User not found'}, 404
    
    data = request.get_json() or {}
    
    # Update allowed fields
    if 'first_name' in data:
        user.first_name = data['first_name'][:50] if data['first_name'] else None
    
    if 'last_name' in data:
        user.last_name = data['last_name'][:50] if data['last_name'] else None
    
    if 'email' in data:
        # Check if new email is already taken by another user
        existing_user = User.find_by_email(data['email'])
        if existing_user and existing_user.id != user.id:
            return {'error': 'Email already registered'}, 400
        user.email = data['email']
    
    try:
        db.session.commit()
        return {
            'message': 'Profile updated successfully',
            'user': user.to_dict(include_sensitive=True)
        }
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Profile update error: {str(e)}")
        return {'error': 'Profile update failed'}, 500

@auth_bp.route('/change-password', methods=['POST'])
@jwt_required()
def change_password():
    """Change user password."""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        return {'error': 'User not found'}, 404
    
    try:
        schema = ChangePasswordSchema()
        data = schema.load(request.get_json() or {})
    except ValidationError as err:
        return {'error': 'Validation failed', 'messages': err.messages}, 400
    
    # Verify current password
    if not user.check_password(data['current_password']):
        return {'error': 'Current password is incorrect'}, 400
    
    # Update password
    user.set_password(data['new_password'])
    
    try:
        db.session.commit()
        return {'message': 'Password changed successfully'}
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Password change error: {str(e)}")
        return {'error': 'Password change failed'}, 500

@auth_bp.route('/verify-token', methods=['POST'])
@jwt_required()
def verify_token():
    """Verify if token is valid."""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user or not user.is_active:
        return {'error': 'Invalid token'}, 401
    
    return {'valid': True, 'user_id': current_user_id}

# Token blacklist checker
@auth_bp.before_app_request
def check_if_token_revoked():
    """Check if token is blacklisted."""
    try:
        jti = get_jwt()['jti']
        return jti in blacklisted_tokens
    except:
        return False