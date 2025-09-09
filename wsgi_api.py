"""
WSGI Configuration for Employee Leave Management API
"""

import os
from api import app, init_database

# Initialize database on startup
if __name__ != '__main__':
    init_database()

# This is what gunicorn will use
application = app

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
