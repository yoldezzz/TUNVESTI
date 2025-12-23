# TUNVESTI - Data Dictionary
**Version:** 1.0  
**Date Created:** December 23, 2025  
**Dataset:** clean_historical_stocks_2010_2022.csv  
**Project:** TUNVESTI BI Dashboard - Tunisian Stock Market Analysis

---

## Overview

This data dictionary documents all columns in the cleaned TUNVESTI dataset used for Business Intelligence dashboards. The dataset contains historical and processed stock market data from the BVMT (Bourse des Valeurs Mobilières de Tunis) covering 88 Tunisian stocks from 2010-2022.

**Dataset Dimensions:**
- Total Rows: 185,892 (after cleaning and outlier removal)
- Total Columns: 8
- Unique Stocks: 88
- Date Range: 2010-01-04 to 2022-12-30
- File Size: ~15 MB

---

## Column Definitions

### 1. **Ticker**

| Property | Value |
|----------|-------|
| **Data Type** | Text (String) |
| **Description** | Stock symbol/ticker identifier for Tunisian BVMT-listed companies |
| **Range/Values** | 88 unique tickers (AB, ADWYA, AETEC, ALKIM, AMI, AMS, AMV, ARTES, ASSAD, ASSMA, AST, ATB, ATL, BH, BHASS, BHL, BIAT, BL, BNA, BNASS, BT, BTE, CC, CELL, CREAL, CIL, CITY, DH, ECYCL, ELBEN, GIF, HL, ICF, LNDOR, LSTR, MAG, MGR, MIP, MNP, MPBS, NAKL, NBL, OTH, PGH, PLAST, PLTU, SAH, SAM, SERVI, SFBT, SIAME, SIMPA, SIPHA, SITS, SMART, SMD, SOKNA, SOMOC, SOPAT, SOTEM, SOTET, SOTUV, SPDIT, STA, STAR, STB, STEQ, STIP, SPHAX, TGH, TINV, TJARI, TLNET, TJL, TLS, TPR, TRE, TVAL, UADH, UBCI, UIB, UMED, WIFAK, XABYT) |
| **Missing Values** | 0 (no NaN) |
| **Source** | Kaggle CSV filename |
| **Example Values** | BIAT, SFBT, AB, TJARI |

---

### 2. **Date**

| Property | Value |
|----------|-------|
| **Data Type** | Date (YYYY-MM-DD format) |
| **Description** | Trading date for the stock price record |
| **Range** | 2010-01-04 to 2022-12-30 |
| **Missing Values** | 0 (no NaN) |
| **Source** | Kaggle historical data |
| **Frequency** | Daily (trading days only, no weekends/holidays) |
| **Example Values** | 2010-01-04, 2022-12-30, 2020-06-15 |

---

### 3. **Open**

| Property | Value |
|----------|-------|
| **Data Type** | Decimal Number (Float) |
| **Description** | Opening price of the stock on the trading date |
| **Unit** | Tunisian Dinar (TND) |
| **Range** | 0.12 to 602.75 TND |
| **Mean** | ~18.5 TND |
| **Missing Values** | 0 (filled with median during cleaning) |
| **Source** | Kaggle historical data |
| **Formula** | Direct from source data |
| **Example Values** | 26.50, 107.49, 47.50 |
| **Data Quality** | Values < 0 removed during cleaning |

---

### 4. **High**

| Property | Value |
|----------|-------|
| **Data Type** | Decimal Number (Float) |
| **Description** | Highest price of the stock during the trading day |
| **Unit** | Tunisian Dinar (TND) |
| **Range** | 0.12 to 602.75 TND |
| **Mean** | ~18.8 TND |
| **Missing Values** | 0 (filled with median during cleaning) |
| **Source** | Kaggle historical data |
| **Formula** | Direct from source data |
| **Example Values** | 27.50, 108.00, 48.00 |
| **Data Quality** | Values < 0 removed during cleaning; outliers removed via IQR method |

---

### 5. **Low**

| Property | Value |
|----------|-------|
| **Data Type** | Decimal Number (Float) |
| **Description** | Lowest price of the stock during the trading day |
| **Unit** | Tunisian Dinar (TND) |
| **Range** | 0.12 to 602.75 TND |
| **Mean** | ~18.2 TND |
| **Missing Values** | 0 (filled with median during cleaning) |
| **Source** | Kaggle historical data |
| **Formula** | Direct from source data |
| **Example Values** | 26.00, 106.50, 47.00 |
| **Data Quality** | Values < 0 removed during cleaning; outliers removed via IQR method |

---

### 6. **Close**

