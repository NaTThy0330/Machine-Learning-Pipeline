# Gold ML Trading Bot - XAUUSD Automated Trading System

## Overview
Machine Learning-powered automated trading bot for Gold (XAUUSD) using XGBoost, technical analysis, macro indicators, and session-aware trading.

**Duration:** 6 sprints over ~12 weeks  
**Tech Stack:** Python 3.10+, XGBoost, OANDA API, FRED API, yfinance  
**Cost:** 100% Free

## Quick Start

### Prerequisites
- Python 3.10+
- Virtual environment (venv)
- OANDA Practice Account (free)
- FRED API Key (free)

### Setup

1. **Activate virtual environment:**
```bash
source venv/bin/activate
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Configure environment:**
   - Edit `.env` with your OANDA and FRED API credentials
   - Never commit `.env` to git

4. **Verify setup:**
```bash
python3 scripts/verify_setup.py
```

## Project Structure

```
gold_ml_bot/
├── data/              # Raw XAUUSD price data (.parquet)
├── features/          # Feature-engineered datasets
├── models/            # Trained XGBoost models
├── notebooks/         # Jupyter notebooks for exploration
├── scripts/           # Python scripts
│   ├── collect_gold_ohlcv.py
│   ├── feature_engineering.py
│   ├── train_model.py
│   ├── live_gold_bot.py
│   └── news_filter.py
├── logs/              # Trading bot logs
├── .env               # API keys (DO NOT COMMIT)
├── .gitignore         # Ignore sensitive files
├── requirements.txt   # Python dependencies
└── README.md          # This file
```

## Sprint Roadmap

- **Sprint 1:** Setup & Install (Done ✓)
- **Sprint 2:** Data Collection (3+ years XAUUSD)
- **Sprint 3:** Feature Engineering
- **Sprint 4:** Train & Validate Model (Accuracy > 52%)
- **Sprint 5:** Paper Trading Bot
- **Sprint 6:** Monitor & Improve

## Important Configuration

Edit `.env` with:
- `OANDA_API_KEY` - From https://oanda.com
- `OANDA_ACCOUNT_ID` - Your practice account ID
- `FRED_API_KEY` - From https://fred.stlouisfed.org

## Risk Management

- **Stop Loss:** 0.5% (Gold-specific, lower than BTC)
- **Take Profit:** 1.0% (Risk:Reward = 1:2)
- **Session Filter:** Trade only 08:00-22:00 GMT (London/NY)
- **News Filter:** Pause 30min before/after NFP/CPI/FOMC
- **Max Position:** Never exceed 20% of portfolio

## Gold-Specific Features

✓ Real Interest Rate inverse relationship  
✓ DXY strength impact  
✓ Session-aware trading (London/NY preferred)  
✓ News event filters  
✓ Reduced volatility indicators (vs BTC)  
✓ No weekend trading  

## Free Resources

- **Data:** MetaTrader5, OANDA API, yfinance
- **ML:** XGBoost, scikit-learn
- **Macro:** FRED API
- **Trading:** OANDA Practice Account
- **Compute:** Google Colab (GPU)

## Documentation

See `summary.md` for complete sprint-by-sprint details.

## Disclaimer

This is an educational project. Trading Gold CFDs involves risk. Always:
- Paper trade minimum 3 months before real money
- Never risk more than you can afford to lose
- Use proper risk management (stop losses, position sizing)
- Backtest thoroughly before deployment

---

Created with ❤️ for automated Gold trading research.
