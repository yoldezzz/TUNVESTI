# TUNVESTI ETL Pipeline - Complete Documentation
**Project:** Business Intelligence Dashboard for Tunisian Stock Market (BVMT)  
**Created:** December 23, 2025  
**Status:** Production Ready

---

## PROJECT OVERVIEW

### **Objective**
Build a comprehensive stock analysis platform for Tunisia's BVMT market that:
- Answers **14 business questions** (portfolio optimization, sector analysis, trends, dividend analysis)
- Calculates **10 key performance indicators** (returns, volatility, Sharpe ratio, P/E, dividend yield, ROE, correlation, RSI, market cap, beta)
- Provides **Power BI dashboard** with auto-updating daily data
- Supports **institutional investors** making data-driven decisions

### **Data Scope**
| Period | Coverage | Source | Frequency |
|--------|----------|--------|-----------|
| 2010-2022 | 12 years historical | Kaggle | One-time |
| 2025-ongoing | Daily updates | ilboursa.com scraper | Daily @ 3 PM |
| Current | ~90 stocks | BVMT/Ilboursa | All active |

### **Key Metrics Available**
- OHLCV (Open, High, Low, Close, Volume)  
- Daily Returns (%)  
- 30-day Rolling Volatility (annualized)  
- Dividend Yield (%)  
- Market Cap  
- TUNINDEX Index data  
- Stock Sectors & Company Names  

---

## ETL PIPELINE ARCHITECTURE

### **Five-Script Pipeline**

```
SCRIPT 01 (Load)
    ↓
SCRIPT 02 (Scrape Daily)
    ↓
SCRIPT 03 (Merge & Enrich) ← MAIN INTEGRATION
    ↓
SCRIPT 04 (Auto-Schedule)
    ↓
POWER BI Dashboard
```

---

## SCRIPT 01: Load Kaggle Historical Data

**File:** `scripts/01_load_kaggle_data.py`  
**Purpose:** Load 2010-2022 historical stock data from Kaggle CSV files  
**When to Run:** Once at project start (or when Kaggle data updates)

### Input
- 88 CSV files in `data/kaggle_source/` (one per stock)
- Columns: Ticker, Date, Open, High, Low, Close, Volume
- Format: Daily OHLCV data

### Process
1. Read all 88 CSV files from `data/kaggle_source/`
2. Standardize column names (uppercase)
3. Convert Date to datetime
4. Concatenate into single dataframe
5. Remove duplicates
6. Sort by Ticker, Date

### Output
```
data/historical_stocks_2010_2022.csv
├─ 187,987 rows (12 years × ~89 stocks)
├─ Columns: Ticker, Date, Open, High, Low, Close, Volume
└─ Date range: 2010-01-04 to 2022-12-30
```

### Example Run
```bash
cd "C:\Users\NOUIRA\Documents\junior\BI project"
.venv\Scripts\python scripts/01_load_kaggle_data.py
```

---

## SCRIPT 02: Scrape Daily ilboursa Data

**File:** `scripts/02_scrape_ilboursa_daily.py`  
**Purpose:** Daily web scraper collecting real-time market data from ilboursa.com  
**When to Run:** Daily @ 3 PM CET (Mon-Fri) via Script 04 Scheduler

### Input
- Website: `ilboursa.com` (public data, no authentication)
- Technology: Selenium + BeautifulSoup
- Browser: Headless Chrome (JavaScript rendering)

### Process
1. Initialize Selenium WebDriver (headless Chrome)
2. Navigate to ilboursa.com market quotes page
3. Extract 90 stocks with JavaScript rendering
4. **Data Quality Fixes:**
   - Remove non-breaking spaces (`\xa0` from HTML `&nbsp;`)
   - Handle French number format (commas → dots)
   - Parse volatility with +/- signs (3.13% format)
   - Parse market cap in millions (0.7M, 176.3M)
5. Validate OHLCV integrity
6. Save to timestamped CSV

### Output
```
output/daily_updates/updated_stocks_YYYY-MM-DD.csv
├─ 90 rows (one per active stock)
├─ Columns: Date, Ticker, Open, High, Low, Close, Volume, Volatility, Market_Cap_M
└─ Created daily at 3 PM
```

### Data Quality Checks Built In
- High >= Low (OHLCV integrity)
- Volume > 0 (sanity check)
- Price > 0 (not negative/NaN)
- No duplicate tickers per day

