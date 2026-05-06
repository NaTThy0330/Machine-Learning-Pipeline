# GOLD ML TRADING BOT - Complete Summary

## Project Overview

**Project Name:** GOLD ML TRADING BOT  
**Target Asset:** XAUUSD (Gold)  
**Duration:** ~12 weeks  
**Total Sprints:** 6  
**Tech Stack:** Python, XGBoost, OANDA API, MetaTrader5, FRED API  
**Cost:** 100% Free  

### Key Differences: Bitcoin → Gold Migration

This project adapts a Bitcoin ML trading bot specifically for Gold (XAUUSD) trading. Major changes:

- **Data Sources:** Binance/ccxt → OANDA API or MetaTrader5 (Gold not on crypto exchanges)
- **Sentiment Analysis:** Reddit Crypto → USD/Geopolitical news + COT (Commitment of Traders) Reports
- **Macro Features:** Added Real Interest Rate, DXY Strength, Inflation Expectations, Gold ETF Flows
- **Technical Indicators:** Adjusted ATR and Bollinger Bands Window (Gold has lower volatility than BTC)
- **Paper Trading:** Binance Testnet → OANDA Practice Account (supports Gold CFDs)
- **Session Filter:** Added Trading Session Feature (London/NY) - Gold moves differently by session

---

## Sprint Overview

| Sprint | Name | Duration | Deliverable | Status |
|--------|------|----------|-------------|--------|
| 1 | Setup & Installation | Week 1-2 | Ready Environment | Pending |
| 2 | Data Collection (OHLCV) | Week 3-4 | 3+ years XAUUSD data | Pending |
| 3 | Feature Engineering | Week 5-6 | Training-ready Dataset | Pending |
| 4 | Train & Validate Model | Week 7-8 | Model (Accuracy > 52%) | Pending |
| 5 | Paper Trading Bot | Week 9-10 | Bot on Demo Account | Pending |
| 6 | Monitor & Improve | Week 11-12 | Production System | Pending |

---

## SPRINT 1: Setup & Installation

**Duration:** 2 weeks (Week 1-2)  
**Goal:** Fully functional development environment

### Tasks

**Task 1.1 - Install Python 3.10+**
- Download Python 3.10/3.11 from https://python.org/downloads
- Check "Add Python to PATH" (Windows)
- Verify: `python --version`

**Task 1.2 - Install VS Code**
- Download from https://code.visualstudio.com
- Install Extensions: Python (Microsoft), Jupyter, GitLens, Indent Rainbow

**Task 1.3 - Create Project Structure & Virtual Environment**
```bash
mkdir gold_ml_bot
cd gold_ml_bot
python -m venv venv
# Windows: venv\Scripts\activate
# Mac/Linux: source venv/bin/activate
```

**Task 1.4 - Install Python Libraries**

Core libraries:
```bash
pip install pandas numpy ta scikit-learn xgboost
pip install python-dotenv requests matplotlib jupyter
pip install pyarrow fastparquet yfinance
```

Gold-specific libraries:
```bash
pip install MetaTrader5      # Fetch XAUUSD from MT5
pip install oandapyV20       # OANDA API for Paper Trading
```

Library differences from Bitcoin plan:
- **MetaTrader5** - Free XAUUSD historical data (requires MT5 installed)
- **oandapyV20** - OANDA API for Gold CFD paper trading
- **yfinance** - Backup source (GC=F - Gold Futures from Yahoo Finance)

**Task 1.5 - Register OANDA Practice Account**
- Go to https://oanda.com → Create free Practice Account (no real money)
- My Account > API Access > Generate API Token
- Create .env file:
```
OANDA_API_KEY=your_oanda_api_key
OANDA_ACCOUNT_ID=your_practice_account_id
FRED_API_KEY=your_fred_key
```

**Task 1.6 - Register FRED API**
- Register at https://fred.stlouisfed.org/docs/api/api_key.html
- Get free API Key
- Gold uses: DXY, Real Interest Rate, CPI, 10yr Treasury Yield (different from BTC)

