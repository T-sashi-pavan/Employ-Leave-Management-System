"""
WSGI Configuration for Employee Leave Management System
Production-ready WSGI entry point
"""

import os
import sys
from app_new import app, db, User

# Force database initialization on every startup
def force_init_db():
    """Force initialize database with tables and default users"""
    try:
        print("🔧 Forcing database initialization...")
        
        with app.app_context():
            # Drop all tables and recreate them (for fresh start)
            print("📦 Creating database tables...")
            db.create_all()
            print("✅ Database tables created successfully!")
            
            # Verify tables exist
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            print(f"📋 Tables found: {tables}")
            
            if 'user' not in tables:
                print("❌ User table not found after creation!")
                # Try alternative approach
                db.metadata.create_all(db.engine)
                tables = inspector.get_table_names()
                print(f"📋 Tables after metadata create: {tables}")
            
            # Create default users
            try:
                # Check if any users exist
                user_count = User.query.count()
                print(f"👥 Current user count: {user_count}")
                
                if user_count == 0:
                    print("👤 Creating default users...")
                    
                    # Create admin user
                    admin = User(
                        username='admin',
                        email='admin@elms.com',
                        role='admin',
                        team=None
                    )
                    admin.set_password('admin123')
                    db.session.add(admin)
                    
                    # Create manager user
                    manager = User(
                        username='manager',
                        email='manager@elms.com',
                        role='manager',
                        team='Engineering'
                    )
                    manager.set_password('manager123')
                    db.session.add(manager)
                    
                    # Create employee user
                    employee = User(
                        username='employee',
                        email='employee@elms.com',
                        role='employee',
                        team='Engineering'
                    )
                    employee.set_password('employee123')
                    db.session.add(employee)
                    
                    db.session.commit()
                    print("✅ Default users created successfully!")
                    print("👤 Admin: admin/admin123")
                    print("👤 Manager: manager/manager123")
                    print("👤 Employee: employee/employee123")
                else:
                    print("ℹ️  Users already exist, skipping creation")
                    
            except Exception as e:
                print(f"⚠️  User creation error: {e}")
                db.session.rollback()
                
        print("🎉 Database initialization completed!")
        
    except Exception as e:
        print(f"❌ Critical database initialization error: {e}")
        import traceback
        traceback.print_exc()

# Always initialize database in production
print("🚀 Starting Employee Leave Management System...")
force_init_db()

# Configure for production
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
