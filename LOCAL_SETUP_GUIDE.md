# ExportFlow - Complete Local Setup Guide
## Exporter Finance & Compliance Platform

A super-detailed, beginner-friendly guide to run this project on your local computer.

---

# TABLE OF CONTENTS

1. [Overview](#overview)
2. [System Requirements](#system-requirements)
3. [Step 1: Install Node.js](#step-1-install-nodejs)
4. [Step 2: Install Python](#step-2-install-python)
5. [Step 3: Install MongoDB](#step-3-install-mongodb)
6. [Step 4: Install Yarn](#step-4-install-yarn)
7. [Step 5: Install Git](#step-5-install-git)
8. [Step 6: Download the Project](#step-6-download-the-project)
9. [Step 7: Setup Backend](#step-7-setup-backend)
10. [Step 8: Setup Frontend](#step-8-setup-frontend)
11. [Step 9: Run the Application](#step-9-run-the-application)
12. [Step 10: Test the Application](#step-10-test-the-application)
13. [Stopping the Application](#stopping-the-application)
14. [Troubleshooting Guide](#troubleshooting-guide)
15. [Useful Commands Cheatsheet](#useful-commands-cheatsheet)

---

# OVERVIEW

## What is this application?
ExportFlow is a web application for managing export business operations including:
- Shipment tracking
- Payment management
- GST compliance
- Export incentives (RoDTEP/RoSCTL)
- AI-powered assistant

## Technology Stack
| Component | Technology | Purpose |
|-----------|------------|---------|
| Frontend | React.js | User interface |
| Backend | FastAPI (Python) | API server |
| Database | MongoDB | Data storage |

## What you'll need
- A computer running Windows 10/11, macOS, or Linux
- Internet connection (for downloading tools)
- About 2GB of free disk space
- 30-60 minutes of time

---

# SYSTEM REQUIREMENTS

## Minimum Requirements
- **RAM:** 4GB (8GB recommended)
- **Disk Space:** 2GB free
- **OS:** Windows 10+, macOS 10.15+, or Ubuntu 20.04+

## Check Your System

### Windows
1. Press `Windows + R`
2. Type `msinfo32` and press Enter
3. Look at "Installed Physical Memory (RAM)"

### macOS
1. Click Apple menu () → "About This Mac"
2. Check the Memory line

### Linux
```bash
free -h
```

---

# STEP 1: INSTALL NODE.JS

Node.js is required to run the frontend (React application).

## Windows Installation

### 1.1 Download Node.js
1. Open your web browser
2. Go to: **https://nodejs.org/**
3. You'll see two download buttons:
   - LTS (Recommended) ← **Click this one**
   - Current
4. Click the **LTS** button to download

### 1.2 Run the Installer
1. Go to your Downloads folder
2. Double-click `node-v20.x.x-x64.msi` (filename may vary)
3. Click **"Next"** on the Welcome screen
4. Check ✅ "I accept the terms in the License Agreement"
5. Click **"Next"**
6. Keep the default installation path (usually `C:\Program Files\nodejs\`)
7. Click **"Next"**
8. On "Custom Setup" - keep defaults, click **"Next"**
9. ⚠️ **Important:** Check ✅ "Automatically install the necessary tools..."
10. Click **"Next"**
11. Click **"Install"**
12. If prompted, click **"Yes"** to allow changes
13. Wait for installation to complete
14. Click **"Finish"**

### 1.3 Verify Installation
1. Press `Windows + R`
2. Type `cmd` and press Enter
3. In the black window (Command Prompt), type:
```bash
node --version
```
4. Press Enter
5. ✅ **Success:** You should see something like `v20.10.0`
6. ❌ **Failed:** If you see "'node' is not recognized...", restart your computer and try again

---

## macOS Installation

### 1.1 Download Node.js
1. Open Safari or Chrome
2. Go to: **https://nodejs.org/**
3. Click the **LTS** button (left button, labeled "Recommended For Most Users")
4. A `.pkg` file will download

### 1.2 Run the Installer
1. Open Finder
2. Go to Downloads folder
3. Double-click `node-v20.x.x.pkg`
4. Click **"Continue"** on the Introduction screen
5. Click **"Continue"** on the License screen
6. Click **"Agree"** to accept the license
7. Click **"Install"**
8. Enter your Mac password when prompted
9. Wait for installation
10. Click **"Close"**

### 1.3 Verify Installation
1. Press `Cmd + Space` (opens Spotlight)
2. Type `terminal` and press Enter
3. In the Terminal window, type:
```bash
node --version
```
4. Press Enter
5. ✅ **Success:** You should see something like `v20.10.0`

---

## Linux (Ubuntu/Debian) Installation

### 1.1 Open Terminal
1. Press `Ctrl + Alt + T` to open Terminal

### 1.2 Install Node.js
Copy and paste these commands one by one:

```bash
# Update package list
sudo apt update

# Install curl if not present
sudo apt install -y curl

# Add NodeSource repository
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -

# Install Node.js
sudo apt install -y nodejs
```

### 1.3 Verify Installation
```bash
node --version
```
✅ **Success:** You should see something like `v20.10.0`

---

# STEP 2: INSTALL PYTHON

Python is required to run the backend (FastAPI server).

## Windows Installation

### 2.1 Download Python
1. Open your web browser
2. Go to: **https://www.python.org/downloads/**
3. Click the big yellow button **"Download Python 3.12.x"**

### 2.2 Run the Installer
1. Go to Downloads folder
2. Double-click `python-3.12.x-amd64.exe`
3. ⚠️ **VERY IMPORTANT:** At the bottom of the first screen, check ✅ **"Add python.exe to PATH"**
4. Click **"Install Now"** (the big button at the top)
5. Wait for installation to complete
6. Click **"Close"**

### 2.3 Verify Installation
1. **Close any open Command Prompt windows**
2. Press `Windows + R`
3. Type `cmd` and press Enter
4. Type:
```bash
python --version
```
5. Press Enter
6. ✅ **Success:** You should see `Python 3.12.x`

Also verify pip (Python package manager):
```bash
pip --version
```
✅ **Success:** You should see `pip 23.x.x from ...`

---

## macOS Installation

### 2.1 Download Python
1. Go to: **https://www.python.org/downloads/**
2. Click **"Download Python 3.12.x"**

### 2.2 Run the Installer
1. Open Downloads folder in Finder
2. Double-click `python-3.12.x-macos11.pkg`
3. Click **"Continue"** through the screens
4. Click **"Install"**
5. Enter your password when prompted
6. Click **"Close"**

### 2.3 Verify Installation
1. Open Terminal (`Cmd + Space`, type `terminal`, press Enter)
2. Type:
```bash
python3 --version
```
3. ✅ **Success:** You should see `Python 3.12.x`

---

## Linux (Ubuntu/Debian) Installation

### 2.1 Install Python
```bash
# Update packages
sudo apt update

# Install Python and pip
sudo apt install -y python3 python3-pip python3-venv

# Verify
python3 --version
pip3 --version
```

---

# STEP 3: INSTALL MONGODB

MongoDB is the database where all application data is stored.

## Windows Installation

### 3.1 Download MongoDB
1. Go to: **https://www.mongodb.com/try/download/community**
2. Under "MongoDB Community Server", ensure:
   - Version: `7.0.x` (latest)
   - Platform: `Windows`
   - Package: `msi`
3. Click **"Download"**

### 3.2 Run the Installer
1. Go to Downloads folder
2. Double-click `mongodb-windows-x86_64-7.0.x-signed.msi`
3. Click **"Next"**
4. Check ✅ "I accept the terms..."
5. Click **"Next"**
6. Choose **"Complete"** installation
7. Click **"Next"**
8. ✅ Keep **"Install MongoDB as a Service"** checked
9. ✅ Keep **"Run service as Network Service user"** selected
10. Click **"Next"**
11. ✅ Keep **"Install MongoDB Compass"** checked (optional GUI tool)
12. Click **"Next"**
13. Click **"Install"**
14. Click **"Yes"** if prompted for permissions
15. Wait for installation
16. Click **"Finish"**

### 3.3 Verify MongoDB is Running
1. Press `Windows + R`
2. Type `services.msc` and press Enter
3. Scroll down to find **"MongoDB Server"**
4. ✅ **Success:** Status should say **"Running"**

If not running:
1. Right-click on "MongoDB Server"
2. Click **"Start"**

### 3.4 Test MongoDB Connection
1. Open Command Prompt (Windows + R, type `cmd`)
2. Type:
```bash
mongosh
```
3. ✅ **Success:** You should see the MongoDB shell prompt
4. Type `exit` to close

---

## macOS Installation

### 3.1 Install Homebrew (if not installed)
1. Open Terminal
2. Run this command:
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```
3. Follow the prompts (press Enter, enter password when asked)

### 3.2 Install MongoDB
```bash
# Add MongoDB tap
brew tap mongodb/brew

# Install MongoDB
brew install mongodb-community@7.0
```

### 3.3 Start MongoDB
```bash
# Start MongoDB service
brew services start mongodb-community@7.0
```

### 3.4 Verify MongoDB is Running
```bash
# Check if running
brew services list
```
✅ **Success:** You should see `mongodb-community started`

### 3.5 Test Connection
```bash
mongosh
```
Then type `exit` to close.

---

## Linux (Ubuntu/Debian) Installation

### 3.1 Import MongoDB Public Key
```bash
curl -fsSL https://pgp.mongodb.com/server-7.0.asc | sudo gpg -o /usr/share/keyrings/mongodb-server-7.0.gpg --dearmor
```

### 3.2 Add MongoDB Repository
```bash
echo "deb [ arch=amd64,arm64 signed-by=/usr/share/keyrings/mongodb-server-7.0.gpg ] https://repo.mongodb.org/apt/ubuntu jammy/mongodb-org/7.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-7.0.list
```

### 3.3 Install MongoDB
```bash
sudo apt update
sudo apt install -y mongodb-org
```

### 3.4 Start MongoDB
```bash
# Start MongoDB
sudo systemctl start mongod

# Enable auto-start on boot
sudo systemctl enable mongod

# Check status
sudo systemctl status mongod
```
✅ **Success:** You should see `active (running)`

---

# STEP 4: INSTALL YARN

Yarn is a package manager for JavaScript (faster than npm).

## All Platforms (Windows, macOS, Linux)

### 4.1 Open Terminal/Command Prompt

**Windows:** Press `Windows + R`, type `cmd`, press Enter
**macOS:** Press `Cmd + Space`, type `terminal`, press Enter
**Linux:** Press `Ctrl + Alt + T`

### 4.2 Install Yarn
```bash
npm install -g yarn
```

Wait for installation to complete.

### 4.3 Verify Installation
```bash
yarn --version
```
✅ **Success:** You should see something like `1.22.x`

---

# STEP 5: INSTALL GIT

Git is used for downloading and managing the project code.

## Windows Installation

### 5.1 Download Git
1. Go to: **https://git-scm.com/download/win**
2. Download will start automatically
3. If not, click **"Click here to download manually"**

### 5.2 Run the Installer
1. Double-click the downloaded file `Git-2.x.x-64-bit.exe`
2. Click **"Yes"** if prompted
3. Click **"Next"** to accept the license
4. Keep default installation location, click **"Next"**
5. Keep default components, click **"Next"**
6. Keep default start menu folder, click **"Next"**
7. **Default editor:** Keep "Use Vim" or select "Use Visual Studio Code" if you have it
8. Click **"Next"** for all remaining screens (keep defaults)
9. Click **"Install"**
10. Click **"Finish"**

### 5.3 Verify Installation
Open a **new** Command Prompt and type:
```bash
git --version
```
✅ **Success:** You should see `git version 2.x.x`

---

## macOS Installation

Git comes pre-installed on macOS. Verify by opening Terminal:
```bash
git --version
```

If not installed, you'll be prompted to install Xcode Command Line Tools. Click **"Install"**.

---

## Linux Installation

```bash
sudo apt install -y git
git --version
```

---

# STEP 6: DOWNLOAD THE PROJECT

Now we'll download the ExportFlow project to your computer.

## Option A: Download as ZIP (Easiest)

### 6.1 Download from Emergent
1. In the Emergent platform, click the **"Download"** or **"Export"** button
2. Save the ZIP file to your Downloads folder

### 6.2 Extract the ZIP File

**Windows:**
1. Go to Downloads folder
2. Right-click on `exportflow.zip` (or similar name)
3. Click **"Extract All..."**
4. Choose a location (e.g., `C:\Projects\exportflow`)
5. Click **"Extract"**

**macOS:**
1. Go to Downloads folder
2. Double-click the ZIP file
3. A folder will be created
4. Move it to a convenient location (e.g., `~/Projects/exportflow`)

**Linux:**
```bash
cd ~/Downloads
unzip exportflow.zip -d ~/Projects/
cd ~/Projects/exportflow
```

---

## Option B: Clone with Git

If you have a Git repository URL:

### 6.1 Create Projects Folder

**Windows:**
```bash
mkdir C:\Projects
cd C:\Projects
```

**macOS/Linux:**
```bash
mkdir -p ~/Projects
cd ~/Projects
```

### 6.2 Clone the Repository
```bash
git clone <your-repository-url> exportflow
cd exportflow
```

---

## 6.3 Verify Project Structure

After downloading, open the folder and verify you see:
```
exportflow/
├── backend/
│   ├── app/
│   ├── server.py
│   ├── requirements.txt
│   └── .env (may need to create)
├── frontend/
│   ├── src/
│   ├── package.json
│   └── .env (may need to create)
└── README.md
```

---

# STEP 7: SETUP BACKEND

## 7.1 Open Terminal/Command Prompt

**Windows:** 
- Press `Windows + R`
- Type `cmd`
- Press Enter

**macOS:**
- Press `Cmd + Space`
- Type `terminal`
- Press Enter

**Linux:**
- Press `Ctrl + Alt + T`

## 7.2 Navigate to Backend Folder

**Windows:**
```bash
cd C:\Projects\exportflow\backend
```

**macOS/Linux:**
```bash
cd ~/Projects/exportflow/backend
```

**Verify you're in the right folder:**
```bash
dir    # Windows
ls     # macOS/Linux
```
You should see `server.py`, `requirements.txt`, `app/` folder, etc.

## 7.3 Create Python Virtual Environment

A virtual environment keeps this project's Python packages separate from other projects.

```bash
python -m venv venv
```

**What this does:** Creates a `venv` folder containing a isolated Python environment.

## 7.4 Activate the Virtual Environment

**Windows (Command Prompt):**
```bash
venv\Scripts\activate.bat
```

**Windows (PowerShell):**
```bash
venv\Scripts\Activate.ps1
```

If you get an error about "execution of scripts is disabled", run PowerShell as Administrator and execute:
```bash
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```
Then try again.

**macOS/Linux:**
```bash
source venv/bin/activate
```

**How to know it worked:**
Your command prompt should now show `(venv)` at the beginning:
```
(venv) C:\Projects\exportflow\backend>     # Windows
(venv) user@computer:~/Projects/exportflow/backend$   # macOS/Linux
```

## 7.5 Upgrade pip

```bash
pip install --upgrade pip
```

Wait for it to complete.

## 7.6 Install Python Dependencies

```bash
pip install -r requirements.txt
```

**What this does:** Installs all required Python packages (FastAPI, MongoDB driver, JWT, etc.)

**This may take 2-5 minutes.** You'll see lots of text scrolling.

✅ **Success:** Command completes without red error messages.

## 7.7 Create Backend Environment File

Create a file named `.env` in the backend folder.

**Windows (Command Prompt):**
```bash
notepad .env
```
This opens Notepad. Paste the following content:

**macOS/Linux:**
```bash
nano .env
```
This opens the nano editor. Paste the following content:

---

**Content for `.env` file:**
```
MONGO_URL="mongodb://localhost:27017"
DB_NAME="exportflow_db"
CORS_ORIGINS="http://localhost:3000"
JWT_SECRET_KEY="my-super-secret-key-change-in-production-12345"
JWT_ALGORITHM="HS256"
JWT_EXPIRE_MINUTES=1440
EMERGENT_LLM_KEY=""
```

---

**Save the file:**
- **Notepad:** Click File → Save, then close Notepad
- **nano:** Press `Ctrl + X`, then `Y`, then `Enter`

## 7.8 Verify .env File Was Created

```bash
dir .env     # Windows
ls -la .env  # macOS/Linux
```

You should see the `.env` file listed.

## 7.9 Start the Backend Server

Make sure your virtual environment is still activated (you see `(venv)` in prompt).

```bash
uvicorn server:app --host 0.0.0.0 --port 8001 --reload
```

**What this does:**
- `uvicorn` - Python web server
- `server:app` - Run the `app` from `server.py` file
- `--host 0.0.0.0` - Accept connections from any IP
- `--port 8001` - Run on port 8001
- `--reload` - Auto-restart when code changes

**Expected output:**
```
INFO:     Will watch for changes in these directories: ['/path/to/backend']
INFO:     Uvicorn running on http://0.0.0.0:8001 (Press CTRL+C to quit)
INFO:     Started reloader process [12345]
INFO:     Started server process [12346]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

✅ **Success:** You see "Application startup complete."

⚠️ **Keep this terminal window open!** The server must keep running.

## 7.10 Test Backend (New Terminal Window)

Open a **new** terminal/command prompt window (keep the backend running in the first one).

**Windows:**
```bash
curl http://localhost:8001/api/health
```

If `curl` is not available on Windows, open a web browser and go to:
**http://localhost:8001/api/health**

**macOS/Linux:**
```bash
curl http://localhost:8001/api/health
```

**Expected response:**
```json
{"status":"healthy","timestamp":"2024-01-28T12:00:00.000000+00:00"}
```

✅ **Backend is working!**

---

# STEP 8: SETUP FRONTEND

## 8.1 Open a New Terminal Window

Keep the backend terminal running. Open a **new** terminal/command prompt.

## 8.2 Navigate to Frontend Folder

**Windows:**
```bash
cd C:\Projects\exportflow\frontend
```

**macOS/Linux:**
```bash
cd ~/Projects/exportflow/frontend
```

**Verify:**
```bash
dir    # Windows
ls     # macOS/Linux
```
You should see `package.json`, `src/` folder, etc.

## 8.3 Install Node.js Dependencies

```bash
yarn install
```

**What this does:** Downloads and installs all JavaScript packages (React, etc.)

**This may take 3-10 minutes** depending on your internet speed.

You'll see output like:
```
yarn install v1.22.x
[1/4] Resolving packages...
[2/4] Fetching packages...
[3/4] Linking dependencies...
[4/4] Building fresh packages...
Done in 123.45s.
```

✅ **Success:** You see "Done" with no red errors.

## 8.4 Create Frontend Environment File

Create a file named `.env` in the frontend folder.

**Windows:**
```bash
notepad .env
```

**macOS/Linux:**
```bash
nano .env
```

**Content for `.env` file:**
```
REACT_APP_BACKEND_URL=http://localhost:8001
```

**Save the file** (Ctrl+S in Notepad, Ctrl+X then Y then Enter in nano).

## 8.5 Verify .env File

```bash
dir .env     # Windows
ls -la .env  # macOS/Linux
```

## 8.6 Start the Frontend Development Server

```bash
yarn start
```

**What this does:** Starts the React development server with hot-reloading.

**Expected output:**
```
Compiled successfully!

You can now view frontend in the browser.

  Local:            http://localhost:3000
  On Your Network:  http://192.168.1.100:3000

Note that the development build is not optimized.
To create a production build, use yarn build.

webpack compiled successfully
```

✅ **Success:** You see "Compiled successfully!"

**Your default web browser should automatically open** to http://localhost:3000

If it doesn't open automatically, manually open your browser and go to:
**http://localhost:3000**

---

# STEP 9: RUN THE APPLICATION

## 9.1 Summary of Running Services

You should now have **two terminal windows** running:

| Terminal | Service | Address | Status |
|----------|---------|---------|--------|
| Terminal 1 | Backend (FastAPI) | http://localhost:8001 | Shows "Application startup complete" |
| Terminal 2 | Frontend (React) | http://localhost:3000 | Shows "Compiled successfully" |

## 9.2 Access the Application

1. Open your web browser (Chrome, Firefox, Edge, Safari)
2. Go to: **http://localhost:3000**
3. You should see the **ExportFlow login page**

---

# STEP 10: TEST THE APPLICATION

## 10.1 Create an Account

1. On the login page, click **"Create account"** link
2. Fill in the registration form:
   - **Full Name:** `John Doe`
   - **Company Name:** `Test Export Company`
   - **Email:** `john@test.com`
   - **Password:** `password123`
3. Click **"Create Account"** button
4. ✅ You should be redirected to the Dashboard

## 10.2 Explore the Dashboard

After logging in, you should see:
- **Left sidebar** with navigation menu
- **Main area** showing dashboard with:
  - Total Export Value card
  - Outstanding Receivables card
  - Incentives Earned card
  - Pending GST Refund card
  - Charts and graphs

## 10.3 Test Core Features

### Create a Shipment
1. Click **"Shipments"** in the left sidebar
2. Click **"New Shipment"** button
3. Fill in:
   - Shipment Number: `SH-2024-001`
   - Buyer Name: `ABC Corporation`
   - Buyer Country: `USA`
   - Origin Port: `INNSA`
   - Destination Port: `USLAX`
   - Total Value: `50000`
4. Click **"Create Shipment"**
5. ✅ Shipment should appear in the list

### Check Forex Rates
1. Click **"Forex"** in the sidebar
2. You should see currency rate cards (USD, EUR, GBP, etc.)
3. Try the currency converter

### Use AI Assistant
1. Click **"AI Assistant"** in the sidebar
2. Type a question: `What is RoDTEP?`
3. Click Send
4. ✅ You should get an AI-generated response

---

# STOPPING THE APPLICATION

## Stop Frontend
1. Go to the terminal running frontend
2. Press `Ctrl + C`
3. The server will stop

## Stop Backend
1. Go to the terminal running backend
2. Press `Ctrl + C`
3. The server will stop

## Deactivate Python Virtual Environment
In the backend terminal:
```bash
deactivate
```

## Stop MongoDB (Optional)

**Windows:**
1. Press `Windows + R`
2. Type `services.msc`
3. Find "MongoDB Server"
4. Right-click → Stop

**macOS:**
```bash
brew services stop mongodb-community
```

**Linux:**
```bash
sudo systemctl stop mongod
```

---

# RESTARTING THE APPLICATION

Next time you want to run the application:

## Terminal 1 - Backend
```bash
# Navigate to backend
cd C:\Projects\exportflow\backend   # Windows
cd ~/Projects/exportflow/backend    # macOS/Linux

# Activate virtual environment
venv\Scripts\activate.bat           # Windows CMD
source venv/bin/activate            # macOS/Linux

# Start server
uvicorn server:app --host 0.0.0.0 --port 8001 --reload
```

## Terminal 2 - Frontend
```bash
# Navigate to frontend
cd C:\Projects\exportflow\frontend  # Windows
cd ~/Projects/exportflow/frontend   # macOS/Linux

# Start server
yarn start
```

---

# TROUBLESHOOTING GUIDE

## Problem: "command not found" or "'xxx' is not recognized"

**Cause:** The software is not installed or not in system PATH.

**Solution:**
1. Close all terminal windows
2. Reinstall the software
3. For Windows, ensure "Add to PATH" is checked during installation
4. Restart your computer
5. Open a new terminal and try again

---

## Problem: MongoDB Connection Error

**Error message:**
```
ServerSelectionTimeoutError: localhost:27017
```

**Solution:**
1. Check if MongoDB is running:
   - **Windows:** Open Services (services.msc), find "MongoDB Server", ensure it's "Running"
   - **macOS:** Run `brew services list` - mongodb should show "started"
   - **Linux:** Run `sudo systemctl status mongod`

2. Start MongoDB if not running:
   - **Windows:** Right-click MongoDB Server in Services → Start
   - **macOS:** `brew services start mongodb-community`
   - **Linux:** `sudo systemctl start mongod`

---

## Problem: Port Already in Use

**Error message:**
```
ERROR: [Errno 98] Address already in use
ERROR: [Errno 48] Address already in use
```

**Solution (find and kill process using the port):**

**Windows:**
```bash
netstat -ano | findstr :8001
# Note the PID (last number)
taskkill /PID <PID> /F
```

**macOS/Linux:**
```bash
lsof -i :8001
# Note the PID
kill -9 <PID>
```

---

## Problem: CORS Error in Browser

**Error in browser console:**
```
Access to XMLHttpRequest at 'http://localhost:8001/api/...' from origin 'http://localhost:3000' has been blocked by CORS policy
```

**Solution:**
1. Check backend `.env` file has:
   ```
   CORS_ORIGINS="http://localhost:3000"
   ```
2. Restart the backend server (Ctrl+C, then run uvicorn again)

---

## Problem: Module Not Found (Python)

**Error:**
```
ModuleNotFoundError: No module named 'fastapi'
```

**Solution:**
1. Make sure virtual environment is activated (you see `(venv)` in prompt)
2. If not, activate it:
   ```bash
   venv\Scripts\activate.bat   # Windows
   source venv/bin/activate    # macOS/Linux
   ```
3. Install requirements again:
   ```bash
   pip install -r requirements.txt
   ```

---

## Problem: npm/yarn Command Not Found

**Solution:**
1. Reinstall Node.js from https://nodejs.org
2. Restart your computer
3. Open new terminal
4. Reinstall yarn:
   ```bash
   npm install -g yarn
   ```

---

## Problem: Frontend Shows Blank Page

**Solutions:**
1. Open browser developer tools (F12)
2. Check Console tab for errors
3. Make sure backend is running
4. Check frontend `.env` has correct `REACT_APP_BACKEND_URL`
5. Clear browser cache (Ctrl+Shift+Delete)
6. Try hard refresh (Ctrl+Shift+R)

---

## Problem: "ENOSPC: System limit for number of file watchers reached" (Linux)

**Solution:**
```bash
echo fs.inotify.max_user_watches=524288 | sudo tee -a /etc/sysctl.conf
sudo sysctl -p
```

---

# USEFUL COMMANDS CHEATSHEET

## Backend Commands
| Command | Description |
|---------|-------------|
| `cd backend` | Go to backend folder |
| `source venv/bin/activate` | Activate virtual environment (macOS/Linux) |
| `venv\Scripts\activate.bat` | Activate virtual environment (Windows) |
| `deactivate` | Deactivate virtual environment |
| `pip install -r requirements.txt` | Install Python dependencies |
| `uvicorn server:app --reload --port 8001` | Start backend server |
| `pip freeze > requirements.txt` | Save current packages to requirements |

## Frontend Commands
| Command | Description |
|---------|-------------|
| `cd frontend` | Go to frontend folder |
| `yarn install` | Install Node.js dependencies |
| `yarn start` | Start development server |
| `yarn build` | Create production build |
| `yarn test` | Run tests |

## MongoDB Commands
| Command | Description |
|---------|-------------|
| `mongosh` | Open MongoDB shell |
| `show dbs` | List all databases |
| `use exportflow_db` | Switch to database |
| `show collections` | List collections |
| `db.users.find()` | View all users |
| `db.shipments.find()` | View all shipments |
| `exit` | Exit MongoDB shell |

## General Commands
| Command | Description |
|---------|-------------|
| `Ctrl + C` | Stop running server |
| `Ctrl + L` | Clear terminal screen |
| `cd ..` | Go up one directory |
| `pwd` | Show current directory (macOS/Linux) |
| `cd` | Show current directory (Windows) |

---

# NEED MORE HELP?

1. Check the error message carefully
2. Search the error message on Google
3. Check Stack Overflow
4. Review this guide again
5. Ensure all prerequisites are installed correctly

---

**Congratulations!** 🎉 You've successfully set up ExportFlow on your local machine!