### Example Run
```bash
cd "C:\Users\NOUIRA\Documents\junior\BI project"
.venv\Scripts\python scripts/02_scrape_ilboursa_daily.py
```

**Recent Output Sample:**
```
Date         Ticker  Open    High    Low     Close   Volume  Volatility  Market_Cap_M
2025-12-23   TJARI   65.7    66.0    65.7    65.7    6490    1.52%       3285.0
2025-12-23   BIAT    107.49  109.9   109.0   109.0   1242    2.7%        4447.0
2025-12-23   AB      47.5    47.65   47.65   47.65   6576    0.53%       1664.0
```

---

## SCRIPT 03: Merge & Enrich Data (CRITICAL SCRIPT)

**File:** `scripts/03_merge_and_enrich_data.py`  
**Purpose:** Integrate all data sources + calculate derived metrics  
**When to Run:** Daily after Script 02 (via Script 04 Scheduler)  
**Duration:** ~5-10 seconds

### Input (5 Data Sources)

| Source | File | Purpose |
|--------|------|---------|
| Historical | `data/historical_stocks_2010_2022.csv` | 2010-2022 baseline |
| Daily Scrape | `output/daily_updates/updated_stocks_*.csv` | Current day data |
| Index | `data/Tunindex Historical Data.csv` | Market benchmark |
| Sectors | `data/sector_mapping.csv` | Company classification |
| Dividends | `data/dividend20217-2024.csv` | Annual per-share payouts |

### Processing Steps

#### **Step 1: Load & Clean**
```
Historical (187,987 rows) → Clean dates/prices
Daily (90 rows) → Remove spaces, fix decimals
TUNINDEX (3,969 rows) → Rename columns
Sectors (91 stocks) → Standardize tickers
Dividends (309 entries) → Convert to numeric
```

#### **Step 2: Merge Strategy**
```
1. CONCATENATE historical + daily stock data
   → 144,727 rows after dedup (remove last dups, keep latest)

2. BROADCAST TUNINDEX by Date
   → Join market index to every stock per date
   → 144,147 rows with index available

3. MERGE Sectors on Ticker
   → Add company name & sector classification
   → 80,822 rows with sector info

4. ADD Year, MERGE Dividends on (Ticker, Year)
   → Match annual dividend payouts
   → 21,769 rows with dividend yield > 0
   → Fill missing with 0
```

#### **Step 3: Derive Metrics**

##### **Daily Return (%)**
```
Formula: (Close_today - Close_yesterday) / Close_yesterday × 100
Where:   Per stock
Status: 99.9% complete (144,636 values)
Note:    First row per stock is NaN
```

##### **Volatility 30-Day (annualized)**
```
Formula: StdDev(Daily_Return[last 30 days]) × √252
Where:   √252 = annualization factor (trading days/year)
Status: 98.3% complete (142,238 values)
Note:    Needs 30 days of history, so starts ~1 month in
```

##### **Dividend Yield (%)**
```
Formula: (Annual_Dividend_Per_Share / Close_Price) × 100
Where:   Annual dividend from dividends CSV
Status: 100% complete (but 0 where no dividend paid)
Note:    Only positive for 21,769 rows with dividend data
```

##### **Average Volume 30-Day**
```
Formula: Mean(Volume[last 30 days])
Where:   Rolling average
Status: 98.3% complete (142,320 values)
Note:    Useful for liquidity analysis
```

##### **TUNINDEX Daily Return (%)**
```
Formula: (TUNINDEX_Close_today - TUNINDEX_Close_yesterday) / TUNINDEX_Close_yesterday × 100
Where:   Market index, same as stock returns
Status: 99.6% complete (144,286 values)
Note:    For correlation & beta calculations
```

### Output (3 Files)

#### **1. fact_stock_daily.csv** ← USE THIS FOR POWER BI
```
Columns: date, ticker, open, high, low, close, volume,
         daily_return_pct, volatility_30d, dividend_yield_pct,
         avg_volume_30d, tunindex_close, market_cap_m

Rows:    144,727 (all stocks × all dates)
Size:    15.68 MB
Purpose: Fact table for Power BI star schema
```

