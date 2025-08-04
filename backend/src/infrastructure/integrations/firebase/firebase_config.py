# backend/api/config/firebase_config.py
# Path: backend/api/config/firebase_config.py

import firebase_admin
from firebase_admin import credentials, auth
from functools import lru_cache
from .settings import get_settings
import json

settings = get_settings()

@lru_cache()
def initialize_firebase():
    """Initialize Firebase Admin SDK"""
    if not firebase_admin._apps:
        if settings.firebase_admin_sdk_path:
            # Use service account file
            cred = credentials.Certificate(settings.firebase_admin_sdk_path)
        else:
            # Use environment variables
            cred_dict = {
                "type": "service_account",
                "project_id": settings.firebase_project_id,
                "private_key_id": "key-id",
                "private_key": "-----BEGIN PRIVATE KEY-----\\n...\\n-----END PRIVATE KEY-----\\n",
                "client_email": f"firebase-adminsdk@{settings.firebase_project_id}.iam.gserviceaccount.com",
                "client_id": "client-id",
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs"
            }
            cred = credentials.Certificate(cred_dict)
        
        firebase_admin.initialize_app(cred)
    
    return firebase_admin.get_app()

def verify_token(id_token: str):
    """Verify Firebase ID token"""
    try:
        initialize_firebase()
        decoded_token = auth.verify_id_token(id_token)
        return decoded_token
    except Exception as e:
        raise ValueError(f"Invalid token: {e}")

def test_auth():
    """Test Firebase authentication setup"""
    try:
        initialize_firebase()
        print("✅ Firebase Auth initialized successfully")
        return True
    except Exception as e:
        print(f"❌ Firebase Auth initialization failed: {e}")
        return False