# 📦 How to Package GutachtenAssist for Distribution

## Option 1: Executable Package (PyInstaller)

### Step 1: Install PyInstaller
```bash
pip install pyinstaller
```

### Step 2: Create Executable
```bash
# Create single executable
pyinstaller --onefile --windowed --name GutachtenAssist simple_demo.py

# Create directory with all files
pyinstaller --onedir --windowed --name GutachtenAssist simple_demo.py
```

### Step 3: Create Installer Script
Create `install.bat` (Windows):
```batch
@echo off
echo Installing GutachtenAssist...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Python is not installed. Please install Python 3.8+ first.
    pause
    exit /b 1
)

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt

REM Create desktop shortcut
echo Creating desktop shortcut...
powershell "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%USERPROFILE%\Desktop\GutachtenAssist.lnk'); $Shortcut.TargetPath = 'python'; $Shortcut.Arguments = 'simple_demo.py'; $Shortcut.WorkingDirectory = '%~dp0'; $Shortcut.Save()"

echo.
echo Installation complete!
echo You can now run GutachtenAssist from the desktop shortcut.
pause
```

Create `install.sh` (Linux/macOS):
```bash
#!/bin/bash
echo "Installing GutachtenAssist..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is not installed. Please install Python 3.8+ first."
    exit 1
fi

# Install dependencies
echo "Installing dependencies..."
pip3 install -r requirements.txt

# Create desktop shortcut
echo "Creating desktop shortcut..."
cat > ~/Desktop/GutachtenAssist.desktop << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=GutachtenAssist
Comment=Expert Opinion Writing Assistant
Exec=python3 simple_demo.py
Path=$(pwd)
Icon=text-editor
Terminal=false
Categories=Office;
EOF

chmod +x ~/Desktop/GutachtenAssist.desktop

echo "Installation complete!"
echo "You can now run GutachtenAssist from the desktop shortcut."
```

## Option 2: Docker Container

### Step 1: Create Dockerfile
```dockerfile
FROM python:3.9-slim

# Set working directory
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
port = 8501\n\
enableCORS = false\n\
\n\
" > ~/.streamlit/config.toml

# Expose port
EXPOSE 8501

# Run the application
CMD ["streamlit", "run", "simple_demo.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

### Step 2: Build and Distribute Docker Image
```bash
# Build image
docker build -t gutachten-assist .

# Save image to file
docker save gutachten-assist > gutachten-assist.tar

# On target machine, load image
docker load < gutachten-assist.tar

# Run container
docker run -p 8501:8501 gutachten-assist
```

## Option 3: Virtual Environment Package

### Step 1: Create Virtual Environment
```bash
# Create virtual environment
python -m venv gutachten-assist-env

# Activate environment
# Windows:
gutachten-assist-env\Scripts\activate
# Linux/macOS:
source gutachten-assist-env/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Create Distribution Package
```bash
# Create distribution directory
mkdir GutachtenAssist-Distribution
cp -r gutachten-assist-env GutachtenAssist-Distribution/
cp -r src GutachtenAssist-Distribution/
cp *.py GutachtenAssist-Distribution/
cp *.md GutachtenAssist-Distribution/
cp requirements.txt GutachtenAssist-Distribution/

# Create run script
echo "cd $(pwd)/GutachtenAssist-Distribution" > GutachtenAssist-Distribution/run.bat
echo "gutachten-assist-env\Scripts\activate" >> GutachtenAssist-Distribution/run.bat
echo "streamlit run simple_demo.py" >> GutachtenAssist-Distribution/run.bat

# Create ZIP
zip -r GutachtenAssist-Distribution.zip GutachtenAssist-Distribution/
```

## Option 4: Windows MSI Installer

### Step 1: Install cx_Freeze
```bash
pip install cx_Freeze
```

### Step 2: Create setup.py
```python
from cx_Freeze import setup, Executable

build_exe_options = {
    "packages": ["streamlit", "pandas", "numpy"],
    "excludes": [],
    "include_files": ["src/", "requirements.txt", "README.md"]
}

setup(
    name="GutachtenAssist",
    version="1.0",
    description="Expert Opinion Writing Assistant",
    options={"build_exe": build_exe_options},
    executables=[Executable("simple_demo.py", base="Win32GUI")]
)
```

