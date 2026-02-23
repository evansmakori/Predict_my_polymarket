# Setup Guide - Polymarket Trading Dashboard

This guide will help you set up and run the Polymarket Trading Dashboard locally.

## Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.12+** - [Download Python](https://www.python.org/downloads/)
- **Node.js 18+** - [Download Node.js](https://nodejs.org/)
- **npm or yarn** - Comes with Node.js

## Quick Start

### 1. Backend Setup

#### Step 1: Navigate to backend directory
```bash
cd polymarket-dashboard/backend
```

#### Step 2: Create a virtual environment
```bash
# On macOS/Linux
python3 -m venv venv
source venv/bin/activate

# On Windows
python -m venv venv
venv\Scripts\activate
```

#### Step 3: Install dependencies
```bash
pip install -r requirements.txt
```

#### Step 4: Create environment file
```bash
cp .env.example .env
```

Edit `.env` if needed (default values should work for local development).

#### Step 5: Run the backend
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The backend API will be available at:
- **API**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc

### 2. Frontend Setup

Open a **new terminal** window/tab.

#### Step 1: Navigate to frontend directory
```bash
cd polymarket-dashboard/frontend
```

#### Step 2: Install dependencies
```bash
npm install
```

If you prefer yarn:
```bash
yarn install
```

#### Step 3: Create environment file
```bash
cp .env.example .env
```

Edit `.env` if needed (default values should work for local development).

#### Step 4: Run the development server
```bash
npm run dev
```

Or with yarn:
```bash
yarn dev
```

The frontend will be available at: **http://localhost:5173**

## First Time Usage

### Extract Your First Market

1. Open the frontend at http://localhost:5173
2. Click on "Extract Market" in the navigation
3. Copy a Polymarket URL, for example:
   - Event: `https://polymarket.com/event/2024-us-presidential-election`
   - Market: `https://polymarket.com/market/will-trump-win-2024`
4. Paste the URL and click "Extract Data"
5. Wait for the extraction to complete
6. View the market in the dashboard!

## Troubleshooting

### Backend Issues

**Problem**: `ModuleNotFoundError`
```bash
# Make sure virtual environment is activated
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows

# Reinstall dependencies
pip install -r requirements.txt
```

**Problem**: Port 8000 already in use
```bash
# Use a different port
uvicorn app.main:app --reload --port 8001

# Then update frontend .env:
VITE_API_BASE_URL=http://localhost:8001
VITE_WS_BASE_URL=ws://localhost:8001
```

**Problem**: Database errors
```bash
# Delete and recreate the database
rm markets.duckdb
# Restart the backend - it will recreate tables automatically
```

### Frontend Issues

**Problem**: `npm: command not found`
```bash
# Install Node.js from https://nodejs.org/
# Verify installation
node --version
npm --version
```

**Problem**: Dependencies won't install
```bash
# Clear npm cache
npm cache clean --force

# Delete node_modules and package-lock.json
rm -rf node_modules package-lock.json

# Reinstall
npm install
```

**Problem**: Port 5173 already in use
```bash
# Vite will automatically try the next available port
# Or specify a different port in vite.config.js
```

## Development Tips

### Hot Reload

Both the backend and frontend support hot reload:
- **Backend**: Changes to Python files will automatically reload the server
- **Frontend**: Changes to React files will instantly update in the browser

### API Documentation

Access the interactive API documentation at http://localhost:8000/docs to:
- Explore all available endpoints
- Test API calls directly from the browser
- View request/response schemas

### Database Inspection

To inspect the DuckDB database:

```python
import duckdb

con = duckdb.connect('markets.duckdb')

# View all markets
print(con.execute("SELECT * FROM polymarket_market_stats LIMIT 10").fetchdf())

# View available tables
print(con.execute("SHOW TABLES").fetchdf())

con.close()
```

### WebSocket Testing

To test WebSocket connections:

1. Open browser DevTools (F12)
2. Go to Network tab
3. Filter by WS (WebSocket)
4. Open a market detail page
5. You should see a WebSocket connection established

## Production Deployment

### Backend

For production, use a production-grade ASGI server:

```bash
# Install gunicorn with uvicorn worker
pip install gunicorn

# Run with multiple workers
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Frontend

Build the frontend for production:

```bash
npm run build
```

This creates a `dist/` folder that can be served by any static file server:

```bash
# Using Python
python -m http.server -d dist 8080

# Using Node.js serve
npx serve -s dist -p 8080

# Using nginx, configure to serve the dist/ folder
```

## Environment Variables

### Backend (.env)

```env
# Database
DUCKDB_PATH=markets.duckdb

# API Settings
API_HOST=0.0.0.0
API_PORT=8000
CORS_ORIGINS=http://localhost:5173,http://localhost:3000

# Polymarket API
GAMMA_BASE=https://gamma-api.polymarket.com
CLOB_BASE=https://clob.polymarket.com
REQUEST_TIMEOUT=30
MAX_RETRIES=3

# Analytics
BASE_RATE=0.50
DEFAULT_DEPTH=10
DEFAULT_FIDELITY=60
```

### Frontend (.env)

```env
VITE_API_BASE_URL=http://localhost:8000
VITE_WS_BASE_URL=ws://localhost:8000
```

## Next Steps

- Explore the dashboard and extract some markets
- Check out the API documentation
- Read the README.md for feature details
- Start building your trading strategies!

## Support

If you encounter issues:

1. Check this SETUP.md guide
2. Review the main README.md
3. Check backend logs in the terminal
4. Check browser console for frontend errors
5. Open an issue on GitHub

Happy trading! 🚀
