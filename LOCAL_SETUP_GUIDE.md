# ExportFlow - Local Development Setup Guide

Complete step-by-step guide to run the Exporter Finance & Compliance Platform on your local machine.

---

## Prerequisites

Before starting, ensure you have the following installed:

### 1. Node.js (v18 or higher)
```bash
# Check if installed
node --version

# Download from: https://nodejs.org/
# Or using nvm (recommended):
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
nvm install 18
nvm use 18
```

### 2. Python (v3.10 or higher)
```bash
# Check if installed
python3 --version

# Download from: https://www.python.org/downloads/
# Or using pyenv:
curl https://pyenv.run | bash
pyenv install 3.11
pyenv global 3.11
```

### 3. MongoDB (v6.0 or higher)
```bash
# Check if installed
mongod --version

# macOS (using Homebrew):
brew tap mongodb/brew
brew install mongodb-community@7.0
brew services start mongodb-community@7.0

# Ubuntu/Debian:
wget -qO - https://www.mongodb.org/static/pgp/server-7.0.asc | sudo apt-key add -
echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu jammy/mongodb-org/7.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-7.0.list
sudo apt-get update
sudo apt-get install -y mongodb-org
sudo systemctl start mongod
sudo systemctl enable mongod

# Windows:
# Download installer from: https://www.mongodb.com/try/download/community
# Run the installer and select "Complete" installation
# MongoDB will run as a Windows service
```

### 4. Yarn (Package Manager)
```bash
# Install yarn globally
npm install -g yarn

# Verify installation
yarn --version
```

### 5. Git
```bash
# Check if installed
git --version

# Download from: https://git-scm.com/downloads
```

---

## Step 1: Clone/Download the Project

```bash
# Option A: Clone from repository (if using Git)
git clone <your-repository-url>
cd exportflow

# Option B: Download and extract ZIP file
# Extract to a folder named 'exportflow'
cd exportflow
```

---

## Step 2: Project Structure Overview

After downloading, your project structure should look like:
```
exportflow/
├── backend/
│   ├── app/
│   │   ├── core/
│   │   ├── auth/
│   │   ├── shipments/
│   │   ├── payments/
│   │   ├── ... (other modules)
│   │   └── main.py
│   ├── server.py
│   ├── requirements.txt
│   └── .env
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── context/
│   │   └── App.js
│   ├── package.json
│   └── .env
└── README.md
```

---

## Step 3: Backend Setup

### 3.1 Navigate to Backend Directory
```bash
cd backend
```

### 3.2 Create Python Virtual Environment
```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate

# On Windows (Command Prompt):
venv\Scripts\activate.bat

# On Windows (PowerShell):
venv\Scripts\Activate.ps1
```

### 3.3 Install Python Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 3.4 Configure Environment Variables
Create or edit the `.env` file in the `backend` directory:

```bash
# Create .env file
cat > .env << 'EOF'
MONGO_URL="mongodb://localhost:27017"
DB_NAME="exportflow_db"
CORS_ORIGINS="http://localhost:3000"
JWT_SECRET_KEY="your-super-secret-key-change-this-in-production"
JWT_ALGORITHM="HS256"
JWT_EXPIRE_MINUTES=1440
EMERGENT_LLM_KEY="your-emergent-llm-key-if-you-have-one"
EOF
```

> **Note:** Replace `your-super-secret-key-change-this-in-production` with a strong secret key.
> For AI features, you'll need an Emergent LLM key or you can leave it empty (AI features will return fallback responses).

### 3.5 Verify MongoDB is Running
```bash
# Check MongoDB status
# macOS:
brew services list | grep mongodb

# Linux:
sudo systemctl status mongod

# Windows:
# Check Services app for "MongoDB Server"

# Or try connecting:
mongosh --eval "db.adminCommand('ping')"
```

### 3.6 Start the Backend Server
```bash
# Make sure virtual environment is activated
# Then run:
uvicorn server:app --host 0.0.0.0 --port 8001 --reload
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8001 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Application startup complete.
```

### 3.7 Verify Backend is Running
Open a new terminal and test:
```bash
curl http://localhost:8001/api/health
```

Expected response:
```json
{"status":"healthy","timestamp":"2024-..."}
```

---

## Step 4: Frontend Setup

### 4.1 Open New Terminal and Navigate to Frontend
```bash
# From project root
cd frontend
```

### 4.2 Install Node Dependencies
```bash
yarn install
```

This will install all packages listed in `package.json`.

### 4.3 Configure Environment Variables
Create or edit the `.env` file in the `frontend` directory:

```bash
cat > .env << 'EOF'
REACT_APP_BACKEND_URL=http://localhost:8001
EOF
```

### 4.4 Start the Frontend Development Server
```bash
yarn start
```

You should see:
```
Compiled successfully!

You can now view the app in the browser.

  Local:            http://localhost:3000
  On Your Network:  http://192.168.x.x:3000
```

