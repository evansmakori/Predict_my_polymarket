# 🎯 Polymarket Trading Dashboard

A real-time web application for monitoring Polymarket prediction markets with advanced analytics and trading signals.

## 🌟 Features

- **Market Explorer**: Browse active Polymarket events/markets with filters (category, liquidity, volume)
- **Live Analytics Panel**: Display key metrics (yes/no prices, spreads, volume, liquidity)
- **Trading Signals**: Visual indicators for long/short opportunities based on advanced algorithms
- **Price Charts**: Interactive time-series charts with technical indicators (MA, EMA, volatility)
- **Orderbook Visualizer**: Real-time bid/ask depth charts
- **Risk Indicators**: "Degen risk" score, overconfidence flags, slippage estimates
- **Watchlist**: Save and track favorite markets
- **Historical Analysis**: Query DuckDB for past market performance

## 🏗️ Tech Stack

### Backend
- **FastAPI**: High-performance async Python web framework
- **DuckDB**: Embedded analytics database
- **WebSockets**: Real-time data streaming
- **Pandas/NumPy**: Data analysis

### Frontend
- **React**: Modern UI framework
- **Recharts**: Beautiful, responsive charts
- **TailwindCSS**: Utility-first CSS framework
- **React Query**: Data fetching and caching

## 📁 Project Structure

```
polymarket-dashboard/
├── backend/
│   ├── app/
│   │   ├── api/              # API routes
│   │   ├── core/             # Core business logic from notebook
│   │   ├── models/           # Data models
│   │   ├── services/         # Business logic services
│   │   └── main.py           # FastAPI application
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── components/       # React components
│   │   ├── pages/            # Page components
│   │   ├── hooks/            # Custom React hooks
│   │   ├── services/         # API services
│   │   └── App.jsx
│   ├── package.json
│   └── vite.config.js
└── README.md
```

## 🚀 Quick Start

### Prerequisites
- Python 3.12+
- Node.js 18+
- npm or yarn

### Backend Setup

1. Navigate to backend directory:
```bash
cd polymarket-dashboard/backend
```

2. Create virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run the backend:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Backend will be available at: http://localhost:8000

### Frontend Setup

1. Navigate to frontend directory:
```bash
cd polymarket-dashboard/frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start development server:
```bash
npm run dev
```

Frontend will be available at: http://localhost:5173

## 📚 API Documentation

Once the backend is running, visit:
- **Interactive API Docs**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc

### Key Endpoints

- `GET /api/markets` - List all markets with filters
- `GET /api/markets/{market_id}` - Get market details
- `GET /api/markets/{market_id}/stats` - Get market statistics
- `GET /api/markets/{market_id}/orderbook` - Get orderbook data
- `GET /api/markets/{market_id}/history` - Get price history
- `POST /api/markets/extract` - Extract data from Polymarket URL
- `WS /ws/markets/{market_id}` - WebSocket for real-time updates

## 🔧 Configuration

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

## 🎨 Features Overview

### 1. Market Explorer
- Search and filter markets by category, liquidity, volume
- Sort by various metrics
- Quick view of key statistics

### 2. Market Detail View
- Comprehensive market information
- Real-time price updates
- Orderbook visualization
- Historical price charts

### 3. Trading Signals
- **Long Signal**: When expected value > 10bp and low volatility
- **Short Signal**: When expected value < -10bp and low volatility
- **No Trade**: Insufficient edge or high volatility

### 4. Risk Analysis
- **Degen Risk Score**: Composite of spread, momentum, and liquidity
- **Late Overconfidence**: Detects markets with extreme prices (>90%) and imbalanced orderbooks
- **Slippage Estimates**: Shows expected slippage for $1k and $10k orders

## 📊 Analytics Explained

### Computed Metrics

- **Volatility (1w)**: Rolling 20-period standard deviation of returns
- **Moving Averages**: 24-period (short) and 96-period (long) MAs
- **EMA Slope**: Exponential moving average trend slope
- **Sentiment Momentum**: Regression slope of price over time
- **Orderbook Imbalance**: (bid_volume - ask_volume) / total_volume
- **Fair Value**: Bayesian-adjusted price using base rate and momentum
- **Expected Value**: fair_value - current_price
- **Kelly Fraction**: Optimal bet size (scaled by 0.5 for safety)

## 🔄 Real-time Updates

The dashboard uses WebSockets to stream live updates:
- Price changes
- Orderbook updates
- New trading signals
- Volume/liquidity changes

Updates are throttled to prevent overwhelming the client (max 1 update/second per market).

## 🛠️ Development

### Running Tests
```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

### Building for Production

#### Backend
```bash
cd backend
pip install -r requirements.txt
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker
```

#### Frontend
```bash
cd frontend
npm run build
# Serve the dist/ folder with your preferred static server
```

## 📝 License

MIT License - feel free to use this for your trading analysis!

## ⚠️ Disclaimer

This tool is for educational and informational purposes only. It does not constitute financial advice. 
Always do your own research before trading on prediction markets.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📧 Support

For issues or questions, please open an issue on GitHub.
