# Vercel Deployment Guide for Employee Leave Management System

## ⚡ Deploy to Vercel (Serverless - Limited for Flask)

**⚠️ Important Note**: Vercel is primarily designed for frontend applications and serverless functions. While it's possible to deploy Flask apps, there are significant limitations:

- No persistent database storage (needs external DB)
- Cold starts for each request
- Limited execution time (10 seconds max)
- No persistent file storage

### Prerequisites
1. Vercel account
2. External database (PostgreSQL, MongoDB Atlas, etc.)

### Step 1: Prepare for Vercel

Create these files for Vercel deployment:

### Step 2: Limitations on Vercel

❌ **Not Recommended for this Flask app because**:
- SQLite database won't persist (gets reset on each deployment)
- Session management issues
- Cold start delays
- Limited to serverless functions

### Step 3: Alternative Vercel Setup (If you still want to try)

1. **Split Architecture**:
   - Deploy Flask API as serverless functions
   - Create separate React/Vue frontend
   - Use external database (PostgreSQL on Render/Railway)

2. **Vercel Configuration**:
   ```json
   {
     "functions": {
       "api/*.py": {
         "runtime": "python3.9"
       }
     },
     "routes": [
       { "src": "/api/(.*)", "dest": "/api/$1" },
       { "src": "/(.*)", "dest": "/index.html" }
     ]
   }
   ```

### Step 4: Why Vercel isn't ideal for this project

1. **Database Persistence**: SQLite resets on each deployment
2. **Session Management**: Flask sessions don't work well with serverless
3. **File Uploads**: No persistent file storage
4. **Complex Routing**: Flask routing conflicts with Vercel's system

---

## 🎯 **Recommendation**: Use Render instead!

For a full-stack Flask application like your Employee Leave Management System:

### ✅ **Better Alternatives to Vercel:**
1. **Render** (Recommended) - Native Python support, persistent DB
2. **Railway** - Great for Flask apps, auto-deploy from Git
3. **Heroku** - Traditional choice for Flask (paid plans)
4. **DigitalOcean App Platform** - Good performance, affordable

---

## 🔄 **Hybrid Approach** (Advanced)

If you want to use Vercel for the frontend:

1. **Separate the projects**:
   - Backend API (Flask) → Deploy to Render
   - Frontend (React/Vue) → Deploy to Vercel

2. **API Communication**:
   - Flask backend serves JSON APIs
   - React frontend consumes APIs
   - Handle CORS properly

This approach gives you:
- Fast frontend on Vercel CDN
- Reliable backend on Render
- Best of both platforms