### Step 3: Build MSI
```bash
python setup.py bdist_msi
```

## Option 5: Portable Package

### Step 1: Create Portable Structure
```
GutachtenAssist-Portable/
├── Python/              # Embedded Python
├── App/                 # Application files
├── Models/              # ML models
├── Data/                # Data storage
├── run.bat              # Windows launcher
├── run.sh               # Linux/macOS launcher
└── README.txt           # Instructions
```

### Step 2: Create Launcher Scripts
Create `run.bat`:
```batch
@echo off
cd /d "%~dp0"
echo Starting GutachtenAssist...
Python\python.exe -m streamlit run App\simple_demo.py --server.port=8501
pause
```

Create `run.sh`:
```bash
#!/bin/bash
cd "$(dirname "$0")"
echo "Starting GutachtenAssist..."
./Python/bin/python3 -m streamlit run App/simple_demo.py --server.port=8501
```

## Option 6: Chocolatey Package (Windows)

### Step 1: Create Chocolatey Package
Create `gutachten-assist.nuspec`:
```xml
<?xml version="1.0"?>
<package xmlns="http://schemas.microsoft.com/packaging/2010/07/nuspec.xsd">
  <metadata>
    <id>gutachten-assist</id>
    <version>1.0.0</version>
    <title>GutachtenAssist</title>
    <authors>Your Name</authors>
    <projectUrl>https://github.com/yourusername/gutachten-assist</projectUrl>
    <licenseUrl>https://github.com/yourusername/gutachten-assist/blob/main/LICENSE</licenseUrl>
    <requireLicenseAcceptance>false</requireLicenseAcceptance>
    <projectSourceUrl>https://github.com/yourusername/gutachten-assist</projectSourceUrl>
    <docsUrl>https://github.com/yourusername/gutachten-assist</docsUrl>
    <bugTrackerUrl>https://github.com/yourusername/gutachten-assist/issues</bugTrackerUrl>
    <tags>gutachten medical expert-opinion streamlit</tags>
    <summary>Expert Opinion Writing Assistant</summary>
    <description>An offline expert opinion writing assistant that helps create German Gutachten through machine learning, speech recognition, and document processing.</description>
  </metadata>
  <files>
    <file src="tools\**" target="tools" />
  </files>
</package>
```

### Step 2: Create Install Script
Create `tools/chocolateyinstall.ps1`:
```powershell
$packageName = 'gutachten-assist'
$toolsDir = "$(Split-Path -parent $MyInvocation.MyCommand.Definition)"

# Install Python if not present
if (!(Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Host "Installing Python..."
    # Download and install Python
}

# Install dependencies
pip install -r requirements.txt

# Create desktop shortcut
$WshShell = New-Object -comObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut("$env:USERPROFILE\Desktop\GutachtenAssist.lnk")
$Shortcut.TargetPath = "python"
$Shortcut.Arguments = "simple_demo.py"
$Shortcut.WorkingDirectory = $toolsDir
$Shortcut.Save()
```

## 📋 Distribution Checklist

### Before Packaging:
- [ ] All dependencies listed in requirements.txt
- [ ] No hardcoded paths
- [ ] Configuration files included
- [ ] Documentation updated
- [ ] License file included
- [ ] Version number updated
- [ ] Test on clean system

### Package Contents:
- [ ] Application source code
- [ ] Python interpreter (if portable)
- [ ] Required dependencies
- [ ] Configuration files
- [ ] Documentation
- [ ] License
- [ ] Installation instructions
- [ ] Run scripts

### Testing:
- [ ] Test on Windows
- [ ] Test on macOS
- [ ] Test on Linux
- [ ] Test with different Python versions
- [ ] Test offline functionality
- [ ] Test file uploads
- [ ] Test all features

## 🚀 Quick Distribution Commands

### Create Executable:
```bash
pyinstaller --onefile --windowed --name GutachtenAssist simple_demo.py
```

### Create Docker Image:
```bash
docker build -t gutachten-assist .
docker save gutachten-assist > gutachten-assist.tar
```

### Create ZIP Package:
```bash
zip -r GutachtenAssist.zip . -x "*.pyc" "__pycache__/*" "venv/*" ".git/*"
```

### Create MSI Installer:
```bash
python setup.py bdist_msi
``` 