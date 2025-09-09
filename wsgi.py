"""
WSGI Configuration for Employee Leave Management System
Production-ready WSGI entry point
"""

import os
from app_new import app

# Configure for production
if __name__ != '__main__':
    # Production environment
    app.config.update(
        DEBUG=False,
        TESTING=False,
    )

# This is what gunicorn will use
application = app

if __name__ == '__main__':
    # For development only
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
