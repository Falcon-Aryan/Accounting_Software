from functools import wraps
import os
from flask import request, jsonify
from appwrite.client import Client
from appwrite.services.users import Users
from ..users.models import User
from .session_store import is_session_active, remove_session, add_session

def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        # Get session ID and user ID from headers
        session_id = request.headers.get('X-Appwrite-Session-ID')
        user_id = request.headers.get('X-Appwrite-User-ID')
        
        if not session_id or not user_id:
            return jsonify({'error': 'Session ID and User ID are required'}), 401
            
        if not is_session_active(session_id):
            return jsonify({'error': 'Session expired or invalid'}), 401
            
        # Initialize Appwrite client
        client = Client()
        client.set_endpoint(os.getenv('APPWRITE_ENDPOINT'))
        client.set_project(os.getenv('APPWRITE_PROJECT_ID'))
        client.set_key(os.getenv('APPWRITE_API_KEY'))
        
        try:
            # Verify session using Users API
            users = Users(client)
            sessions = users.list_sessions(user_id)
            
            # Check if session exists
            session_valid = False
            for session in sessions['sessions']:
                if session['$id'] == session_id:
                    session_valid = True
                    break
                    
            if not session_valid:
                remove_session(session_id)
                return jsonify({'error': 'Invalid session'}), 401
                
            # Get user
            user = User.get_user(user_id)
            if not user:
                remove_session(session_id)
                return jsonify({'error': 'User not found'}), 401
                
            # Add session to server-side store if not already present
            add_session(session_id)
                
            # Add user to request context
            request.user = user
            return f(*args, **kwargs)
            
        except Exception as e:
            print(f"Auth error: {str(e)}")
            remove_session(session_id)
            return jsonify({'error': 'Authentication failed'}), 401
            
    return decorated
