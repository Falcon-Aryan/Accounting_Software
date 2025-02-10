"""Session management module to handle server-side session storage"""

# Server-side session store that gets cleared on server restart
active_sessions = set()

def add_session(session_id):
    """Add a session ID to the active sessions store"""
    active_sessions.add(session_id)

def remove_session(session_id):
    """Remove a session ID from the active sessions store"""
    active_sessions.discard(session_id)  # Using discard instead of remove to avoid KeyError

def is_session_active(session_id):
    """Check if a session ID exists in the active sessions store"""
    return session_id in active_sessions
