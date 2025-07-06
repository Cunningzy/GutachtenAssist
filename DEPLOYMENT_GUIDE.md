# 🌐 How to Deploy GutachtenAssist Online

## Option 1: Streamlit Cloud (Easiest)

### Step 1: Prepare for Streamlit Cloud
1. Create `requirements.txt` (already done)
2. Create `.streamlit/config.toml`:

```toml
[server]
port = 8501
enableCORS = false
enableXsrfProtection = false

[browser]
gatherUsageStats = false
```

### Step 2: Deploy to Streamlit Cloud
1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Connect your GitHub repository
3. Deploy automatically

## Option 2: Heroku

### Step 1: Create Heroku Files

**Create `Procfile`:**
```
web: streamlit run simple_demo.py --server.port=$PORT --server.address=0.0.0.0
```

**Create `runtime.txt`:**
```
python-3.9.18
```

**Create `setup.sh`:**
```bash
mkdir -p ~/.streamlit/
echo "\
[server]\n\
headless = true\n\
port = \$PORT\n\
enableCORS = false\n\
\n\
" > ~/.streamlit/config.toml
```

### Step 2: Deploy to Heroku
```bash
# Install Heroku CLI
# Create app
heroku create gutachten-assist-app

# Deploy
git add .
git commit -m "Deploy to Heroku"
git push heroku main
```

## Option 3: Railway

### Step 1: Prepare for Railway
Create `railway.json`:
```json
{
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "streamlit run simple_demo.py --server.port=$PORT --server.address=0.0.0.0",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

### Step 2: Deploy
1. Go to [railway.app](https://railway.app)
2. Connect GitHub repository
3. Deploy automatically

## Option 4: Google Cloud Run

### Step 1: Create Dockerfile
```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy application code
COPY . .

# Create streamlit config
RUN mkdir -p ~/.streamlit/
RUN echo "\
[server]\n\
headless = true\n\
port = \$PORT\n\
enableCORS = false\n\
\n\
" > ~/.streamlit/config.toml

# Expose port
EXPOSE 8501

# Run the application
CMD ["streamlit", "run", "simple_demo.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

### Step 2: Deploy to Google Cloud Run
```bash
# Build and push to Google Container Registry
gcloud builds submit --tag gcr.io/PROJECT_ID/gutachten-assist

# Deploy to Cloud Run
gcloud run deploy gutachten-assist \
  --image gcr.io/PROJECT_ID/gutachten-assist \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

## Option 5: AWS Elastic Beanstalk

### Step 1: Create Application Bundle
```bash
# Create deployment package
zip -r gutachten-assist.zip . -x "*.pyc" "__pycache__/*" "venv/*"
```

### Step 2: Deploy to AWS
1. Go to AWS Elastic Beanstalk Console
2. Create new application
3. Upload ZIP file
4. Configure environment

## Option 6: DigitalOcean App Platform

### Step 1: Prepare for DigitalOcean
Create `.do/app.yaml`:
```yaml
name: gutachten-assist
services:
- name: web
  source_dir: /
  github:
    repo: yourusername/gutachten-assist
    branch: main
  run_command: streamlit run simple_demo.py --server.port=8080 --server.address=0.0.0.0
  environment_slug: python
```

### Step 2: Deploy
1. Go to DigitalOcean App Platform
2. Connect GitHub repository
3. Deploy automatically

## Option 7: Vercel (Alternative)

### Step 1: Create `vercel.json`
```json
{
  "version": 2,
  "builds": [
    {
      "src": "simple_demo.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "simple_demo.py"
    }
  ]
}
```

### Step 2: Deploy
```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
vercel
```

## 🔧 Configuration for Production

### Environment Variables
Create `.env` file:
```env
# Production settings
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_ADDRESS=0.0.0.0
STREAMLIT_SERVER_HEADLESS=true
STREAMLIT_BROWSER_GATHER_USAGE_STATS=false
```

### Security Considerations
1. **HTTPS**: Enable SSL certificates
2. **Authentication**: Add login system
3. **Rate Limiting**: Prevent abuse
4. **Data Privacy**: Secure file uploads
5. **Backup**: Regular data backups

## 📊 Monitoring and Analytics

### Add Monitoring
```python
# Add to your app
import streamlit as st
from datetime import datetime

# Track usage
if 'visit_count' not in st.session_state:
    st.session_state.visit_count = 0
st.session_state.visit_count += 1

# Log analytics
st.write(f"Visits: {st.session_state.visit_count}")
```

## 🚀 Quick Deploy Commands

### Streamlit Cloud (Recommended)
```bash
# 1. Push to GitHub
git add .
git commit -m "Deploy to Streamlit Cloud"
git push origin main

# 2. Go to share.streamlit.io and connect repository
```

### Heroku Quick Deploy
```bash
# Create and deploy in one command
heroku create gutachten-assist-$(date +%s)
git push heroku main
```

## 📋 Deployment Checklist

- [ ] Repository is public or connected to deployment platform
- [ ] `requirements.txt` is up to date
- [ ] No sensitive data in code
- [ ] Environment variables configured
- [ ] SSL certificate enabled
- [ ] Domain configured (optional)
- [ ] Monitoring set up
- [ ] Backup strategy in place 