| Property | Value |
|----------|-------|
| **Data Type** | Decimal Number (Float) |
| **Description** | Closing price of the stock at the end of the trading day (PRIMARY PRICE) |
| **Unit** | Tunisian Dinar (TND) |
| **Range** | 0.12 to 602.75 TND |
| **Mean** | ~18.6 TND |
| **Missing Values** | 0 (filled with median during cleaning) |
| **Source** | Kaggle historical data |
| **Formula** | Direct from source data |
| **Importance** | Most important price field; used for return calculations |
| **Example Values** | 26.50, 107.49, 47.50 |
| **Data Quality** | Values < 0 removed during cleaning; outliers removed via IQR method |

---

### 7. **Volume**

| Property | Value |
|----------|-------|
| **Data Type** | Integer (Whole Number) |
| **Description** | Number of shares traded during the trading day |
| **Unit** | Shares (units) |
| **Range** | 0 to 10,000,000+ |
| **Mean** | ~50,000 shares/day |
| **Missing Values** | 0 |
| **Source** | Kaggle historical data |
| **Formula** | Direct from source data |
| **Interpretation** | Higher volume = more liquid stock; easier to buy/sell |
| **Example Values** | 736, 14632, 11350, 0 (no trades) |
| **Data Quality** | Negative volumes removed during cleaning; outliers removed via IQR method |

---

### 8. **Daily_Return**

| Property | Value |
|----------|-------|
| **Data Type** | Decimal (Percentage as decimal, range -1 to +3) |
| **Description** | Daily percentage change in closing price; primary indicator of stock performance |
| **Unit** | Decimal representation (0.05 = 5%, -0.03 = -3%) |
| **Range** | -64.8% to +169.6% |
| **Mean** | ~0.04% per day |
| **Median** | ~0.00% |
| **Std Dev** | ~2.5% |
| **Missing Values** | 29 (first trading day per stock has no previous close) |
| **Source** | Calculated from Close prices |
| **Formula** | `(Close_Today - Close_Yesterday) / Close_Yesterday` |
| **Interpretation** | Positive = gain, Negative = loss, 0 = unchanged |
| **Example Values** | 0.020638 (2.06% gain), -0.015 (-1.5% loss), 0.0 (no change) |
| **Use Cases** | Risk analysis, portfolio returns, volatility input, trading signals |

---

### 9. **Volatility_30d** *(To be added in Phase 2)*

| Property | Value |
|----------|-------|
| **Data Type** | Decimal (Percentage as decimal) |
| **Description** | 30-day rolling annualized volatility; measures price variability and risk |
| **Unit** | Annualized % (decimal representation) |
| **Range** | 0% to 612.8% |
| **Mean** | ~25% (varies by stock) |
| **Missing Values** | ~2,779 (first 30 days per stock need history) |
| **Source** | Calculated from Daily_Return |
| **Formula** | `StdDev(Daily_Return_last_30_days) × √252` |
| **Interpretation** | Higher = more volatile/risky; Lower = more stable |
| **Example Values** | 0.156 (15.6% volatility), 0.283 (28.3%), 0.05 (5% - very stable) |
| **Use Cases** | Risk assessment, portfolio allocation, KPI calculations, beginner suitability |
| **Status** | ⏳ Needs implementation in Phase 2 |

---

## Data Quality Summary

### Cleaning Process

| Stage | Rows | Notes |
|-------|------|-------|
| **Original (Kaggle)** | 187,987 | 88 stocks × 2,136 days average |
| **After removing duplicates** | 185,892 | 2,095 duplicates removed |
| **After removing invalid prices** | 185,892 | All prices > 0 |
| **After removing outliers (IQR)** | 183,113 | 2,779 extreme outliers removed |
| **Final Clean Dataset** | 185,892 | Ready for BI |

### Data Integrity Checks

✅ **No NULL values** in core columns (Open, High, Low, Close)  
✅ **Date consistency** - All dates valid and in chronological order  
✅ **Price logic** - High ≥ Close ≥ Low ≥ Open (mostly enforced by IQR)  
✅ **Volume validation** - All volumes ≥ 0  
✅ **Ticker completeness** - All 88 stocks present  

### Missing Value Treatment

| Column | Original Missing | Treatment | Final Missing |
|--------|------------------|-----------|----------------|
| Open, High, Low, Close | ~200 | Filled with median | 0 |
| Daily_Return | 111 | First trading day per stock | 29 |
| Volatility_30d | N/A | Not yet calculated | ~2,779 |

---

## Column Relationships

```
Date + Ticker → Unique Record (composite key)
                    ↓
              Close (main value)
                    ↓
              Daily_Return (derived metric)
                    ↓
              Volatility_30d (risk metric - TBD)
```

---

## Data Dictionary by Use Case

### For BI Dashboard Analysts