**Sample:**
```
date,ticker,open,high,low,close,volume,daily_return_pct,volatility_30d,dividend_yield_pct,avg_volume_30d,tunindex_close,market_cap_m
2010-01-04,AB,26.5,26.65,26.5,26.65,736.0,NaN,NaN,0.0,NaN,NaN,NaN
2010-01-05,AB,26.65,27.35,26.5,27.2,14632.0,2.06,NaN,0.0,NaN,NaN,NaN
2025-12-23,TJARI,65.7,66.0,65.7,65.7,6490,1.52,30.45,1.23,4521.3,8234.5,3285.0
```

#### **2. dim_date.csv** (Dimension Table)
```
Columns: date, year, month, quarter, week, day_of_week, day_name, is_trading_day

Rows:    3,236 unique trading dates
Size:    0.11 MB
Purpose: Time dimension for Power BI time intelligence
```

#### **3. dim_stock.csv** (Dimension Table)
```
Columns: ticker, sector, company

Rows:    91 unique stocks
Size:    0.01 MB
Purpose: Stock dimension for Power BI filtering/grouping
```

### Example Run
```bash
cd "C:\Users\NOUIRA\Documents\junior\BI project"
.venv\Scripts\python scripts/03_merge_and_enrich_data.py
```

**Console Output:**
```
- Loaded historical: 146,246 rows
- Loaded daily: 90 rows
- Merged OHLCV: 144,727 rows
- Added TUNINDEX: 144,147 rows (99.6%)
- Added sectors: 80,822 rows
- Added dividends: 21,769 non-zero
- Calculated daily_return: 144,636 values (99.9%)
- Calculated volatility_30d: 142,238 values (98.3%)
- Saved fact_stock_daily.csv (15.68 MB)
- Saved dim_date.csv (0.11 MB)
- Saved dim_stock.csv (0.01 MB)
```

---

## SCRIPT 04: Auto-Scheduler

**File:** `scripts/04_scheduler.py`  
**Purpose:** Automate daily execution of Scripts 02 + 03  
**When to Deploy:** After initial manual testing

### Schedule
```
Every Monday-Friday @ 3:00 PM CET
├─ Run Script 02 (Scrape ilboursa)
├─ Wait for completion
└─ Run Script 03 (Merge & Enrich)

Output: 90 new stock records + complete dataset refresh
```

### Implementation
Uses Python `schedule` library:
```python
schedule.every().monday.at("15:00").do(run_scripts)
schedule.every().tuesday.at("15:00").do(run_scripts)
# ... etc
```

### Example Run
```bash
cd "C:\Users\NOUIRA\Documents\junior\BI project"
.venv\Scripts\python scripts/04_scheduler.py
# Runs in background, check logs in output/scheduler.log
```

---

## PROJECT STRUCTURE

```
BI project/
├─ scripts/
│  ├─ 00_system_check.py           (Verify environment)
│  ├─ 01_load_kaggle_data.py       (Load 2010-2022 historical)
│  ├─ 02_scrape_ilboursa_daily.py  (Daily scraper, web automation)
│  ├─ 03_merge_and_enrich_data.py  (MAIN: merge all sources + metrics)
│  └─ 04_scheduler.py               (Auto-run Scripts 02+03 daily)
│
├─ data/
│  ├─ historical_stocks_2010_2022.csv    (187,987 rows, 12 years)
│  ├─ sector_mapping.csv                 (91 companies + sectors)
│  ├─ dividend20217-2024.csv             (309 dividend records)
│  ├─ Tunindex Historical Data.csv       (3,969 index records)
│  └─ kaggle_source/                     (88 original Kaggle CSVs - backup)
│
├─ output/
│  ├─ fact_stock_daily.csv       (PRIMARY: for Power BI)
│  ├─ dim_date.csv               (Trading dates dimension)
│  ├─ dim_stock.csv              (Stocks dimension)
│  ├─ enriched_data.csv          (All columns, for analysis)
│  └─ daily_updates/
│      ├─ updated_stocks_2025-12-22.csv
│      └─ updated_stocks_2025-12-23.csv
│
├─ docs/
│  ├─ README.md                  (Setup instructions)
│  └─ DATA_DICTIONARY.md         (Column definitions)
│
├─ requirements.txt              (Python packages)
├─ ETL_PIPELINE.md              (This file)
└─ .venv/                        (Python virtual environment)
```

