# ExportFlow - Local Setup Guide

## Prerequisites

Before starting, ensure you have the following installed:
- **Node.js** v18+ (LTS recommended)
- **Python** 3.10+
- **MongoDB** (local instance or MongoDB Atlas connection string)
- **Git**

## Quick Start

### 1. Clone the Repository

```bash
git clone <repository-url>
cd EXPORT_FLOW
```

### 2. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Backend Environment Variables

Create a `.env` file in the `backend/` directory:

```env
MONGO_URL=mongodb://localhost:27017
DB_NAME=exportflow
JWT_SECRET_KEY=your-secret-key-here-change-in-production
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7
ENCRYPTION_KEY=your-32-byte-encryption-key-here
```

### 4. Start Backend Server

```bash
# From backend directory
uvicorn main:app --host 0.0.0.0 --port 8001 --reload
```

The backend API will be available at `http://localhost:8001`

### 5. Frontend Setup

```bash
# Open new terminal, navigate to frontend directory
cd frontend

# Install dependencies (use yarn for consistency)
yarn install
```

### 6. Frontend Environment Variables

Create/update `.env` file in the `frontend/` directory:

```env
REACT_APP_BACKEND_URL=http://localhost:8001
```

**Important**: For local development, use `http://localhost:8001` (without `/api` suffix). The AuthContext handles API path construction automatically.

### 7. Start Frontend Server

```bash
# From frontend directory
yarn start
```

The frontend will be available at `http://localhost:3000`

---

## Verification

### Test Backend Health
```bash
curl http://localhost:8001/api/health
# Expected: {"status":"healthy","database":"connected",...}
```

### Test User Registration
```bash
curl -X POST http://localhost:8001/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"Test@123","full_name":"Test User"}'
```

### Test User Login
```bash
curl -X POST http://localhost:8001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"Test@123"}'
```

---

## Project Structure

```
EXPORT_FLOW/
├── backend/
│   ├── main.py                 # FastAPI entry point
│   ├── requirements.txt        # Python dependencies
│   ├── .env                    # Backend environment variables
│   ├── app/
│   │   ├── core/              # Security, config, database
│   │   ├── models/            # Pydantic models
│   │   └── routes/            # API endpoints
│   └── tests/                 # Backend tests
│
├── frontend/
│   ├── package.json           # Node dependencies
│   ├── .env                   # Frontend environment variables
│   ├── craco.config.js        # Webpack configuration
│   └── src/
│       ├── App.js             # Root component
│       ├── index.js           # Entry point
│       ├── index.css          # Global styles
│       ├── pages/             # Page components
│       ├── components/        # Reusable components
│       ├── context/           # React context (Auth, Theme)
│       └── services/          # API service functions
│
└── README.md
```

---

## Key Features

### Authentication
- JWT-based auth with short-lived access tokens (15 min)
- Refresh token rotation for security
- Automatic token refresh before expiry

### Security
- Field-level AES-256-GCM encryption for sensitive data
- Tamper-proof audit logs with hash chain
- PII masking by default with on-demand decryption

### Landing Page
- Apple-style scroll-synced hero animation
- Premium logistics/export themed images
- Smooth parallax transitions tied to scroll position

### Dashboard
- Real-time export statistics
- Export trend charts
- Payment status visualization
- AI-powered risk alerts
- Quick action buttons

---

## Troubleshooting

### Backend Issues

**"ModuleNotFoundError"**
```bash
pip install -r requirements.txt
```

**"MongoDB connection failed"**
- Verify MongoDB is running: `mongosh`
- Check MONGO_URL in `.env`

### Frontend Issues

**"ENOENT: no such file or directory"**
```bash
rm -rf node_modules yarn.lock
yarn install
```

**"API calls failing with 404"**
- Verify `REACT_APP_BACKEND_URL` in `.env`
- Ensure backend is running on port 8001
- Check browser console for actual request URLs

**Blank page or white screen**
```bash
# Clear cache and restart
rm -rf node_modules/.cache
yarn start
```

### General Issues

**"Port already in use"**
```bash
# Find and kill process on port
lsof -ti:8001 | xargs kill -9  # Backend
lsof -ti:3000 | xargs kill -9  # Frontend
```

---

## Test Credentials

For local testing:
- **Email**: test@moradabad.com
- **Password**: Test@123

---

## Development Notes

### API Endpoints
All API endpoints are prefixed with `/api`:
- `POST /api/auth/login` - User login
- `POST /api/auth/register` - User registration
- `GET /api/auth/me` - Get current user
- `GET /api/dashboard/stats` - Dashboard statistics
- `GET /api/shipments` - List shipments
- `GET /api/payments` - List payments
- `GET /api/forex/rates` - Forex rates

### Adding New Features
1. Create backend route in `backend/app/routes/`
2. Add Pydantic models in `backend/app/models/`
3. Create frontend page in `frontend/src/pages/`
4. Add route in `frontend/src/App.js`
5. Update navigation in `DashboardLayout.js`

### CSS Guidelines
- Use Tailwind CSS utility classes
- Dark theme: `bg-[#09090B]` primary background
- Primary accent: `violet-600` / `violet-500`
- Use `shadcn/ui` components from `/frontend/src/components/ui/`

---

*Last Updated: February 18, 2025*
