"""
Firebase Authentication module for validating ID tokens from Unity clients.
"""
import os
from functools import wraps
from flask import request, jsonify, g
import firebase_admin
from firebase_admin import credentials, auth

# Initialize Firebase Admin SDK
_firebase_app = None

def init_firebase():
    """
    Initialize Firebase Admin SDK.
    Can be initialized with:
    1. Service account JSON file (FIREBASE_CREDENTIALS_PATH)
    2. Service account JSON content (FIREBASE_CREDENTIALS_JSON)
    3. Default credentials (for GCP environments)
    """
    global _firebase_app
    
    if _firebase_app is not None:
        return _firebase_app
    
    try:
        # Option 1: Path to service account JSON file
        cred_path = os.getenv('FIREBASE_CREDENTIALS_PATH')
        if cred_path and os.path.exists(cred_path):
            cred = credentials.Certificate(cred_path)
            _firebase_app = firebase_admin.initialize_app(cred)
            return _firebase_app
        
        # Option 2: Service account JSON as string (useful for Docker secrets)
        cred_json = os.getenv('FIREBASE_CREDENTIALS_JSON')
        if cred_json:
            import json
            cred_dict = json.loads(cred_json)
            cred = credentials.Certificate(cred_dict)
            _firebase_app = firebase_admin.initialize_app(cred)
            return _firebase_app
        
        # Option 3: Default credentials (for GCP environments)
        _firebase_app = firebase_admin.initialize_app()
        return _firebase_app
        
    except Exception as e:
        raise Exception(f"Failed to initialize Firebase: {str(e)}. "
                       f"Set FIREBASE_CREDENTIALS_PATH or FIREBASE_CREDENTIALS_JSON environment variable.")


def verify_firebase_token(token: str):
    """
    Verify a Firebase ID token and return the decoded token.
    
    Args:
        token: Firebase ID token string
        
    Returns:
        dict: Decoded token containing user info (uid, email, etc.)
        
    Raises:
        ValueError: If token is invalid or expired
    """
    if _firebase_app is None:
        init_firebase()
    
    try:
        decoded_token = auth.verify_id_token(token)
        return decoded_token
    except auth.InvalidIdTokenError:
        raise ValueError("Invalid ID token")
    except auth.ExpiredIdTokenError:
        raise ValueError("Expired ID token")
    except Exception as e:
        raise ValueError(f"Token verification failed: {str(e)}")


def get_firebase_user_from_request():
    """
    Extract and verify Firebase token from request headers.
    Expects token in 'Authorization' header as 'Bearer <token>'
    
    Returns:
        dict: Decoded token with user info
        
    Raises:
        ValueError: If token is missing or invalid
    """
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        raise ValueError("Missing Authorization header")
    
    try:
        scheme, token = auth_header.split(' ', 1)
        if scheme.lower() != 'bearer':
            raise ValueError("Authorization header must be 'Bearer <token>'")
    except ValueError:
        raise ValueError("Invalid Authorization header format")
    
    return verify_firebase_token(token)


def require_firebase_auth(f):
    """
    Decorator to require Firebase authentication for a route.
    Validates the Firebase ID token and stores user info in Flask's g object.
    
    Usage:
        @api_bp.route('/protected')
        @require_firebase_auth
        def protected_route():
            user_id = g.firebase_user['uid']
            ...
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            decoded_token = get_firebase_user_from_request()
            # Store user info in Flask's g for use in route handlers
            g.firebase_user = decoded_token
            g.firebase_uid = decoded_token['uid']
            return f(*args, **kwargs)
        except ValueError as e:
            return jsonify({"error": str(e)}), 401
        except Exception as e:
            return jsonify({"error": f"Authentication error: {str(e)}"}), 401
    
    return decorated_function

