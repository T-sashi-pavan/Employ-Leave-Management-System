"""
WSGI Configuration for Employee Leave Management System
Production-ready WSGI entry point
"""

import os
from app_new import app, db, User

# Initialize database in production
def init_db():
    """Initialize database with tables and default users"""
    with app.app_context():
        try:
            # Create all tables
            db.create_all()
            print("✅ Database tables created successfully!")
            
            # Create default admin user if not exists
            admin = User.query.filter_by(username='admin').first()
            if not admin:
                admin = User(
                    username='admin',
                    email='admin@elms.com',
                    role='admin',
                    team=None
                )
                admin.set_password('admin123')  # Change this in production!
                db.session.add(admin)
                db.session.commit()
                print("✅ Created default admin user (username: admin, password: admin123)")
            
        except Exception as e:
            print(f"❌ Database initialization error: {e}")

# Configure for production
if __name__ != '__main__':
    # Production environment
    app.config.update(
        DEBUG=False,
        TESTING=False,
    )
    # Initialize database tables on startup
    init_db()

# This is what gunicorn will use
application = app

if __name__ == '__main__':
    # For development only
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
