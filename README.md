# TUNVESTI

Tunisia Stock Exchange (BVMT) data pipeline and BI solution - combining historical data (2010-2022) with daily web scraping for Power BI analysis.

## Setup

1. **Install Python 3.13+** and create virtual environment:
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

2. **Verify environment**:
```powershell
python scripts/00_system_check.py
```

## Usage

### Initial Data Load

```powershell
python scripts/01_load_kaggle_data.py          # Merge 88 historical stock files
python scripts/02_scrape_ilboursa_daily.py     # Scrape latest data
python scripts/03_merge_and_enrich_data.py     # Generate star schema
```

**Outputs:**
- `output/fact_stock_daily.csv` - Main dataset (144K+ rows)
- `output/dim_date.csv` - Date dimension
- `output/dim_stock.csv` - Stock dimension

### Daily Updates

```powershell
python scripts/04_scheduler.py  # Automated daily updates at 3 PM
```

## Data Model

**Fact Table**: OHLC prices, volume, daily returns, 30-day volatility, dividends, TUNINDEX

**Dimensions**: Date (calendar attributes), Stock (ticker, sector, company)

## Power BI

1. Import CSVs from `output/` folder
2. Create relationships:
   - `fact_stock_daily[date]` → `dim_date[date]`
   - `fact_stock_daily[ticker]` → `dim_stock[ticker]`
3. See `docs/POWERBI_IMPLEMENTATION_GUIDE.md` for DAX measures

## Documentation

- `docs/DATA_DICTIONARY.md` - Column definitions
- `docs/ETL_PIPELINE.md` - Pipeline details
- `docs/POWERBI_IMPLEMENTATION_GUIDE.md` - Dashboard setup

## Data Sources

- Historical: Kaggle (2010-2022)
- Daily: Ilboursa.com web scraping
- 91 stocks, 3,236 trading days
