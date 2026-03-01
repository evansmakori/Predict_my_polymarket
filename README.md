# Predict My Polymarket 🎯

A comprehensive real-time trading dashboard for Polymarket prediction markets with advanced risk analysis, scoring systems, and market intelligence features.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.9+-blue.svg)
![React](https://img.shields.io/badge/react-18.0+-blue.svg)

## 🌟 Features

### Core Functionality
- **Real-time Market Data**: Live updates from Polymarket API via WebSocket connections
- **Advanced Market Scoring**: Multi-dimensional risk and opportunity assessment system
- **Market Rankings**: Intelligent ranking system based on liquidity, volume, and risk metrics
- **Price Charts**: Interactive TradingView-style charts with technical indicators
- **Order Book Visualization**: Real-time bid/ask spreads and market depth analysis

### Advanced Analytics
- **Unified Risk Score**: Composite scoring system evaluating market quality and trading opportunities
- **Risk Alerts**: Automated alerts for high-risk market conditions
- **Liquidity Heatmap**: Visual representation of market liquidity across different markets
- **Score History Tracking**: Historical tracking of market scores over time
- **Market Metadata Analysis**: Deep insights into market structure and participant behavior

### Alert System
- **Low Liquidity Alerts**: Warnings for markets with insufficient liquidity
- **High Volatility Alerts**: Detection of unusual price movements
- **Spread Alerts**: Notifications for wide bid-ask spreads
- **Volume Alerts**: Tracking of unusual trading volume patterns

## 🏗️ Architecture

### Backend (Python/FastAPI)
- **FastAPI** framework for high-performance async API
- **WebSocket** support for real-time data streaming
- **SQLite** database for market data and score history
- **Polymarket API** integration for market data
- **Advanced scoring algorithms** for risk assessment

### Frontend (React/Vite)
- **React 18** with modern hooks and context API
- **TailwindCSS** for responsive styling
- **Recharts** for data visualization
- **Real-time WebSocket** client for live updates
- **Responsive design** optimized for desktop and mobile

## 📋 Prerequisites

- **Python 3.9+**
- **Node.js 16+** and npm
- **Docker** (optional, for containerized deployment)
- **Polymarket API access** (optional, for enhanced features)

## 🚀 Quick Start

### Method 1: Local Development

#### Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env

# Run the backend server
python run.py
```

The backend API will be available at `http://localhost:8000`

#### Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Copy environment template
cp .env.example .env

# Start development server
npm run dev
```

The frontend will be available at `http://localhost:5173`

### Method 2: Docker Deployment

```bash
# Build and start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

Access the application:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

### Method 3: GitHub Deployment Script

```bash
# Make the script executable
chmod +x DEPLOY_TO_GITHUB.sh

# Run deployment
./DEPLOY_TO_GITHUB.sh
```

## 📁 Project Structure

```
Predict_my_polymarket/
├── backend/
│   ├── app/
│   │   ├── api/            # API endpoints
│   │   │   ├── markets.py  # Market data endpoints
│   │   │   └── websocket.py # WebSocket handlers
│   │   ├── core/           # Core business logic
│   │   │   ├── scoring.py  # Market scoring algorithms
│   │   │   ├── alerts.py   # Alert generation system
│   │   │   ├── analytics.py # Analytics engine
│   │   │   └── polymarket.py # Polymarket API client
│   │   ├── models/         # Data models
│   │   └── services/       # Service layer
│   ├── requirements.txt    # Python dependencies
│   └── run.py             # Application entry point
├── frontend/
│   ├── src/
│   │   ├── components/    # React components
│   │   │   ├── UnifiedRiskScore.jsx
│   │   │   ├── RiskAlerts.jsx
│   │   │   ├── LiquidityHeatmap.jsx
│   │   │   ├── ScoreHistoryChart.jsx
│   │   │   └── ...
│   │   ├── pages/         # Page components
│   │   │   ├── Dashboard.jsx
│   │   │   ├── Rankings.jsx
│   │   │   └── MarketDetail.jsx
│   │   ├── services/      # API services
│   │   └── utils/         # Utility functions
│   ├── package.json       # Node dependencies
│   └── vite.config.js     # Vite configuration
├── docker-compose.yml     # Docker compose configuration
├── Dockerfile.backend     # Backend Docker image
├── Dockerfile.frontend    # Frontend Docker image
└── README.md             # This file
```

## 🎯 Key Components

### Backend Components

#### Scoring System
The platform uses a sophisticated multi-factor scoring algorithm:

- **Liquidity Score** (30%): Evaluates market depth and liquidity
- **Volume Score** (25%): Analyzes trading volume patterns
- **Volatility Score** (20%): Measures price stability
- **Spread Score** (15%): Assesses bid-ask spread efficiency
- **Market Quality** (10%): Overall market health indicators

See `backend/SCORING_SYSTEM.md` for detailed documentation.

#### Alert System
Real-time monitoring and alerts for:
- Low liquidity conditions
- High volatility events
- Wide spread warnings
- Unusual volume patterns

### Frontend Components

#### Dashboard
- Market overview with key metrics
- Real-time price updates
- Risk score indicators
- Active alerts panel

#### Rankings Page
- Sortable market rankings
- Multi-criteria filtering
- Score breakdown visualization
- Historical performance tracking

#### Market Detail
- Detailed market information
- Interactive price charts
- Order book depth
- Historical score trends
- Risk assessment breakdown

## 🔧 Configuration

### Backend Configuration

Edit `backend/.env`:

```env
# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
CORS_ORIGINS=http://localhost:5173,http://localhost:3000

# Database
DATABASE_URL=sqlite:///./polymarket.db

# Polymarket API (optional)
POLYMARKET_API_KEY=your_api_key_here

# Scoring Weights (optional customization)
LIQUIDITY_WEIGHT=0.30
VOLUME_WEIGHT=0.25
VOLATILITY_WEIGHT=0.20
```

### Frontend Configuration

Edit `frontend/.env`:

```env
VITE_API_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000
```

## 📊 API Documentation

Once the backend is running, visit `http://localhost:8000/docs` for interactive API documentation powered by Swagger/OpenAPI.

### Key Endpoints

- `GET /api/markets` - List all markets with scores
- `GET /api/markets/{market_id}` - Get market details
- `GET /api/markets/{market_id}/score-history` - Get score history
- `GET /api/markets/rankings` - Get ranked markets
- `WS /ws` - WebSocket for real-time updates

## 🧪 Testing

### Backend Tests

```bash
cd backend
pytest
```

### Frontend Tests

```bash
cd frontend
npm test
```

## 📈 Usage Examples

### Extract Market Data

Navigate to the Extract Market page to pull data from specific Polymarket URLs or search for markets by keywords.

### View Rankings

The Rankings page displays markets sorted by their unified risk score, helping identify the best trading opportunities.

### Monitor Alerts

The Alerts Panel shows real-time warnings about market conditions that may require attention.

### Analyze Historical Trends

Each market detail page includes historical score charts to track how market quality has evolved over time.

## 🤝 Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 Documentation

- [Scoring System](backend/SCORING_SYSTEM.md) - Detailed scoring algorithm documentation
- [Scoring Quickstart](backend/SCORING_QUICKSTART.md) - Quick guide to the scoring system
- [Advanced UI Features](ADVANCED_UI_FEATURES.md) - Frontend component guide
- [Scoring Features Implementation](SCORING_FEATURES_IMPLEMENTATION.md) - Implementation details

## 🛠️ Built With

### Backend
- [FastAPI](https://fastapi.tiangolo.com/) - Modern web framework
- [SQLAlchemy](https://www.sqlalchemy.org/) - SQL toolkit and ORM
- [Pydantic](https://pydantic-docs.helpmanual.io/) - Data validation
- [httpx](https://www.python-httpx.org/) - HTTP client
- [python-dotenv](https://github.com/theskumar/python-dotenv) - Environment management

### Frontend
- [React](https://reactjs.org/) - UI library
- [Vite](https://vitejs.dev/) - Build tool
- [TailwindCSS](https://tailwindcss.com/) - CSS framework
- [Recharts](https://recharts.org/) - Charting library
- [Axios](https://axios-http.com/) - HTTP client

## 🚀 Deployment

### Production Deployment

1. **Environment Variables**: Set production environment variables
2. **Database**: Configure production database (PostgreSQL recommended)
3. **Security**: Enable HTTPS and secure WebSocket connections
4. **Monitoring**: Set up logging and monitoring
5. **Scaling**: Use Docker Swarm or Kubernetes for scaling

### Deployment Options

- **Docker Compose**: Simple single-server deployment
- **Cloud Platforms**: Deploy to AWS, GCP, Azure, or DigitalOcean
- **Container Orchestration**: Kubernetes for large-scale deployments

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Polymarket for providing market data API
- FastAPI community for excellent documentation
- React community for amazing tools and libraries

## 📞 Support

For support, please:
- Open an issue on GitHub
- Check existing documentation
- Review the FAQ in the wiki

## 🔮 Roadmap

- [ ] Machine learning models for price prediction
- [ ] Advanced portfolio management features
- [ ] Social sentiment analysis integration
- [ ] Mobile app (React Native)
- [ ] Multi-chain support
- [ ] Advanced backtesting tools
- [ ] API rate limiting and caching
- [ ] User authentication and personalization

## ⚠️ Disclaimer

This tool is for informational purposes only. It does not constitute financial advice. Always do your own research before making trading decisions. Prediction markets involve risk, and you should only invest what you can afford to lose.

---

**Built with ❤️ for the Polymarket community**

*Star ⭐ this repository if you find it helpful!*
