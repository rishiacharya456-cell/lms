import firebase_admin
from firebase_admin import credentials
from django.conf import settings
import os


def initialize_firebase():
    try:
        if not firebase_admin._apps:

            firebase_path = os.path.join(settings.BASE_DIR, "firebase.json")

            print("PATH:", firebase_path)
            print("EXISTS:", os.path.exists(firebase_path))

            cred = credentials.Certificate(firebase_path)
            firebase_admin.initialize_app(cred)

            print("🔥 Firebase initialized successfully")

    except Exception as e:
        print("❌ Firebase init error:", str(e))