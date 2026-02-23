# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-02-23

### Added
- Initial release of Polymarket Trading Dashboard
- FastAPI backend with complete Polymarket data extraction
- React frontend with Vite and TailwindCSS
- Real-time market data via WebSocket
- Advanced analytics:
  - Volatility calculation
  - Moving averages (short/long)
  - EMA slope analysis
  - Sentiment momentum
  - Liquidity scoring
  - Degen risk assessment
- Trading signals (long/short/no-trade)
- Interactive price charts with Recharts
- Orderbook visualization for YES/NO tokens
- Market extraction from Polymarket URLs
- DuckDB integration for data persistence
- RESTful API with OpenAPI documentation
- Docker support with docker-compose
- GitHub Actions CI/CD workflows
- Comprehensive documentation

### Features
- Market Explorer with filters
- Real-time price updates
- Market detail page with full analytics
- Dark mode support
- Responsive design
- Health check endpoints
- Error handling and validation
- CORS configuration

### Documentation
- README with quick start guide
- Setup instructions
- Manual setup guide
- GitHub deployment guide
- API documentation
- Contributing guidelines
- Security policy
- Test URLs and examples

## [Unreleased]

### Planned Features
- User authentication
- Watchlist/favorites persistence
- Portfolio tracking
- Custom alert notifications
- Advanced charting with technical indicators
- Market comparison tools
- Historical performance analytics
- Export data to CSV/Excel
- Mobile app (React Native)
- Rate limiting
- Redis caching layer
- PostgreSQL support (alternative to DuckDB)

---

For the full commit history, see the [GitHub repository](https://github.com/yourusername/polymarket-dashboard).
