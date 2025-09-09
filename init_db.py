#!/usr/bin/env python3
"""
Database Initialization Script for Employee Leave Management System
This script creates the database tables and initial admin user
"""

import os
from app_new import app, db, User

def create_default_users():
    """Create default admin and test users"""
    with app.app_context():
        # Check if admin already exists
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            # Create default admin user
            admin = User(
                username='admin',
                email='admin@elms.com',
                role='admin',
                team=None
            )
            admin.set_password('admin123')  # Change this in production!
            db.session.add(admin)
            print("✅ Created default admin user (username: admin, password: admin123)")
        
        # Create a test manager
        manager = User.query.filter_by(username='manager').first()
        if not manager:
            manager = User(
                username='manager',
                email='manager@elms.com',
                role='manager',
                team='Engineering'
            )
            manager.set_password('manager123')
            db.session.add(manager)
            print("✅ Created test manager user (username: manager, password: manager123)")
        
        # Create a test employee
        employee = User.query.filter_by(username='employee').first()
        if not employee:
            employee = User(
                username='employee',
                email='employee@elms.com',
                role='employee',
                team='Engineering'
            )
            employee.set_password('employee123')
            db.session.add(employee)
            print("✅ Created test employee user (username: employee, password: employee123)")
        
        db.session.commit()
        print("✅ Default users created successfully!")

def init_database():
    """Initialize database with tables and default data"""
    with app.app_context():
        try:
            # Create all tables
            db.create_all()
            print("✅ Database tables created successfully!")
            
            # Create default users
            create_default_users()
            
            print("\n🎉 Database initialization completed!")
            print("\n📋 Default Login Credentials:")
            print("👤 Admin: username=admin, password=admin123")
            print("👤 Manager: username=manager, password=manager123") 
            print("👤 Employee: username=employee, password=employee123")
            print("\n⚠️  Please change default passwords in production!")
            
        except Exception as e:
            print(f"❌ Database initialization failed: {e}")
            raise

if __name__ == '__main__':
    init_database()
