"""
Employee Leave Management System - Backend API
Pure Flask API for frontend/backend separation
"""

import os
from datetime import datetime, date
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from functools import wraps
import re

# Initialize Flask app
app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///elms_api.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_ALGORITHM'] = 'HS256'

# Initialize extensions
db = SQLAlchemy(app)
CORS(app, origins=['*'])  # Configure for your Vercel domain in production

# Database Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # admin, manager, employee
    team = db.Column(db.String(50), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    last_login = db.Column(db.DateTime)
    
    def set_password(self, password):
        self.password = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password, password)
    
    def get_leave_balance(self):
        current_year = datetime.now().year
        approved_leaves = LeaveRequest.query.filter_by(
            user_id=self.id, 
            status='approved'
        ).filter(
            db.extract('year', LeaveRequest.start_date) == current_year
        ).all()
        
        used_days = sum([(req.end_date - req.start_date).days + 1 for req in approved_leaves])
        return max(0, 30 - used_days)
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'team': self.team,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'is_active': self.is_active,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'leave_balance': self.get_leave_balance()
        }

class LeaveRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    reason = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default='pending')
    manager_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    decision_reason = db.Column(db.Text, nullable=True)
    applied_on = db.Column(db.DateTime, default=datetime.utcnow)
    decided_at = db.Column(db.DateTime, nullable=True)
    
    # Relationships
    employee = db.relationship('User', foreign_keys=[user_id], backref='leave_requests')
    manager = db.relationship('User', foreign_keys=[manager_id], backref='managed_requests')
    
    @property
    def days_count(self):
        return (self.end_date - self.start_date).days + 1
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'employee_name': self.employee.username,
            'employee_team': self.employee.team,
            'start_date': self.start_date.isoformat(),
            'end_date': self.end_date.isoformat(),
            'reason': self.reason,
            'status': self.status,
            'manager_id': self.manager_id,
            'manager_name': self.manager.username if self.manager else None,
            'decision_reason': self.decision_reason,
            'applied_on': self.applied_on.isoformat(),
            'decided_at': self.decided_at.isoformat() if self.decided_at else None,
            'days_count': self.days_count
        }

class AuditLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    action = db.Column(db.String(200), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    ip_address = db.Column(db.String(50), nullable=False)
    details = db.Column(db.Text, nullable=True)
    
    user = db.relationship('User', backref='audit_logs')
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'username': self.user.username,
            'action': self.action,
            'timestamp': self.timestamp.isoformat(),
            'ip_address': self.ip_address,
            'details': self.details
        }

# Helper functions
def generate_token(user_id):
    """Generate JWT token for user"""
    payload = {
        'user_id': user_id,
        'exp': datetime.utcnow().timestamp() + 24 * 3600  # 24 hours
    }
    return jwt.encode(payload, app.config['SECRET_KEY'], algorithm=app.config['JWT_ALGORITHM'])

def verify_token(token):
    """Verify JWT token and return user"""
    try:
        payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=[app.config['JWT_ALGORITHM']])
        user = User.query.get(payload['user_id'])
        return user
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return None

