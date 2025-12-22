# 🎯 TUNVESTI - Final Data Pipeline

**Production Dashboard Data Pipeline**  
Real-time stock market data → Continuous updates → Dashboard Ready CSV

---

## 📊 FINAL OUTPUT

**File**: `output/final_tunvesti_dataset.csv`

### Data Specification:
```csv
Date,Ticker,CompanyName,Sector,Open,High,Low,Close,Volume,Return%,Volatility_30d,TUNINDEXClose
2025-12-22,AB,Arab Bank,Banking,3850,3900,3840,3875,125000,0.65,2.34,7850
2025-12-22,ABC,Assurance Bahja,Insurance,3200,3250,3190,3215,85000,-0.45,1.89,7850
2025-12-22,BFBK,Banque Franco,Banking,2890,2920,2880,2910,45000,0.35,2.12,7850
```

### Columns (11 total):
| Column | Type | Source | Update |
|--------|------|--------|--------|
| Date | YYYY-MM-DD | All sources | Daily |
| Ticker | Text | Kaggle + Ilboursa | Fixed |
| CompanyName | Text | BVMT company list | Fixed |
| Sector | Text | BVMT sectors | Fixed |
| Open | Float | Kaggle 2010-2022 / Ilboursa 2023+ | Daily |
| High | Float | Kaggle 2010-2022 / Ilboursa 2023+ | Daily |
| Low | Float | Kaggle 2010-2022 / Ilboursa 2023+ | Daily |
| Close | Float | Kaggle 2010-2022 / Ilboursa 2023+ | Daily |
| Volume | Integer | Kaggle 2010-2022 / Ilboursa 2023+ | Daily |
| Return% | Float | Calculated daily | Daily |
| Volatility_30d | Float | Calculated rolling | Daily |
| TUNINDEXClose | Float | Ilboursa index scraper | Daily |

---

## 🔄 DATA SOURCES (3 Websites)

### 1️⃣ Kaggle - Historical Data (2010-2022)
```
URL: https://www.kaggle.com/datasets/amariaziz/tunisian-stock-market
Data: Daily OHLCV for 80 stocks
Action: Download once, place in data/ folder
```

### 2️⃣ Ilboursa - Daily Updates (2023-2025)
```
URL: https://www.ilboursa.com/marches/cours
Data: Daily prices + volume
Action: Scrape daily (automated)
Script: scripts/02_scrape_ilboursa_daily.py
```

### 3️⃣ BVMT - Company Reference Data
```
URL: https://www.bvmt.com.tn/en/liste-des-societes
Data: Company names, sectors, classifications
Action: Download once, save as TICKER_MAPPING.csv
Script: scripts/01_load_kaggle_data.py merges this
```

---

## 🚀 QUICK START (5 minutes)

### Step 1: Setup (First time only)
```powershell
# Activate environment
.\.venv\Scripts\Activate.ps1

# Verify system
python scripts/00_system_check.py
```

### Step 2: Download Data (First time only)
```powershell
# Download Kaggle dataset
# 1. Go to https://www.kaggle.com/datasets/amariaziz/tunisian-stock-market
# 2. Click "Download"
# 3. Extract to: data/kaggle_source/

# Download company mapping (when 00_system_check.py prompts)
# Go to https://www.bvmt.com.tn/en/liste-des-societes
# Save as: data/TICKER_MAPPING.csv (Ticker, CompanyName, Sector columns)
```

### Step 3: Run Pipeline (Daily)
```powershell
# Load historical + scrape today + merge everything
python scripts/01_load_kaggle_data.py
python scripts/02_scrape_ilboursa_daily.py
python scripts/03_merge_data.py

# Final output: output/final_tunvesti_dataset.csv ✅
```

### Step 4: Automate (Optional)
```powershell
# Run daily updates automatically at 3 PM (Monday-Friday)
python scripts/04_scheduler.py
```

---

## 📁 Project Structure

