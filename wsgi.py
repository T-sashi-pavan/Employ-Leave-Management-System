import os
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, UserMixin, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
from functools import wraps
import pandas as pd
from io import StringIO
from config_production import config

# Initialize Flask app
app = Flask(__name__)

# Load configuration based on environment
env = os.environ.get('FLASK_ENV', 'development')
app.config.from_object(config[env])

# Initialize extensions
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'

# Import all the models and routes from app_new.py
# (This is a simplified production wrapper)

if __name__ == '__main__':
    # For development only
    if env == 'development':
        with app.app_context():
            db.create_all()
            print("✅ Database tables created successfully!")
        app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
    else:
        # Production: Let gunicorn handle the app
        with app.app_context():
            db.create_all()
            print("✅ Production database initialized!")