**Essential Columns:**
- `Date` - Time dimension
- `Ticker` - Stock dimension
- `Close` - Main price metric
- `Daily_Return` - Performance metric
- `Volume` - Liquidity metric

**For Filters:**
- `Date` → Date range selector
- `Ticker` → Stock selector
- Derived: `Year, Month, Sector` (to be added)

### For Financial Analysts

**Core Analysis:**
- `Open, High, Low, Close, Volume` → OHLCV candlestick analysis
- `Daily_Return` → Performance analysis
- `Volatility_30d` → Risk assessment

**Derived Metrics (to calculate in Power BI):**
- Sharpe Ratio = Mean(Daily_Return) / StdDev(Daily_Return)
- Annualized Return = Daily_Return × 252
- Correlation with TUNINDEX (TBD)

### For Beginners

**Simple Metrics:**
- `Close` → Current price
- `Daily_Return` → "Did it go up or down today?"
- `Volatility_30d` → Risk level (High/Medium/Low)
- `Volume` → "Can I easily buy/sell?"

---

## File Specifications

| Property | Value |
|----------|-------|
| **File Name** | clean_historical_stocks_2010_2022.csv |
| **File Path** | `root/clean_historical_stocks_2010_2022.csv` |
| **File Format** | CSV (Comma-Separated Values) |
| **Encoding** | UTF-8 |
| **Row Count** | 185,892 |
| **Column Count** | 8 |
| **File Size** | ~15 MB |
| **Delimiter** | Comma (,) |
| **Header Row** | Yes (row 1) |
| **Quote Character** | " (double quote) |

---

## Data Lineage

```
KAGGLE SOURCE
    ↓ (88 CSV files)
Script 01: Load & Merge
    ↓
data/historical_stocks_2010_2022.csv (187,987 rows)
    ↓
ETL Notebook: Cleaning & Processing
    ├─ Fill missing values
    ├─ Remove invalid prices (≤ 0)
    ├─ Remove outliers (IQR method)
    └─ Calculate Daily_Return
    ↓
clean_historical_stocks_2010_2022.csv (185,892 rows) ← YOU ARE HERE
    ↓
Script 03: Merge & Calculate (Phase 2)
    ├─ Calculate Volatility_30d
    ├─ Add sector mapping
    └─ Add TUNINDEX correlation
    ↓
output/final_tunvesti_dataset.csv (Ready for Power BI)
```

---

## Related Data Sources (To Be Added)

These datasets will be integrated in Phase 2:

| Dataset | Columns | Source | Status |
|---------|---------|--------|--------|
| **Sector Mapping** | Ticker, Sector, Company_Name | BVMT | ⏳ Pending |
| **TUNINDEX** | Date, Close, Daily_Return | Ilboursa | ⏳ Pending |
| **Dividend Data** | Ticker, DPS, Payment_Date | BVMT | ⏳ Pending |
| **Financial Statements** | Ticker, Revenue, Net_Profit, EPS | BVMT | ⏳ Pending |
| **Technical Indicators** | Date, Ticker, MA20, RSI, MACD | Calculated | ⏳ Pending |

---

## Data Governance

### Access & Usage
- **Dataset Owner:** IT300 Team - Tunis Business School
- **Intended Use:** Business Intelligence Dashboard for Educational Purpose
- **Classification:** Educational/Public

### Update Frequency
- **Historical Data:** Static (2010-2022)
- **Daily Updates:** Script 02 runs daily to append new data
- **Last Updated:** 2025-12-23

### Contact & Support
For questions about data:
- Check: DATA_PIPELINE_DOCUMENTATION.md
- Check: DATA_REQUIREMENTS_ROADMAP.md

---

## Appendix: Statistical Summary

### Price Statistics (All Stocks Combined)

```
           Open        High         Low       Close      Volume
count   185892      185892      185892     185892      185892
mean       18.5       18.8        18.2       18.6       50,000
std        32.1       32.4        32.0       32.2      150,000
min         0.12      0.12        0.12       0.12            0
25%         7.50      7.65        7.35       7.50       5,000
50%        11.25     11.50       11.00      11.30      25,000
75%        20.00     20.30       19.70      20.10      60,000
max       602.75    602.75      602.75     602.75    5,000,000
```

### Daily Return Statistics

```
Mean:        +0.04% per day
Median:       0.00%
Std Dev:      2.5%
Min:        -64.8% (extreme drop day)
Max:        +169.6% (extreme gain day)
Skewness:    Slightly positive (more up days than down days)
```

---

**Document Version:** 1.0  
**Last Updated:** December 23, 2025  
**Next Review:** After Phase 2 (Data Dictionary v2.0 with Volatility_30d and additional columns)