```
├── data/
│   ├── kaggle_source/          (Download from Kaggle)
│   ├── TICKER_MAPPING.csv      (From BVMT website)
│   ├── historical_stocks_2010_2022.csv
│   └── daily_updates/
│       ├── updated_stocks_YYYY-MM-DD.csv
│       └── TUNINDEX_YYYY-MM-DD.csv
│
├── scripts/
│   ├── 00_system_check.py      (Pre-flight check)
│   ├── 01_load_kaggle_data.py  (Load historical + merge metadata)
│   ├── 02_scrape_ilboursa_daily.py  (Scrape current prices + index)
│   ├── 03_merge_data.py        (Merge + calculate metrics)
│   └── 04_scheduler.py         (Daily automation)
│
├── output/
│   ├── final_tunvesti_dataset.csv   (⭐ FINAL DASHBOARD CSV)
│   ├── data_loading.log
│   ├── web_scraping.log
│   ├── merge_results.log
│   └── scheduler.log
│
└── README.md (this file)
```

---

## 🔍 What Each Script Does

### 00_system_check.py
**Verify environment is ready**
```powershell
python scripts/00_system_check.py
```
✅ Checks: Python version, packages, files, connectivity, website accessibility

---

### 01_load_kaggle_data.py
**Load 2010-2022 historical data + merge company metadata**
```powershell
python scripts/01_load_kaggle_data.py
```
📥 **Input**: 
- `data/kaggle_source/*.csv` (Kaggle dataset)
- `data/TICKER_MAPPING.csv` (Company names, sectors)

📤 **Output**:
- `data/historical_stocks_2010_2022.csv` (80 stocks, ~8000 rows, 2010-2022)

🔧 **What it does**:
1. Reads all Kaggle CSV files
2. Adds Company Name and Sector from mapping
3. Sorts by Date and Ticker
4. Saves to output file

---

### 02_scrape_ilboursa_daily.py
**Scrape today's stock prices from Ilboursa + TUNINDEX**
```powershell
python scripts/02_scrape_ilboursa_daily.py
```
📥 **Input**: None (scrapes website)

