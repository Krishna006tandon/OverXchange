# 🚀 Railway Deployment Guide

## 📋 Prerequisites

1. **GitHub Account** - Your code should be on GitHub
2. **Railway Account** - Sign up at [railway.app](https://railway.app)
3. **MongoDB Atlas** - Already configured in your app

## 🚀 Step-by-Step Deployment

### Step 1: Push Code to GitHub

```bash
# Initialize git if not already done
git init

# Add all files
git add .

# Commit changes
git commit -m "Prepare for Railway deployment"

# Add your GitHub repository as remote
git remote add origin https://github.com/YOUR_USERNAME/OverXchange.git

# Push to GitHub
git push -u origin main
```

### Step 2: Deploy to Railway

1. **Go to Railway Dashboard**
   - Visit [railway.app](https://railway.app)
   - Sign in with your GitHub account

2. **Create New Project**
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose your OverXchange repository

3. **Configure Environment Variables**
   - Go to "Variables" tab
   - Add these environment variables:
   ```
   PORT=5000
   MONGODB_URI=mongodb+srv://krishnatandon006:krishnatandon006@zenspace.63o32aq.mongodb.net/
   ```

4. **Deploy**
   - Railway will automatically detect it's a Python app
   - It will install dependencies from `requirements.txt`
   - The app will start using the `Procfile`

### Step 3: Get Your Live URL

- Railway will provide a URL like: `https://your-app-name.railway.app`
- You can also set up a custom domain in the "Settings" tab

## 🔧 Configuration Files Created

### 1. `Procfile`
```
web: python wsgi.py
```

### 2. `wsgi.py`
- WSGI entry point for Railway
- Handles path configuration
- Sets up production environment

### 3. `requirements.txt` (Root)
- All Python dependencies
- Includes gunicorn for production

### 4. `runtime.txt`
- Specifies Python version (3.11.7)

### 5. `.gitignore`
- Excludes unnecessary files from deployment

## 🌐 Access Your Deployed App

Once deployed, your app will be available at:
- **Main URL**: `https://your-app-name.railway.app`
- **API Endpoints**: `https://your-app-name.railway.app/api/`

## 🔍 Troubleshooting

### Common Issues:

1. **Build Fails**
   - Check Railway logs in the "Deployments" tab
   - Ensure all dependencies are in `requirements.txt`
   - Verify Python version in `runtime.txt`

2. **App Won't Start**
   - Check if `wsgi.py` is correctly configured
   - Verify `Procfile` syntax
   - Check environment variables

3. **Database Connection Issues**
   - Ensure MongoDB Atlas IP whitelist includes Railway IPs
   - Verify connection string in environment variables

4. **Static Files Not Loading**
   - Check if frontend files are in the correct location
   - Verify Flask static file serving configuration

### Useful Commands:

```bash
# Check Railway CLI (optional)
npm install -g @railway/cli

# Login to Railway
railway login

# Link to your project
railway link

# Deploy manually
railway up

# View logs
railway logs
```

## 📊 Monitoring

- **Logs**: View in Railway dashboard
- **Metrics**: Monitor in "Metrics" tab
- **Deployments**: Track in "Deployments" tab

## 🔄 Continuous Deployment

Railway automatically deploys when you push to your main branch on GitHub.

## 💰 Pricing

- **Free Tier**: $5 credit monthly
- **Paid Plans**: Pay-as-you-go based on usage

## 🎉 Success!

Your OverXchange application is now live on Railway! 🚀

---

**Next Steps:**
1. Test all features on the live URL
2. Set up custom domain (optional)
3. Configure monitoring and alerts
4. Set up CI/CD pipeline (optional) 