# Render Deployment Guide for Employee Leave Management System

## 🌐 Deploy to Render (Full-Stack - Recommended)

Render is perfect for Flask applications as it supports Python backends with persistent storage.

### Prerequisites
1. GitHub account with your code pushed
2. Render account (free tier available)

### Step 1: Prepare for Render

1. **Update requirements.txt** (already done)
2. **Create render.yaml** (deployment configuration)
3. **Update app for production**

### Step 2: Environment Setup

Create a `.env` file for local development:
```
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///leaves.db
FLASK_ENV=production
```

### Step 3: Deploy on Render

1. **Go to Render Dashboard**: https://dashboard.render.com
2. **Connect GitHub**: Link your repository
3. **Create New Web Service**:
   - Repository: `your-username/Employ-Leave-Management-System`
   - Branch: `main`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn app_new:app`

### Step 4: Configure Environment Variables

In Render Dashboard, add these environment variables:
- `SECRET_KEY`: `your-super-secret-key-for-production`
- `DATABASE_URL`: Will be auto-generated for PostgreSQL
- `FLASK_ENV`: `production`

### Step 5: Database Setup

Render provides PostgreSQL. Update your app to use it in production.

### Features on Render:
✅ Automatic HTTPS
✅ Free tier available
✅ Persistent database storage
✅ Continuous deployment from Git
✅ Custom domains
✅ Built-in monitoring

### URLs after deployment:
- **Application**: `https://your-app-name.onrender.com`
- **Admin Access**: Login with admin credentials
- **Database**: Managed PostgreSQL included

---

## 💡 **Why Render for Flask?**
- Native Python support
- Persistent database storage
- No cold starts (unlike serverless)
- Easy environment variable management
- Built-in HTTPS and monitoring
