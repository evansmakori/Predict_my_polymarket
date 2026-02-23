# 🚀 Quick Start Guide

Get the Polymarket Trading Dashboard running in 5 minutes!

## Prerequisites

- Python 3.12+
- Node.js 18+
- 5 minutes of your time ⏰

## Step 1: Backend (2 minutes)

```bash
# Navigate to backend
cd polymarket-dashboard/backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the server
python run.py
```

✅ Backend running at http://localhost:8000

## Step 2: Frontend (2 minutes)

**Open a NEW terminal window**, then:

```bash
# Navigate to frontend
cd polymarket-dashboard/frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

✅ Frontend running at http://localhost:5173

## Step 3: Extract Your First Market (1 minute)

1. Open http://localhost:5173 in your browser
2. Click **"Extract Market"** in the navigation
3. Paste a Polymarket URL, for example:
   ```
   https://polymarket.com/event/presidential-election-winner-2024
   ```
4. Click **"Extract Data"**
5. Wait ~30 seconds for extraction
6. Click the market link to view analytics!

## 🎉 You're Done!

You now have a fully functional trading dashboard with:
- ✅ Real-time market data
- ✅ Advanced analytics
- ✅ Trading signals
- ✅ Interactive charts
- ✅ Live orderbook

## Next Steps

- Extract more markets
- Explore the analytics
- Check out the trading signals
- Read the full [README.md](README.md) for details

## Troubleshooting

**Backend won't start?**
```bash
# Make sure you're in the venv
source venv/bin/activate
pip install -r requirements.txt
```

**Frontend won't start?**
```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
```

**Need more help?** Check [SETUP.md](SETUP.md) for detailed instructions.
