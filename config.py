import os

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "change-me-in-prod")
    API_URL    = os.environ.get("API_URL", "")