def token_required(f):
    """Decorator to require authentication"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'error': 'Token is missing'}), 401
        
        try:
            if token.startswith('Bearer '):
                token = token[7:]
            
            current_user = verify_token(token)
            if not current_user:
                return jsonify({'error': 'Token is invalid'}), 401
                
        except Exception as e:
            return jsonify({'error': 'Token is invalid'}), 401
        
        return f(current_user, *args, **kwargs)
    return decorated

def role_required(roles):
    """Decorator to require specific roles"""
    def decorator(f):
        @wraps(f)
        def decorated(current_user, *args, **kwargs):
            if current_user.role not in roles:
                return jsonify({'error': 'Insufficient permissions'}), 403
            return f(current_user, *args, **kwargs)
        return decorated
    return decorator

def log_action(user_id, action, details=None):
    """Log user actions"""
    audit = AuditLog(
        user_id=user_id,
        action=action,
        ip_address=request.remote_addr or '127.0.0.1',
        details=details
    )
    db.session.add(audit)
    db.session.commit()

# Validation helpers
def validate_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password(password):
    return len(password) >= 6

# API Routes

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'timestamp': datetime.utcnow().isoformat()})

@app.route('/api/auth/register', methods=['POST'])
def register():
    """User registration"""
    try:
        data = request.get_json()
        
        # Validation
        required_fields = ['username', 'email', 'password', 'role']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        username = data['username'].strip()
        email = data['email'].strip().lower()
        password = data['password']
        role = data['role']
        team = data.get('team', '').strip() or None
        
        # Validate input
        if len(username) < 4 or len(username) > 20:
            return jsonify({'error': 'Username must be 4-20 characters'}), 400
        
        if not validate_email(email):
            return jsonify({'error': 'Invalid email format'}), 400
        
        if not validate_password(password):
            return jsonify({'error': 'Password must be at least 6 characters'}), 400
        
        if role not in ['admin', 'manager', 'employee']:
            return jsonify({'error': 'Invalid role'}), 400
        
        # Check if user exists
        if User.query.filter_by(username=username).first():
            return jsonify({'error': 'Username already exists'}), 400
        
        if User.query.filter_by(email=email).first():
            return jsonify({'error': 'Email already registered'}), 400
        
        # Create user
        user = User(
            username=username,
            email=email,
            role=role,
            team=team
        )
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        log_action(user.id, f'User registered: {username} ({role})')
        
        return jsonify({
            'message': 'Registration successful',
            'user': user.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Registration failed: {str(e)}'}), 500

@app.route('/api/auth/login', methods=['POST'])
def login():
    """User login"""
    try:
        data = request.get_json()
        
        username = data.get('username', '').strip()
        password = data.get('password', '')
        
        if not username or not password:
            return jsonify({'error': 'Username and password are required'}), 400
        
        user = User.query.filter_by(username=username).first()
        
        if not user or not user.check_password(password) or not user.is_active:
            return jsonify({'error': 'Invalid credentials'}), 401
        
        # Update last login
        user.last_login = datetime.utcnow()
        db.session.commit()
        
        # Generate token
        token = generate_token(user.id)
        
        log_action(user.id, 'User logged in')
        
        return jsonify({
            'message': 'Login successful',
            'token': token,
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Login failed: {str(e)}'}), 500

@app.route('/api/auth/profile', methods=['GET'])
@token_required
def get_profile(current_user):
    """Get user profile"""
    return jsonify({'user': current_user.to_dict()})

@app.route('/api/leaves', methods=['GET'])
@token_required
def get_leaves(current_user):
    """Get leave requests based on user role"""
    try:
        if current_user.role == 'employee':
            # Employee sees only their requests
            requests = LeaveRequest.query.filter_by(user_id=current_user.id).order_by(LeaveRequest.applied_on.desc()).all()
        elif current_user.role == 'admin':
            # Admin sees all requests
            requests = LeaveRequest.query.order_by(LeaveRequest.applied_on.desc()).all()
        else:  # manager
            # Manager sees team requests
            team_users = User.query.filter_by(team=current_user.team, role='employee').all()
            user_ids = [u.id for u in team_users]
            requests = LeaveRequest.query.filter(LeaveRequest.user_id.in_(user_ids)).order_by(LeaveRequest.applied_on.desc()).all()
        
        return jsonify({
            'requests': [req.to_dict() for req in requests]
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to fetch requests: {str(e)}'}), 500

@app.route('/api/leaves', methods=['POST'])
@token_required
def create_leave_request(current_user):
    """Create new leave request"""
    try:
        data = request.get_json()
        
        # Validation
        required_fields = ['start_date', 'end_date', 'reason']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        start_date = datetime.strptime(data['start_date'], '%Y-%m-%d').date()
        end_date = datetime.strptime(data['end_date'], '%Y-%m-%d').date()
        reason = data['reason'].strip()
        
        # Validate dates
        if start_date < date.today():
            return jsonify({'error': 'Start date cannot be in the past'}), 400
        
        if end_date < start_date:
            return jsonify({'error': 'End date cannot be before start date'}), 400
        
        if len(reason) < 10:
            return jsonify({'error': 'Reason must be at least 10 characters'}), 400
        
        # Check leave balance
        days_requested = (end_date - start_date).days + 1
        if current_user.get_leave_balance() < days_requested:
            return jsonify({
                'error': f'Insufficient leave balance. You have {current_user.get_leave_balance()} days remaining.'
            }), 400
        
        # Create request
        leave_request = LeaveRequest(
            user_id=current_user.id,
            start_date=start_date,
            end_date=end_date,
            reason=reason
        )
        
        db.session.add(leave_request)
        db.session.commit()
        
        log_action(current_user.id, f'Applied for leave: {start_date} to {end_date}', f'Days: {days_requested}')
        
        return jsonify({
            'message': 'Leave request created successfully',
            'request': leave_request.to_dict()
        }), 201
        
    except ValueError as e:
        return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to create request: {str(e)}'}), 500

@app.route('/api/leaves/<int:leave_id>', methods=['PUT'])
@token_required
@role_required(['manager', 'admin'])
def decide_leave_request(current_user, leave_id):
    """Approve or reject leave request"""
    try:
        data = request.get_json()
        
        decision = data.get('decision')
        decision_reason = data.get('decision_reason', '').strip()
        
        if decision not in ['approved', 'rejected']:
            return jsonify({'error': 'Decision must be approved or rejected'}), 400
        
        leave_request = LeaveRequest.query.get_or_404(leave_id)
        
        if leave_request.status != 'pending':
            return jsonify({'error': 'Request has already been decided'}), 400
        
        # Check permissions
        if current_user.role == 'manager' and leave_request.employee.team != current_user.team:
            return jsonify({'error': 'You can only decide on your team requests'}), 403
        
        # Update request
        leave_request.status = decision
        leave_request.manager_id = current_user.id
        leave_request.decision_reason = decision_reason
        leave_request.decided_at = datetime.utcnow()
        
        db.session.commit()
        
        log_action(current_user.id, f'{decision.title()} leave request #{leave_id}', decision_reason)
        
        return jsonify({
            'message': f'Leave request {decision} successfully',
            'request': leave_request.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to update request: {str(e)}'}), 500

@app.route('/api/admin/users', methods=['GET'])
@token_required
@role_required(['admin'])
def get_users(current_user):
    """Get all users (admin only)"""
    try:
        users = User.query.order_by(User.created_at.desc()).all()
        return jsonify({
            'users': [user.to_dict() for user in users]
        }), 200
    except Exception as e:
        return jsonify({'error': f'Failed to fetch users: {str(e)}'}), 500

@app.route('/api/admin/stats', methods=['GET'])
@token_required
@role_required(['admin'])
def get_admin_stats(current_user):
    """Get admin dashboard statistics"""
    try:
        stats = {
            'total_users': User.query.count(),
            'total_employees': User.query.filter_by(role='employee').count(),
            'total_managers': User.query.filter_by(role='manager').count(),
            'total_requests': LeaveRequest.query.count(),
            'pending_requests': LeaveRequest.query.filter_by(status='pending').count(),
            'approved_requests': LeaveRequest.query.filter_by(status='approved').count(),
            'rejected_requests': LeaveRequest.query.filter_by(status='rejected').count()
        }
        
        # Calculate approval rate
        total_requests = stats['total_requests']
        stats['approval_rate'] = round((stats['approved_requests'] / total_requests * 100) if total_requests > 0 else 0, 1)
        
        return jsonify({'stats': stats}), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to fetch stats: {str(e)}'}), 500

@app.route('/api/admin/audit-logs', methods=['GET'])
@token_required
@role_required(['admin'])
def get_audit_logs(current_user):
    """Get audit logs (admin only)"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 50, type=int)
        
        logs = AuditLog.query.order_by(AuditLog.timestamp.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'logs': [log.to_dict() for log in logs.items],
            'total': logs.total,
            'pages': logs.pages,
            'current_page': logs.page
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to fetch logs: {str(e)}'}), 500

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return jsonify({'error': 'Internal server error'}), 500

# Initialize database
def init_database():
    """Initialize database with tables and default users"""
    with app.app_context():
        try:
            db.create_all()
            print("✅ Database tables created successfully!")
            
            # Create default admin user
            admin = User.query.filter_by(username='admin').first()
            if not admin:
                admin = User(
                    username='admin',
                    email='admin@elms.com',
                    role='admin',
                    team=None
                )
                admin.set_password('admin123')
                db.session.add(admin)
                print("✅ Created admin user: admin/admin123")
            
            # Create test manager
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
                print("✅ Created manager user: manager/manager123")
            
            # Create test employee
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
                print("✅ Created employee user: employee/employee123")
            
            db.session.commit()
            print("✅ Database initialization completed!")
            
        except Exception as e:
            print(f"❌ Database initialization failed: {e}")
            raise

if __name__ == '__main__':
    init_database()
    
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') != 'production'
    
    print(f"🚀 Employee Leave Management API starting...")
    print(f"🌐 Port: {port}")
    print(f"🔧 Debug: {debug}")
    
    app.run(host='0.0.0.0', port=port, debug=debug)
