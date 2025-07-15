import os

DEBUG = True
SECRET_KEY = os.getenv("SECRET_KEY", "default-secret")