📤 **Output**:
- `output/daily_updates/updated_stocks_YYYY-MM-DD.csv` (Today's prices)
- `output/daily_updates/TUNINDEX_YYYY-MM-DD.csv` (Today's index)

🔧 **What it does**:
1. Connects to https://www.ilboursa.com/marches/cours
2. Parses HTML table
3. Extracts: Ticker, Close, Volume for all stocks
4. Connects to https://www.ilboursa.com/marches/indice
5. Extracts: TUNINDEX daily close value
6. Saves both to dated CSV files
7. Logs any errors to web_scraping.log

---

### 03_merge_data.py
**Merge historical + daily data, calculate metrics**
```powershell
python scripts/03_merge_data.py
```
📥 **Input**:
- `data/historical_stocks_2010_2022.csv`
- `output/daily_updates/updated_stocks_*.csv`
- `output/daily_updates/TUNINDEX_*.csv`

📤 **Output**:
- `output/final_tunvesti_dataset.csv` (Complete dataset with metrics)

🔧 **What it does**:
1. Loads historical + all daily updates
2. Deduplicates by (Date, Ticker)
3. **Calculates**: Daily Return% = (Today Close - Yesterday Close) / Yesterday Close × 100
4. **Calculates**: Volatility_30d = Standard deviation of returns over last 30 days
5. **Adds**: TUNINDEX close for each date
6. Joins all columns into final CSV
7. Saves as `final_tunvesti_dataset.csv`
8. Generates data quality report

---

### 04_scheduler.py (Optional Automation)
**Automatically run Steps 2-3 every weekday at 3 PM**
```powershell
python scripts/04_scheduler.py
```

⏰ **Schedule**:
- Runs: Monday-Friday at 15:00 (3 PM Tunisia time)
- Action: Scrapes Ilboursa → Merges → Updates CSV
- Keeps: final_tunvesti_dataset.csv fresh daily

🔧 **Customize time** (line 56 in script):
```python
schedule.every().monday.at("15:00").do(daily_update_job)
# Change "15:00" to your preferred time
```

⚠️ **Note**: Scheduler runs continuously. To stop: Ctrl+C in terminal

---

## 📈 Dashboard Data Ready

Your final CSV (`output/final_tunvesti_dataset.csv`) is ready for:
- ✅ Power BI
- ✅ Tableau
- ✅ Google Sheets
- ✅ Excel pivot tables
- ✅ Python Pandas analysis
- ✅ Any BI tool that accepts CSV

### Columns Available for Dashboard:
```
Return%            → YoY/MOM returns
Volatility_30d     → Risk analysis
Close              → Price trends
Volume             → Liquidity
TUNINDEXClose      → Market benchmark
Sector             → Segment analysis
```

---

## ⚠️ Troubleshooting

### "Kaggle dataset not found"
```
✅ Solution:
1. Download from https://www.kaggle.com/datasets/amariaziz/tunisian-stock-market
2. Extract folder
3. Place in: data/kaggle_source/
4. Re-run: python scripts/01_load_kaggle_data.py
```

### "TICKER_MAPPING.csv not found"
```
✅ Solution:
1. Go to https://www.bvmt.com.tn/en/liste-des-societes
2. Copy company list to Excel or create CSV
3. Create CSV: Ticker, CompanyName, Sector (3 columns)
4. Save to: data/TICKER_MAPPING.csv
5. Re-run: python scripts/01_load_kaggle_data.py
```

### "Website unreachable" / "Scraper failed"
```
✅ Solution:
1. Check internet connection
2. Try manually opening https://www.ilboursa.com/marches/cours
3. If works: Website structure may have changed
4. Check logs: output/web_scraping.log
5. Contact team if persistent
```

### "No data in final CSV"
```
✅ Solution:
1. Verify 01_load_kaggle_data.py completed successfully
2. Verify 02_scrape_ilboursa_daily.py created daily_updates/ files
3. Check logs: output/data_loading.log, output/web_scraping.log
4. Run 00_system_check.py to verify files exist
```

---

## 🔄 Daily Update Workflow

**Manual (Recommended for testing)**:
```powershell
# Every day:
python scripts/02_scrape_ilboursa_daily.py    # ~30 sec
python scripts/03_merge_data.py               # ~1-2 sec
# New CSV created: output/final_tunvesti_dataset.csv ✅
```

**Automated (Set & Forget)**:
```powershell
# Run once:
python scripts/04_scheduler.py
# Runs daily at 3 PM automatically
# Updates output/final_tunvesti_dataset.csv
# Stop anytime: Ctrl+C
```

---

## 📊 Data Freshness

| Data | Frequency | Latest |
|------|-----------|--------|
| Daily Prices | Every trading day | Today's close |
| TUNINDEX | Every trading day | Today's close |
| Volatility | Every trading day | Recalculated |
| Return% | Every trading day | Recalculated |
| Company Names | Once (static) | Q4 2025 |
| Sectors | Once (static) | Q4 2025 |

---

## 🎯 Next Steps

1. ✅ **Download Kaggle dataset** → Place in `data/kaggle_source/`
2. ✅ **Create TICKER_MAPPING.csv** → From BVMT website (Ticker, CompanyName, Sector)
3. ✅ **Run `01_load_kaggle_data.py`** → Loads history
4. ✅ **Run `02_scrape_ilboursa_daily.py`** → Gets today's prices + TUNINDEX
5. ✅ **Run `03_merge_data.py`** → Creates `final_tunvesti_dataset.csv`
6. ✅ **Use in dashboard** → Connect to Power BI / Tableau / etc.
7. ⏳ **Run `04_scheduler.py`** → Automate daily updates (optional)

---

## 📝 Files Log Locations

After each run, check logs for errors/warnings:
```
output/data_loading.log      ← 01_load_kaggle_data.py
output/web_scraping.log      ← 02_scrape_ilboursa_daily.py
output/merge_results.log     ← 03_merge_data.py
output/scheduler.log         ← 04_scheduler.py
```

---

## ✅ Production Checklist

Before sharing with team:

- [ ] Downloaded Kaggle dataset
- [ ] Created TICKER_MAPPING.csv with all 80 stocks
- [ ] Ran system check: `python scripts/00_system_check.py` → All ✅
- [ ] Ran full pipeline (01 → 02 → 03)
- [ ] Output file exists: `output/final_tunvesti_dataset.csv`
- [ ] CSV has data (not empty)
- [ ] Date range covers 2010-2025
- [ ] No error messages in logs
- [ ] Ready for dashboard integration

---

**Status**: 🟢 PRODUCTION READY  
**Last Updated**: December 22, 2025  
**Final Output CSV**: `output/final_tunvesti_dataset.csv`
#   T U N V E S T I  
 