---

## Step 5: Access the Application

### 5.1 Open in Browser
Navigate to: **http://localhost:3000**

### 5.2 Create an Account
1. Click "Create account" on the login page
2. Fill in the registration form:
   - Full Name: `Your Name`
   - Company Name: `Your Company`
   - Email: `your@email.com`
   - Password: `yourpassword`
3. Click "Create Account"

### 5.3 Explore the Dashboard
After registration, you'll be redirected to the dashboard where you can:
- Create shipments
- Track payments
- Check forex rates
- Manage GST compliance
- Calculate export incentives
- Use the AI assistant

---

## Step 6: Running Both Servers (Quick Reference)

You need **two terminal windows** running simultaneously:

### Terminal 1 - Backend
```bash
cd backend
source venv/bin/activate  # or venv\Scripts\activate on Windows
uvicorn server:app --host 0.0.0.0 --port 8001 --reload
```

### Terminal 2 - Frontend
```bash
cd frontend
yarn start
```

---

## Common Issues & Troubleshooting

### Issue 1: MongoDB Connection Error
```
Error: connect ECONNREFUSED 127.0.0.1:27017
```
**Solution:** Start MongoDB service
```bash
# macOS
brew services start mongodb-community

# Linux
sudo systemctl start mongod

# Windows - Start MongoDB service from Services app
```

### Issue 2: Port Already in Use
```
Error: listen EADDRINUSE: address already in use :::8001
```
**Solution:** Kill the process using the port
```bash
# Find process using port 8001
lsof -i :8001  # macOS/Linux
netstat -ano | findstr :8001  # Windows

# Kill the process
kill -9 <PID>  # macOS/Linux
taskkill /PID <PID> /F  # Windows
```

### Issue 3: Python Module Not Found
```
ModuleNotFoundError: No module named 'fastapi'
```
**Solution:** Ensure virtual environment is activated and dependencies installed
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### Issue 4: Node/Yarn Command Not Found
**Solution:** Ensure Node.js and Yarn are installed and in PATH
```bash
# Reinstall yarn
npm install -g yarn

# Verify
yarn --version
```

### Issue 5: CORS Error in Browser
```
Access to XMLHttpRequest blocked by CORS policy
```
**Solution:** Ensure backend `.env` has correct CORS origin:
```
CORS_ORIGINS="http://localhost:3000"
```
Then restart the backend server.

---

## Development Commands Reference

### Backend Commands
```bash
# Start server (development with auto-reload)
uvicorn server:app --host 0.0.0.0 --port 8001 --reload

# Start server (production)
uvicorn server:app --host 0.0.0.0 --port 8001 --workers 4

# Run linting
pip install ruff
ruff check app/

# Format code
pip install black
black app/
```

### Frontend Commands
```bash
# Start development server
yarn start

# Build for production
yarn build

# Run tests
yarn test

# Run linting
yarn lint
```

### Database Commands
```bash
# Connect to MongoDB shell
mongosh

# Select database
use exportflow_db

# View collections
show collections

# View all users
db.users.find().pretty()

# View all shipments
db.shipments.find().pretty()

# Clear all data (careful!)
db.dropDatabase()
```

---

## API Documentation

Once the backend is running, access the auto-generated API docs:

- **Swagger UI:** http://localhost:8001/docs
- **ReDoc:** http://localhost:8001/redoc

---

## Environment Variables Reference

### Backend (.env)
| Variable | Description | Example |
|----------|-------------|---------|
| `MONGO_URL` | MongoDB connection string | `mongodb://localhost:27017` |
| `DB_NAME` | Database name | `exportflow_db` |
| `CORS_ORIGINS` | Allowed frontend origins | `http://localhost:3000` |
| `JWT_SECRET_KEY` | Secret for JWT tokens | `your-secret-key` |
| `JWT_ALGORITHM` | JWT algorithm | `HS256` |
| `JWT_EXPIRE_MINUTES` | Token expiry in minutes | `1440` |
| `EMERGENT_LLM_KEY` | AI integration key | `sk-emergent-xxx` |

### Frontend (.env)
| Variable | Description | Example |
|----------|-------------|---------|
| `REACT_APP_BACKEND_URL` | Backend API URL | `http://localhost:8001` |

---

## Production Deployment Notes

For production deployment, consider:

1. **Use production MongoDB** (MongoDB Atlas or self-hosted)
2. **Set strong JWT_SECRET_KEY**
3. **Use HTTPS** for both frontend and backend
4. **Set proper CORS origins**
5. **Use environment-specific .env files**
6. **Enable MongoDB authentication**

---

## Support

If you encounter issues:
1. Check the troubleshooting section above
2. Verify all prerequisites are installed correctly
3. Ensure MongoDB is running
4. Check that both terminals (backend & frontend) are running

Happy coding! 🚀