**Task 1.7 - Project Folder Structure**
```
gold_ml_bot/
├── data/              # Raw XAUUSD data (.parquet)
├── features/          # Feature-engineered data
├── models/            # Trained models
├── notebooks/         # Jupyter Notebooks
├── scripts/           # Python scripts
├── logs/              # Execution logs
├── .env               # API keys (NO COMMIT)
└── requirements.txt
```

### Checklist Sprint 1
- [ ] Python 3.10+ installed
- [ ] VS Code with Python Extension installed
- [ ] Virtual Environment created & activated
- [ ] All libraries installed (MetaTrader5, oandapyV20)
- [ ] OANDA Practice Account created with API key
- [ ] FRED API key obtained
- [ ] Folder structure complete
- [ ] .gitignore includes .env

---

## SPRINT 2: Data Collection (Gold OHLCV)

**Duration:** 2 weeks (Week 3-4)  
**Goal:** 3+ years XAUUSD data + Gold-specific macro indicators

### Key Differences: Gold vs Bitcoin Data

- **No 24/7 trading** - Closed weekends (Sat 22:00 GMT to Sun 22:00 GMT)
- **Three free sources:** MT5 (broker), OANDA API, yfinance (GC=F futures)
- **Use 3+ years data** (longer trends than Bitcoin)
- **Volume caveat:** Tick Volume from brokers not reliable - use as proxy only

### Tasks

**Task 2.1 - Collect XAUUSD from MetaTrader5 (Primary)**

```python
# scripts/collect_gold_ohlcv_mt5.py
import MetaTrader5 as mt5
import pandas as pd
from datetime import datetime

mt5.initialize()

def fetch_gold_mt5(timeframe, years=3):
    tf_map = {'1h': mt5.TIMEFRAME_H1, '4h': mt5.TIMEFRAME_H4, '1d': mt5.TIMEFRAME_D1}
    rates = mt5.copy_rates_from_pos('XAUUSD', tf_map[timeframe], 0, years*365*24)
    df = pd.DataFrame(rates)
    df['timestamp'] = pd.to_datetime(df['time'], unit='s')
    df = df[['timestamp','open','high','low','close','tick_volume']]
    df.rename(columns={'tick_volume':'volume'}, inplace=True)
    # Filter out weekends
    df = df[df['timestamp'].dt.dayofweek < 5]
    return df

for tf in ['1h', '4h', '1d']:
    df = fetch_gold_mt5(tf)
    df.to_parquet(f'data/XAUUSD_{tf}.parquet', index=False)
    print(f'Saved XAUUSD_{tf}: {len(df)} rows')

mt5.shutdown()
```

**Task 2.2 - Fallback: Collect from yfinance**

```python
# scripts/collect_gold_yfinance.py
import yfinance as yf
import pandas as pd

gold = yf.download('GC=F', period='3y', interval='1h')
gold.reset_index(inplace=True)
gold.columns = ['timestamp','open','high','low','close','volume']
gold = gold[gold['timestamp'].dt.dayofweek < 5]  # Filter weekends
gold.to_parquet('data/XAUUSD_1h_yf.parquet', index=False)
print(f'YFinance Gold: {len(gold)} rows')
```

**Task 2.3 - Collect Macro Indicators from FRED (Gold-specific)**

```python
# scripts/collect_macro_gold.py
SERIES = {
    'DFF':           'fed_rate',          # Fed Funds Rate
    'CPIAUCSL':      'cpi',               # CPI Inflation
    'DTWEXBGS':      'dxy',               # US Dollar Index (Critical for Gold!)
    'T10YIE':        'inflation_exp',     # 10yr Inflation Expectations
    'DFII10':        'real_rate_10y',     # Real Interest Rate 10yr (Inverse to Gold!)
    'T10Y2Y':        'yield_spread',      # Yield Curve
    'GOLDAMGBD228NLBM': 'gold_fix',      # London Gold Fix
}
```

**⚠️ CRITICAL:** Real Interest Rate (DFII10) has **inverse relationship** with Gold - when real rates decrease, Gold typically rises. This is the most important macro feature for Gold ML.

