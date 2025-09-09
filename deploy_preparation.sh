#!/bin/bash

# 🚀 One-Click Deployment Script for Employee Leave Management System

echo "🚀 Starting deployment preparation..."

# Check if git is initialized
if [ ! -d ".git" ]; then
    echo "📝 Initializing Git repository..."
    git init
    git branch -M main
fi

# Add all files
echo "📦 Adding files to Git..."
git add .

# Commit changes
echo "💾 Committing changes..."
git commit -m "Deploy: Employee Leave Management System

✨ Features:
- Complete Flask web application with role-based access
- User registration and authentication system
- Admin, Manager, and Employee dashboards  
- Leave request workflow (submit, approve, reject)
- Audit logging and activity tracking
- Data export functionality (CSV)
- Responsive Bootstrap 5 UI
- Production-ready configuration

🚀 Ready for deployment to Render/Railway/Heroku"

echo "✅ Git repository prepared!"
echo ""
echo "🌐 Next steps for deployment:"
echo ""
echo "📌 Option 1: Render (Recommended)"
echo "   1. Go to https://render.com"
echo "   2. Sign up/Login"
echo "   3. New Web Service → Connect GitHub"
echo "   4. Select this repository"
echo "   5. Build Command: pip install -r requirements.txt"
echo "   6. Start Command: gunicorn app_new:app"
echo "   7. Add environment variable: SECRET_KEY=your-secret-key"
echo "   8. Deploy!"
echo ""
echo "📌 Option 2: Railway"
echo "   1. Go to https://railway.app"
echo "   2. New Project → Deploy from GitHub"
echo "   3. Select this repository"
echo "   4. Add environment variable: SECRET_KEY=your-secret-key"
echo "   5. Deploy!"
echo ""
echo "📌 Option 3: Heroku"
echo "   heroku create your-app-name"
echo "   heroku addons:create heroku-postgresql:hobby-dev"
echo "   git push heroku main"
echo ""
echo "🎉 Your Employee Leave Management System is ready for deployment!"
echo "📖 Read DEPLOYMENT_GUIDE.md for detailed instructions"
