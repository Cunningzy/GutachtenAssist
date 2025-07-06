# 💾 How to Save Your GutachtenAssist Project

## Method 1: Git Repository (Recommended)

### Step 1: Install Git
Download from [git-scm.com](https://git-scm.com)

### Step 2: Initialize Git Repository
```bash
# Initialize git repository
git init

# Add all files
git add .

# Create first commit
git commit -m "Initial commit: GutachtenAssist project"
```

### Step 3: Connect to GitHub/GitLab
```bash
# Create repository on GitHub/GitLab first, then:
git remote add origin https://github.com/yourusername/gutachten-assist.git
git branch -M main
git push -u origin main
```

## Method 2: ZIP Archive

### Create Backup Archive
```bash
# Windows
powershell Compress-Archive -Path . -DestinationPath GutachtenAssist.zip

# Linux/macOS
zip -r GutachtenAssist.zip . -x "*.pyc" "__pycache__/*" "venv/*"
```

## Method 3: Cloud Storage

### Google Drive
1. Upload entire project folder to Google Drive
2. Share with collaborators

### OneDrive/Dropbox
1. Sync project folder to cloud storage
2. Automatic backup and sharing

## Method 4: Docker Image

### Create Dockerfile
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8501

CMD ["streamlit", "run", "simple_demo.py", "--server.port=8501"]
```

### Build and Save Docker Image
```bash
# Build image
docker build -t gutachten-assist .

# Save image to file
docker save gutachten-assist > gutachten-assist.tar

# Load on another machine
docker load < gutachten-assist.tar
```

## 📁 Project Structure to Save

```
GutachtenAssist/
├── src/                    # Source code
├── requirements.txt        # Dependencies
├── main.py                # Main application
├── simple_demo.py         # Demo version
├── setup_models.py        # Model setup
├── test_installation.py   # Installation test
├── demo.py                # Demo script
├── README.md              # Documentation
├── INSTALLATION.md        # Installation guide
└── SAVE_GUIDE.md         # This file
```

## 🔒 Security Considerations

### What to Include:
- ✅ Source code
- ✅ Documentation
- ✅ Configuration files
- ✅ Requirements

### What to Exclude:
- ❌ API keys
- ❌ Personal data
- ❌ Large model files (>100MB)
- ❌ Log files
- ❌ Temporary files

## 📋 Backup Checklist

- [ ] Source code committed to Git
- [ ] Documentation included
- [ ] Requirements file updated
- [ ] README updated
- [ ] Installation guide included
- [ ] Demo version working
- [ ] Test scripts included
- [ ] No sensitive data included
- [ ] Backup created (ZIP/Cloud) 