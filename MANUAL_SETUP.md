# 🚀 Manual Setup Instructions

The automated installation is taking longer than expected. Follow these manual steps to get the dashboard running.

## Option 1: Using Startup Scripts (EASIEST)

### Terminal 1 - Start Backend

```bash
cd polymarket-dashboard
./START_BACKEND.sh
```

Wait for it to say "Application startup complete" - this means the server is running!

### Terminal 2 - Start Frontend

Open a **NEW** terminal, then:

```bash
cd polymarket-dashboard
./START_FRONTEND.sh
```

Wait for it to say "Local: http://localhost:5173"

### Open Browser

Go to: http://localhost:5173

---

## Option 2: Manual Step-by-Step

### Backend (Terminal 1)

```bash
cd polymarket-dashboard/backend

# Install packages in the existing env
cd ../..
env/bin/pip install fastapi uvicorn[standard] python-multipart websockets pydantic-settings aiofiles

# Go back to backend
cd polymarket-dashboard/backend

# Create .env file
cp .env.example .env

# Start server
../../env/bin/python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

**Success indicators:**
- You should see: `INFO:     Uvicorn running on http://0.0.0.0:8000`
- And: `INFO:     Application startup complete.`

### Frontend (Terminal 2)

Open a **NEW** terminal:

```bash
cd polymarket-dashboard/frontend

# Install dependencies
npm install

# Create .env file
cp .env.example .env

# Start dev server
npm run dev
```

**Success indicators:**
- You should see: `VITE v5.x.x ready in X ms`
- And: `➜  Local:   http://localhost:5173/`

---

## Troubleshooting

### Backend Issues

**"No module named fastapi"**
```bash
# Make sure you're using the correct Python
cd polymarket-dashboard/backend
../../env/bin/pip install fastapi uvicorn[standard] python-multipart websockets pydantic-settings aiofiles
../../env/bin/python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

**Port 8000 already in use**
```bash
# Kill any existing process on port 8000
lsof -ti:8000 | xargs kill -9

# Then start the server again
```

**Database error**
```bash
# The database will be created automatically
# Just make sure you're in the backend directory when running
```

### Frontend Issues

**"npm: command not found"**
```bash
# Install Node.js first
# Visit: https://nodejs.org/
```

**Installation fails**
```bash
# Clear cache and try again
cd polymarket-dashboard/frontend
rm -rf node_modules package-lock.json
npm cache clean --force
npm install
```

**Port 5173 already in use**
- Vite will automatically try port 5174, 5175, etc.
- Or you can specify a different port in vite.config.js

---

## Verify Everything is Working

### 1. Check Backend (should return JSON)
```bash
curl http://localhost:8000/health
```

Expected output:
```json
{"status":"ok","database":"healthy"}
```

### 2. Check Frontend
Open browser: http://localhost:5173

You should see the Polymarket Dashboard interface.

### 3. Check API Docs
Open browser: http://localhost:8000/docs

You should see interactive API documentation.

---

## Next Steps After Startup

1. **Extract a market:**
   - Click "Extract Market" in the navigation
   - Paste: `https://polymarket.com/event/presidential-election-winner-2024`
   - Click "Extract Data"
   - Wait 30-60 seconds

2. **View the dashboard:**
   - Go back to "Dashboard"
   - You should see the extracted market(s)
   - Click on a market to see detailed analytics

3. **Explore features:**
   - Check out the price charts
   - View the orderbook
   - Look at trading signals
   - Check risk metrics

---

## Still Having Issues?

### Check the logs

**Backend logs:**
- Look in the terminal where you ran the backend
- Errors will show in red
- Common issues: missing packages, port conflicts

**Frontend logs:**
- Look in the terminal where you ran npm run dev
- Also check browser console (F12 → Console tab)

### Common Issues

1. **Backend starts but frontend can't connect**
   - Make sure backend is on port 8000
   - Check frontend .env file has correct API URL
   - Check for CORS errors in browser console

2. **WebSocket not connecting**
   - This is normal until you open a market detail page
   - Check browser console for WebSocket errors
   - Make sure WS URL in frontend .env is correct

3. **No markets showing**
   - You need to extract markets first using "Extract Market" page
   - Markets are stored in `backend/markets.duckdb`
   - If database is corrupted, delete it and re-extract

---

## Quick Test

Once both servers are running, try this quick test:

```bash
# Test backend health
curl http://localhost:8000/health

# Test frontend
curl http://localhost:5173
```

Both should return responses (HTML for frontend, JSON for backend).

---

## Success! 🎉

If you see:
- ✅ Backend running on http://localhost:8000
- ✅ Frontend running on http://localhost:5173  
- ✅ Dashboard loads in browser
- ✅ Can extract a market successfully

**You're all set!** Start analyzing prediction markets! 📈