---

## SPRINT 3: Feature Engineering (Gold)

**Duration:** 2 weeks (Week 5-6)  
**Goal:** Production-ready feature dataset

### Feature Categories

**Technical Features:**
- SMA/EMA (20, 50, 200-day)
- RSI, MACD, ATR (adjusted for Gold volatility)
- Bollinger Bands (adjusted window for Gold)
- Volume Momentum

**Macro Features (Gold-specific):**
- Real Interest Rate momentum
- DXY strength
- Inflation expectations vs actual CPI
- Yield curve slope

**Session Features:**

```python
def add_session_features(df):
    hour = df['timestamp'].dt.hour
    
    # London Session (08:00-17:00 GMT) - Most active
    df['session_london'] = ((hour >= 8) & (hour < 17)).astype(int)
    
    # New York Session (13:00-22:00 GMT)
    df['session_ny'] = ((hour >= 13) & (hour < 22)).astype(int)
    
    # Asian Session (00:00-08:00 GMT) - Least volatile
    df['session_asian'] = ((hour >= 0) & (hour < 8)).astype(int)
    
    # Day of Week (Gold has patterns Mon-Fri)
    df['day_of_week'] = df['timestamp'].dt.dayofweek
    df['is_friday'] = (df['day_of_week'] == 4).astype(int)  # NFP on Friday
    return df
```

**Real Interest Rate Feature (Most Important for Gold):**
- Real rate inverse relationship with Gold prices
- When rates fall → Gold rises
- Feature importance should be in Top 10

### Data Processing
- Split Train/Test by time (NOT random) - 60% train / 20% validation / 20% test
- Normalize features for XGBoost
- Handle extreme values (outliers)

---

## SPRINT 4: Train & Validate Model

**Duration:** 2 weeks (Week 7-8)  
**Goal:** Model with Accuracy > 52%

### Model: XGBoost Classifier

- **Input:** Engineered features (Technical + Session + Macro + COT)
- **Output:** Binary classification (1 = up, 0 = down)
- **Target:** Accuracy > 52% (above random 50%)

### Training Process
1. Train XGBoost with Gold feature list
2. Walk-Forward Validation (5 folds)
3. Target average accuracy > 52%
4. Feature importance analysis (Session & Real Rate should be Top 10)
5. Simulate P&L after accounting for spread
6. Save model to `models/gold_xgb_model.pkl`
7. Save feature importance visualization

### Checklist Sprint 4
- [ ] Train/Test split by time (not random)
- [ ] Train XGBoost with all Gold features
- [ ] Walk-Forward Validation (5 folds) complete
- [ ] Average Accuracy > 52%
- [ ] Feature Importance shows Session & Real Rate in Top 10
- [ ] P&L simulation still profitable after spread
- [ ] Model saved as models/gold_xgb_model.pkl
- [ ] Feature importance image saved

---

## SPRINT 5: Paper Trading Bot (Gold CFD)

**Duration:** 2 weeks (Week 9-10)  
**Goal:** Bot running on OANDA Practice Account

### Task 5.1 - Setup OANDA Practice API

```bash
pip install oandapyV20
```

.env file:
```
OANDA_API_KEY=your_practice_api_token
OANDA_ACCOUNT_ID=your_practice_account_id
OANDA_ENVIRONMENT=practice    # Use practice, NOT live
```

### Task 5.2 - Live Data from OANDA API

```python
# scripts/live_gold_bot.py
import oandapyV20
import oandapyV20.endpoints.instruments as instruments
import pickle, pandas as pd, time, os, ta
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
client = oandapyV20.API(access_token=os.getenv('OANDA_API_KEY'),
                        environment=os.getenv('OANDA_ENVIRONMENT'))

def get_live_gold_data(count=300):
    params = {'granularity': 'H1', 'count': count}
    r = instruments.InstrumentsCandles('XAU_USD', params=params)
    client.request(r)
    candles = r.response['candles']
    rows = []
    for c in candles:
        if c['complete']:
            rows.append({
                'timestamp': pd.Timestamp(c['time']),
                'open': float(c['mid']['o']),
                'high': float(c['mid']['h']),
                'low': float(c['mid']['l']),
                'close': float(c['mid']['c']),
                'volume': int(c['volume'])
            })
    df = pd.DataFrame(rows)
    df = add_technical_features(df)
    df = add_session_features(df)
    df.dropna(inplace=True)
    return df
```

