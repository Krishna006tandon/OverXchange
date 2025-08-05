# Deployment Troubleshooting Guide

## 404 Error on API Endpoints

If you're getting a 404 error when trying to access API endpoints, here are the steps to troubleshoot:

### 1. Check Railway Deployment Status

1. Go to your Railway dashboard
2. Check if the deployment is successful
3. Look at the deployment logs for any errors

### 2. Verify Procfile Configuration

The Procfile should contain:
```
web: python wsgi.py
```

### 3. Check wsgi.py Configuration

Make sure `wsgi.py` is properly configured:
```python
#!/usr/bin/env python3
import os
import sys

# Add backend directory to Python path
backend_dir = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.insert(0, backend_dir)

# Change to backend directory
os.chdir(backend_dir)

# Import the Flask app
from app import app

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)
```

### 4. Test API Endpoints

Run the test script to check if endpoints are working:
```bash
python test_api.py
```

### 5. Check Environment Variables

Make sure these environment variables are set in Railway:
- `PORT` (Railway sets this automatically)
- `RAILWAY_ENVIRONMENT` (Railway sets this automatically)

### 6. Common Issues and Solutions

#### Issue: 404 on all API endpoints
**Solution**: Check if the Flask app is running properly

#### Issue: CORS errors
**Solution**: CORS is already configured in the app

#### Issue: Database connection errors
**Solution**: Check MongoDB connection string

### 7. Manual Testing

You can manually test the API using curl:

```bash
# Test basic endpoint
curl https://overxchange-production.up.railway.app/

# Test login endpoint
curl -X POST https://overxchange-production.up.railway.app/api/login \
  -H "Content-Type: application/json" \
  -d '{"username":"test@test.com","password":"test123"}'

# Test admin login
curl -X POST https://overxchange-production.up.railway.app/api/admin/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@gmail.com","password":"admin"}'
```

### 8. Railway Deployment Commands

If you need to redeploy:

```bash
# Commit your changes
git add .
git commit -m "Fix deployment issues"

# Push to Railway
git push railway main
```

### 9. Check Logs

In Railway dashboard:
1. Go to your service
2. Click on "Deployments"
3. Click on the latest deployment
4. Check the logs for any errors

### 10. Restart Service

If all else fails:
1. Go to Railway dashboard
2. Find your service
3. Click "Restart"

## Admin Account Creation

If admin accounts are not being created automatically:

1. Check if the initialization function is running
2. Manually create admin using the API:
```bash
curl -X POST https://overxchange-production.up.railway.app/api/admin/create \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@gmail.com","password":"admin","name":"Admin User","role":"admin"}'
```

## Frontend Issues

If the frontend is not loading:

1. Check if the static files are being served
2. Verify the FRONTEND_DIR path in app.py
3. Make sure all HTML files are in the frontend directory

## Database Issues

If you're having database connection issues:

1. Check MongoDB connection string
2. Verify network access
3. Check if the database exists and has the required collections

## Quick Fix Checklist

- [ ] Procfile points to `wsgi.py`
- [ ] wsgi.py imports app correctly
- [ ] All environment variables are set
- [ ] MongoDB connection is working
- [ ] Admin accounts are created
- [ ] Frontend files are in the correct location
- [ ] Railway deployment is successful
- [ ] No errors in deployment logs 