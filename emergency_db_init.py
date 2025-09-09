#!/usr/bin/env python3
"""
Emergency Database Initialization Script
Run this to force create database tables and users
"""

import os
import sys

# Ensure we can import the app
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from app_new import app, db, User
    
    def emergency_db_init():
        """Emergency database initialization"""
        print("🚨 Emergency Database Initialization")
        print("=" * 50)
        
        with app.app_context():
            try:
                # Force create all tables
                print("🔧 Dropping and recreating all tables...")
                db.drop_all()
                db.create_all()
                
                # Verify tables
                from sqlalchemy import inspect
                inspector = inspect(db.engine)
                tables = inspector.get_table_names()
                print(f"✅ Tables created: {tables}")
                
                if 'user' not in tables:
                    raise Exception("User table not created!")
                
                # Create default users
                print("👤 Creating default users...")
                
                users_data = [
                    {'username': 'admin', 'email': 'admin@elms.com', 'role': 'admin', 'team': None, 'password': 'admin123'},
                    {'username': 'manager', 'email': 'manager@elms.com', 'role': 'manager', 'team': 'Engineering', 'password': 'manager123'},
                    {'username': 'employee', 'email': 'employee@elms.com', 'role': 'employee', 'team': 'Engineering', 'password': 'employee123'}
                ]
                
                for user_data in users_data:
                    user = User(
                        username=user_data['username'],
                        email=user_data['email'],
                        role=user_data['role'],
                        team=user_data['team']
                    )
                    user.set_password(user_data['password'])
                    db.session.add(user)
                    print(f"➕ Added user: {user_data['username']}")
                
                db.session.commit()
                
                # Verify users
                user_count = User.query.count()
                print(f"✅ Total users created: {user_count}")
                
                print("\n🎉 Emergency initialization completed!")
                print("\n📋 Login Credentials:")
                print("👤 Admin: admin / admin123")
                print("👤 Manager: manager / manager123")
                print("👤 Employee: employee / employee123")
                
                return True
                
            except Exception as e:
                print(f"❌ Emergency initialization failed: {e}")
                import traceback
                traceback.print_exc()
                return False
    
    if __name__ == '__main__':
        success = emergency_db_init()
        sys.exit(0 if success else 1)
        
except Exception as e:
    print(f"❌ Import error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