### Task 5.3 - Paper Trade Logic with Gold Risk Rules

```python
class GoldPaperTrader:
    def __init__(self, balance=10000, units=10):  # 10 oz Gold
        self.balance = balance
        self.position = 0
        self.entry_price = 0
        self.units = units
        self.trades = []
        self.daily_loss = 0

    def execute(self, signal, price, proba):
        confidence = proba[1]
        if confidence < 0.60: 
            return   # Confidence Filter
        
        # Stop Loss Check
        if self.position > 0:
            loss_pct = (price - self.entry_price) / self.entry_price
            if loss_pct < -0.005:   # Gold Stop Loss = 0.5% (BTC uses 3%)
                print('STOP LOSS triggered!')
                self._sell(price)
                return
        
        if signal == 1 and self.position == 0:
            self._buy(price)
        elif signal == 0 and self.position > 0:
            self._sell(price)
```

### Task 5.4 - Session Filter (Trade only during London/NY)

```python
def should_trade(timestamp):
    hour = timestamp.hour
    # Only allow trading 08:00-22:00 GMT (London + NY sessions)
    return 8 <= hour < 22

# In main loop
if not should_trade(datetime.utcnow()):
    print('Outside trading hours — skipping')
    time.sleep(1800)
    continue
```

**CRITICAL:** Gold should ONLY trade during London (08:00-17:00 GMT) and NY (13:00-22:00 GMT) sessions. Spread is very high during Asian session (00:00-08:00 GMT).

### Checklist Sprint 5
- [ ] OANDA Practice Account created with API key
- [ ] Bot fetches live XAUUSD from OANDA API
- [ ] Session Filter working (no trading outside 08:00-22:00 GMT)
- [ ] Stop Loss set to 0.5% (appropriate for Gold)
- [ ] Paper Trade Logic working (BUY/SELL correct)
- [ ] Bot runs automatically & pauses outside session
- [ ] Log file updated every 1 hour
- [ ] Paper traded for at least 1 week, check P&L

---

## SPRINT 6: Monitor & Improve

**Duration:** 2 weeks (Week 11-12)  
**Goal:** Stable system with retrain & news filter

### Task 6.1 - News Event Filter (Gold-specific - NOT in Bitcoin plan)

Gold jumps 0.5-2% instantly on NFP, CPI, FOMC events. Must pause bot before major news:

```python
# scripts/news_filter.py
import requests, pandas as pd

HIGH_IMPACT_NEWS = ['Non-Farm', 'NFP', 'CPI', 'FOMC', 'Fed Rate', 'GDP']

def get_upcoming_news():
    # ForexFactory Calendar API (free)
    url = 'https://nfs.faireconomy.media/ff_calendar_thisweek.json'
    r = requests.get(url)
    events = r.json()
    high_impact = [e for e in events
                   if e['impact'] == 'High'
                   and any(k in e['title'] for k in HIGH_IMPACT_NEWS)]
    return high_impact

def is_news_window(current_time, news_events, minutes=30):
    for event in news_events:
        event_time = pd.Timestamp(event['date'])
        diff = abs((current_time - event_time).total_seconds() / 60)
        if diff <= minutes:
            print(f'NEWS FILTER: {event["title"]} — pausing bot')
            return True
    return False
```

### Task 6.2 - Dashboard & Gold-specific Metrics

