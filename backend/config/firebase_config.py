import firebase_admin
from firebase_admin import credentials
import os

def initialize_firebase():
    """Initialize Firebase Admin SDK"""
    try:
        # Look for service account key in APPDATA
        service_account_path = os.path.join(os.getenv('APPDATA'), 'accounting_software', 'serviceAccountKey.json')
        
        if not os.path.exists(service_account_path):
            raise FileNotFoundError(
                f"Firebase service account key not found at {service_account_path}. "
                "Please place your serviceAccountKey.json in this location."
            )
            
        cred = credentials.Certificate(service_account_path)
        firebase_admin.initialize_app(cred)
        print("Firebase initialized successfully")
    except Exception as e:
        print(f"Error initializing Firebase: {str(e)}")
        raise e
