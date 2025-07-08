# SimVestor - AI-Powered Thematic Investment Simulator

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)]([https://simvestor.streamlit.app](https://simvestor-v1.streamlit.app/))

## 🚀 Overview

SimVestor is an AI-powered thematic investment simulator that helps users analyze past investment performance, compare portfolios, and predict future trends. Built with Streamlit and modern ML techniques, featuring robust data handling and comprehensive analytics.

**🏗️ Modular Architecture**: The app is built with a clean, modular structure for easy maintenance and extensibility.

## ✨ Features

### 🎯 **Theme-Based Investment Selection**
- **80+ Investment Themes** across 10 categories
- **Smart Theme Categorization**: Technology, Energy, Healthcare, Consumer, Financial, Industrial, Communications, Market Indices, Global Markets, Popular Stocks
- **Auto Theme-Ticker Mapping** with intelligent suggestions
- **Custom Ticker Input** with validation

### 📊 **Historical Investment Simulation**
- **Real Market Data** from Yahoo Finance API with robust fallback
- **Multi-Strategy Data Fetching** with exponential backoff retry logic
- **Sample Data Generation** for demonstration when API is rate-limited
- **Investment Performance Calculation** with detailed metrics

### 📈 **Advanced Portfolio Management**
- **Portfolio Tracking**: Add investments to compare performance
- **Multi-Investment Comparison**: Side-by-side analysis
- **Portfolio Summary Dashboard** with total returns
- **Benchmark Comparison** against S&P 500
- **Export Functionality** (JSON/CSV formats)

### 🔬 **Advanced Analytics Suite**
- **Technical Indicators**: RSI, Moving Averages, Bollinger Bands, Volume Analysis
- **AI-Generated Insights**: Performance analysis, risk assessment, sector insights
- **Market News Integration**: Real-time news fetching for stocks
- **Data Quality Validation**: Comprehensive data health checks

### 🤖 **AI-Powered Predictions**
- **Multiple ML Models**: Random Forest, Linear Regression with model comparison
- **Technical Feature Engineering**: RSI, Moving Averages, Price Momentum
- **Prediction Accuracy Metrics** with confidence intervals
- **Interactive Prediction Charts** with historical overlay

### 📊 **Comprehensive Risk Analysis**
- **Volatility Analysis**: Annualized volatility with risk categorization
- **Maximum Drawdown**: Peak-to-trough decline analysis
- **Sharpe Ratio**: Risk-adjusted return calculation
- **Alpha Calculation**: Excess return over benchmark
- **Detailed Risk Metrics Dashboard**

### 🛡️ **Robust Error Handling**
- **Enhanced Error Categorization**: Rate limits, network issues, invalid tickers
- **Intelligent Fallback Systems**: Multiple data source strategies
- **Connection Testing**: Real-time API status checking
- **Data Source Status Tracking**: Live/Limited/Sample data indicators

## 🔧 Technology Stack

### **Data & Analysis**
- `yfinance==0.2.54`: Stable stock data collection with robust error handling
- `pandas`, `numpy`: Advanced data processing and analysis
- `plotly`: Interactive and responsive charting
- `streamlit`: Modern web app framework with real-time updates

### **Machine Learning**
- `scikit-learn`: Multiple ML models with automated selection
- Technical indicators for feature engineering
- Performance comparison and model optimization
- Prediction accuracy validation

### **Enhanced Features**
- `logging`: Comprehensive error tracking and debugging
- `json`: Data export and serialization
- `typing`: Type hints for code reliability
- Portfolio management with session state persistence

## 🏗️ Modular Architecture

SimVestor features a clean, modular architecture for easy maintenance and extensibility:

```
SimVestor/
├── app.py                    # Main Streamlit application
├── modules/                  # Modular components
│   ├── data_fetcher.py      # Data fetching with progress bars
│   ├── analysis.py          # Financial calculations & ML
│   ├── visualization.py     # Charts and data presentation  
│   ├── news.py              # News fetching with rate limits
│   ├── portfolio.py         # Portfolio management
│   └── utils.py             # Utilities and configurations
├── requirements.txt         # Dependencies
└── README.md               # Documentation
```

### Module Benefits
- **🔧 Easy Maintenance**: Each module handles specific functionality
- **🔄 Reusable Components**: Modules can be imported in other projects  
- **🧪 Better Testing**: Individual modules can be tested independently
- **⚡ Faster Development**: Easier to find and modify specific features
- **🛡️ Isolated Error Handling**: Better error management per module

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- Internet connection for real-time data

### Local Installation

```bash
# Clone repository
git clone https://github.com/yourusername/simvestor.git
cd simvestor

# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run app.py
```

### Docker Installation

```bash
# Build Docker image
docker build -t simvestor .

# Run container
docker run -p 8501:8501 simvestor
```

### Online Access
Visit: [SimVestor App](https://simvestor.streamlit.app)

## 📊 How to Use

### 1. **Theme Selection**
- **Browse by Category**: Choose from 10 organized categories
- **Search All Themes**: Search through 80+ available themes
- **Custom Ticker**: Enter any valid stock symbol

### 2. **Investment Configuration**
- **Start Date**: Choose your investment entry point (up to 5 years back)
- **Investment Amount**: Set your hypothetical investment ($100 - $1,000,000)
- **Analysis Options**: Enable AI predictions, choose prediction timeframe

### 3. **Run Analysis**
- Click **"Run Simulation"** to fetch data and calculate returns
- View comprehensive results including charts, metrics, and insights
- Use **"Add to Portfolio"** to track multiple investments

### 4. **Advanced Features**
- **Portfolio Tracking**: Compare multiple investments side-by-side
- **Benchmark Comparison**: See how your investment performed vs S&P 500
- **Technical Analysis**: View RSI, moving averages, and other indicators
- **AI Insights**: Get automated investment insights and recommendations
- **Export Data**: Download results as JSON or CSV files

## 🎯 Investment Theme Categories

### 💻 **Technology & Innovation**
- Artificial Intelligence → NVDA
- Cloud Computing → MSFT
- Cybersecurity → CRWD
- Fintech → PYPL
- Semiconductor → NVDA
- Software → MSFT

### 🔋 **Energy & Environment**
- Clean Energy → TSLA
- Electric Vehicles → TSLA
- Solar Energy → ENPH
- Renewable Energy → ICLN
- Oil & Gas → XOM

### 🏥 **Healthcare & Biotech**
- Healthcare → JNJ
- Biotechnology → GILD
- Pharmaceuticals → PFE
- Medical Devices → JNJ
- Genomics → ARKG

### 🛍️ **Consumer & Lifestyle**
- Gaming → NVDA
- Streaming → NFLX
- E-commerce → AMZN
- Social Media → META
- Travel → ABNB

### 📊 **Market Indices**
- S&P 500 → SPY
- NASDAQ → QQQ
- Dow Jones → DIA
- Small Cap → IWM

### 🌍 **Global Markets**
- Emerging Markets → EEM
- China → FXI
- Europe → EFA
- Japan → EWJ
- India → INDA

## 🤖 AI Prediction System

### **Multi-Model Approach**
The app automatically selects the best-performing model from:

1. **Linear Regression**: Trend-based predictions
2. **Random Forest**: Ensemble learning for complex patterns
3. **Model Selection**: Automatic best-model selection based on validation performance

### **Technical Features**
- **Moving Averages**: 7-day, 21-day trend analysis
- **RSI (14-period)**: Momentum oscillator for overbought/oversold conditions
- **Price Momentum**: Recent price change analysis
- **Validation**: Cross-validation with accuracy metrics

### **Prediction Output**
- **30-60 day forecasts** with confidence intervals
- **Accuracy metrics** and model performance indicators
- **Visual charts** overlaying predictions on historical data
- **Risk warnings** and disclaimer notices

## 📊 Analytics Dashboard

### **Performance Metrics**
- Initial vs Final Investment Value
- Total Return ($ and %)
- Annualized Return
- Risk-Adjusted Return

### **Risk Analysis**
- **Volatility**: Annualized standard deviation
- **Maximum Drawdown**: Peak-to-trough decline
- **Sharpe Ratio**: Risk-adjusted return metric
- **Value at Risk**: Potential loss estimation

### **Technical Indicators**
- **RSI**: Relative Strength Index for momentum
- **Moving Averages**: 20, 50, 200-day trends
- **Bollinger Bands**: Volatility bands
- **Volume Analysis**: Trading volume patterns

### **Portfolio Features**
- **Multi-Investment Tracking**: Compare up to 10 investments
- **Portfolio Summary**: Total returns and allocation
- **Benchmark Comparison**: Performance vs S&P 500
- **Export Options**: JSON and CSV downloads

## 🛡️ Data Quality & Reliability

### **Data Sources**
- **Primary**: Yahoo Finance API (yfinance 0.2.54)
- **Fallback**: Sample data for demonstration
- **Validation**: Comprehensive data quality checks

### **Error Handling**
- **Rate Limit Management**: Intelligent retry with exponential backoff
- **Network Resilience**: Multiple API strategies and fallbacks
- **Data Validation**: Quality checks and completeness metrics
- **User Feedback**: Clear error messages and suggestions

### **Connection Testing**
- Real-time API status checking
- Multiple ticker validation
- Data source status indicators
- Network troubleshooting guidance

## ⚠️ Important Disclaimers

- **Educational Purpose Only**: This tool is for educational and research purposes
- **Not Investment Advice**: Do not use for actual investment decisions
- **Past Performance**: Does not guarantee future results
- **Prediction Accuracy**: ML predictions are estimates with inherent uncertainty
- **Data Limitations**: Yahoo Finance rate limits may affect real-time data availability

## � Recent Updates (v2.0)

### **New Features**
- ✅ Portfolio tracking and comparison
- ✅ S&P 500 benchmark comparison
- ✅ Advanced technical indicators
- ✅ AI-generated investment insights
- ✅ Real-time news integration
- ✅ Data quality validation
- ✅ Enhanced error handling
- ✅ Export functionality (JSON/CSV)

### **Improvements**
- ✅ Robust data fetching with fallbacks
- ✅ Better UI/UX with organized categories
- ✅ Comprehensive analytics dashboard
- ✅ Performance optimizations
- ✅ Enhanced documentation

## 🔄 Roadmap

### **Planned Features**
- [ ] **Options Analysis**: Call/put option pricing and Greeks
- [ ] **Crypto Support**: Bitcoin, Ethereum, and altcoin analysis
- [ ] **ESG Scoring**: Environmental, Social, Governance metrics
- [ ] **Sector Rotation**: Automated sector performance analysis
- [ ] **Monte Carlo Simulation**: Risk scenario modeling
- [ ] **Custom Alerts**: Price and performance notifications
- [ ] **Mobile App**: React Native mobile application

### **Technical Improvements**
- [ ] **Real-time WebSocket**: Live price updates
- [ ] **Database Integration**: PostgreSQL for data persistence
- [ ] **API Rate Optimization**: Professional data sources
- [ ] **Advanced ML**: LSTM and transformer models
- [ ] **Backtesting Engine**: Strategy performance testing

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [yfinance](https://github.com/ranaroussi/yfinance) for financial data
- [Streamlit](https://streamlit.io/) for the amazing web framework
- [Plotly](https://plotly.com/) for interactive visualizations
- [scikit-learn](https://scikit-learn.org/) for machine learning capabilities

---

**Built with ❤️ by the SimVestor Team**

[📈 Try SimVestor Now](https://simvestor.streamlit.app)