```python
log = pd.read_csv('logs/bot_log.txt', names=['datetime','price','signal','portfolio'])

# Sharpe Ratio
returns = log['portfolio'].pct_change().dropna()
sharpe = returns.mean() / returns.std() * (252**0.5)
print(f'Sharpe Ratio: {sharpe:.2f}  (target > 1.0)')

# Max Drawdown
peak = log['portfolio'].cummax()
drawdown = (log['portfolio'] - peak) / peak
print(f'Max Drawdown: {drawdown.min()*100:.1f}%  (target < 10%)')

# Win Rate
wins = (returns > 0).sum()
print(f'Win Rate: {wins/len(returns)*100:.1f}%')
```

### Task 6.3 - Auto-Retrain (Monthly)

```python
# scripts/retrain_gold.py
def check_and_retrain():
    # Fetch new data from OANDA/MT5
    # Re-run Feature Engineering
    # Train new model
    # If new Walk-Forward Accuracy > old → replace model
    pass

# Cron: 0 0 1 * * python /path/to/scripts/retrain_gold.py
```

### Task 6.4 - Risk Management Rules (Gold-tuned)

- **Stop Loss:** 0.5% from entry (Bitcoin uses 3% - Gold lower volatility)
- **Take Profit:** 1.0% from entry (Risk:Reward = 1:2)
- **Daily Loss Limit:** If daily loss > 2%, stop bot
- **Confidence Threshold:** Trade only if Confidence > 60%
- **Session Filter:** Trade only 08:00-22:00 GMT
- **News Filter:** Pause 30 min before/after NFP, CPI, FOMC
- **Max Position:** Never > 20% of portfolio

### Checklist Sprint 6
- [ ] News Event Filter working (pauses before NFP/CPI/FOMC)
- [ ] Dashboard shows Sharpe Ratio & Max Drawdown
- [ ] Sharpe Ratio > 1.0 (viable system)
- [ ] Max Drawdown < 10%
- [ ] Retrain script configured (runs monthly)
- [ ] All Risk Rules implemented (Stop/TP/Confidence/Session/News)
- [ ] Paper traded for 4+ weeks minimum before real money
- [ ] Review: Sharpe > 1 and Return > 0% before going live

---

## ⚠️ BEFORE USING REAL MONEY - Gold CFD Risk Warnings

1. **Paper trade minimum 3 months** before considering real money
2. **Gold has high spread** vs Crypto - must calculate transaction costs in backtest
3. **Session timing is critical:** 
   - London Open (08:00-10:00 GMT) - Most volatile
   - NY Open (13:00-15:00 GMT) - Very volatile
   - Asian hours - High spread, low liquidity
4. **News events are dangerous:** NFP, CPI, FOMC cause 0.5-2% jumps
5. **Accuracy 55% ≠ Profit** - Must verify actual P&L after spread deduction
6. **Model degrades over time** - Retrain every 1-3 months mandatory

---

## Free Tools Used in This Project

| Task | Details | Tool/Library | Cost |
|------|---------|--------------|------|
| Programming | Main language | Python 3.10+ | Free |
| Code Editor | IDE | VS Code | Free |
| Gold Data | XAUUSD prices | MetaTrader5/OANDA API | Free |
| Backup Data | Fallback source | yfinance | Free |
| Data Processing | Data manipulation | pandas/numpy | Free |
| Technical Analysis | Gold indicators | ta library | Free |
| ML Model | Classification | XGBoost | Free |
| Model Evaluation | Metrics | scikit-learn | Free |
| Macro Data | Economic indicators | FRED API | Free |
| Paper Trading | Risk-free testing | OANDA Practice Account | Free |
| GPU Compute | Model training | Google Colab | Free |

**Total Project Cost: $0 / ฿0 - 100% FREE**

---

## Project Timeline

- **Week 1-2:** Setup environment & install dependencies
- **Week 3-4:** Collect 3+ years of XAUUSD data
- **Week 5-6:** Build technical, macro, and session features
- **Week 7-8:** Train XGBoost model, validate accuracy > 52%
- **Week 9-10:** Deploy paper trading bot on OANDA
- **Week 11-12:** Monitor performance, add news filter, setup retrain

**Total: ~12 weeks to production-ready system**

---

*Created by Claude - Anthropic | May 2026*
