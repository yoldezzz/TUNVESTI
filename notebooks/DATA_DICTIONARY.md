# Data Dictionary - TUNVESTI Project

**Date:** December 23, 2025  
**Version:** 1.0  
**Project:** Business Intelligence Dashboard for Tunisian Stock Market

---

## Overview

This document defines all data columns in the TUNVESTI datasets used for Power BI analysis.

**Main Tables:**
1. **fact_stock_daily** (144,727 rows) - Primary fact table
2. **dim_date** (3,236 rows) - Date dimension
3. **dim_stock** (91 rows) - Stock dimension
4. **enriched_data** (144,727 rows) - Full dataset with all intermediate fields (reference only)

---

## fact_stock_daily - Primary Fact Table

**Purpose:** Main dataset for Power BI analysis. One row per stock per trading day.

**Row Count:** 144,727  
**Columns:** 13  
**Data Type:** Time-series data (2010-2025)  
**Grain:** Daily, by stock  
**Update Frequency:** Daily at 3:15 PM (Mon-Fri)

---

### CORE TRADING DATA (OHLCV)

#### **1. date**
| Property | Value |
|----------|-------|
| Data Type | Date (not datetime) |
| Format | YYYY-MM-DD |
| Null Values | 0 (0.0%) - COMPLETE |
| Range | 2010-01-04 to 2025-12-23 |
| Example | 2025-12-23 |
| **Definition** | **Trading date when transaction occurred** |
| **Usage** | Primary time dimension. Use to filter/group analysis by date |
| **Calculation** | Loaded from source data, verified as trading day |

---

#### **2. ticker**
| Property | Value |
|----------|-------|
| Data Type | Text |
| Format | Uppercase, 3-5 characters |
| Null Values | 0 (0.0%) - COMPLETE |
| Unique Values | 91 stocks |
| Example | TJARI, BIAT, AB, SFBT |
| **Definition** | **Stock ticker symbol (stock exchange code)** |
| **Usage** | Identifier to filter/group by individual stock. Link to dim_stock |
| **Calculation** | Uppercase standardization applied during merge |

---

#### **3. open**
| Property | Value |
|----------|-------|
| Data Type | Decimal (4 decimals) |
| Format | Price in TND (Tunisian Dinar) |
| Null Values | 0 (0.0%) - COMPLETE |
| Range | 0.50 to 1,300.00 TND |
| Example | 65.70 TND |
| **Definition** | **Opening price at market open** |
| **Usage** | Component of OHLCV. Used in return calculations, trend analysis |
| **Calculation** | From source data (ilboursa.com or Kaggle) |
| **Notes** | Historical data from Kaggle, recent from web scraper. No adjustments made. |

---

#### **4. high**
| Property | Value |
|----------|-------|
| Data Type | Decimal (4 decimals) |
| Format | Price in TND |
| Null Values | 0 (0.0%) - COMPLETE |
| Range | 0.50 to 1,300.00 TND |
| Example | 66.00 TND |
| **Definition** | **Highest price during the trading day** |
| **Usage** | Trend analysis, range analysis, support/resistance levels |
| **Calculation** | From source data |
| **Validation** | High >= Low (verified: 100% pass) |

---

#### **5. low**
| Property | Value |
|----------|-------|
| Data Type | Decimal (4 decimals) |
| Format | Price in TND |
| Null Values | 0 (0.0%) - COMPLETE |
| Range | 0.50 to 1,300.00 TND |
| Example | 65.70 TND |
| **Definition** | **Lowest price during the trading day** |
| **Usage** | Trend analysis, range analysis, support/resistance levels |
| **Calculation** | From source data |
| **Validation** | High >= Low (verified: 100% pass) |

---

#### **6. close**
| Property | Value |
|----------|-------|
| Data Type | Decimal (4 decimals) |
| Format | Price in TND |
| Null Values | 0 (0.0%) - COMPLETE |
| Range | 0.50 to 1,300.00 TND |
| Example | 65.70 TND |
| **Definition** | **Closing price at market close** |
| **Usage** | Most important price! Used for returns, trend analysis, valuation |
| **Calculation** | From source data |
| **Notes** | Most reliable price point for daily analysis |

---

#### **7. volume**
| Property | Value |
|----------|-------|
| Data Type | Decimal (0 decimals - whole number) |
| Format | Number of shares traded |
| Null Values | 0 (0.0%) - COMPLETE |
| Range | 0 to 150,000+ shares |
| Example | 6,490 shares |
| **Definition** | **Total number of shares traded during the day** |
| **Usage** | Liquidity analysis, volume trends, support/resistance confirmation |
| **Calculation** | From source data |

---

### DERIVED METRICS (Calculated)

#### **8. daily_return_pct**
| Property | Value |
|----------|-------|
| Data Type | Decimal (2-4 decimals) |
| Format | Percentage (%) |
| Null Values | 91 (0.06%) - EXPECTED |
| Range | -50% to +50% |
| Example | +1.52% |
| **Definition** | **Daily percentage return: (Close_today - Close_yesterday) / Close_yesterday × 100** |
| **Usage** | Portfolio returns, risk assessment, momentum analysis |
| **Calculation** | Calculated per ticker (grouped). First row per stock = NaN (no previous day) |
| **Formula** | `(close / LAG(close, 1) OVER (PARTITION BY ticker ORDER BY date) - 1) * 100` |
| **Completeness** | 99.94% (144,636 values) |
| **Notes** | NaN for first trading date per stock is CORRECT and EXPECTED |

---

#### **9. volatility_30d**
| Property | Value |
|----------|-------|
| Data Type | Decimal (2 decimals) |
| Format | Percentage (%) - annualized |
| Null Values | 2,489 (1.72%) - EXPECTED |
| Range | 5% to 50% |
| Example | 30.45% |
| **Definition** | **30-day rolling annualized volatility (standard deviation of returns)** |
| **Usage** | Risk measurement, volatility clustering, portfolio diversification |
| **Calculation** | StdDev(daily_return[last 30 days]) × √252 |
| **Formula** | `STDEV(daily_return_pct) OVER (PARTITION BY ticker ORDER BY date ROWS BETWEEN 29 PRECEDING AND CURRENT ROW) * SQRT(252)` |
| **Annualization** | √252 = 15.87 (trading days per year) |
| **Warmup Period** | First 30 days per stock have NaN (need data). Day 31 onwards = calculated |
| **Completeness** | 98.28% (142,238 values) |
| **Notes** | Higher = more risky. Lower = more stable. NaN before day 30 is CORRECT |

---

#### **10. dividend_yield_pct**
| Property | Value |
|----------|-------|
| Data Type | Decimal (2 decimals) |
| Format | Percentage (%) |
| Null Values | 0 (0.0%) - 100% complete |
| Range | 0% to 5% |
| Example | 1.23% |
| **Definition** | **Annual dividend per share / Closing price × 100** |
| **Usage** | Income investment analysis, yield comparison, total return |
| **Calculation** | (dividend_per_share / close) × 100 |
| **Formula** | `(dividend_per_share / close) * 100` |
| **Zeros** | 122,958 (84.96%) - Most stocks DON'T pay dividends (CORRECT) |
| **Positive Values** | 21,769 (15.04%) - Dividend-paying stocks |
| **Source** | Merged from dividend20217-2024.csv by (ticker, year) |
| **Notes** | 0 = no dividend that year. Not null = correct. Use for income portfolios. |

---

#### **11. avg_volume_30d**
| Property | Value |
|----------|-------|
| Data Type | Decimal (0-2 decimals) |
| Format | Average shares per day |
| Null Values | 2,407 (1.66%) - EXPECTED |
| Range | 100 to 50,000+ shares |
| Example | 4,521.3 shares |
| **Definition** | **30-day rolling average trading volume** |
| **Usage** | Liquidity analysis, trading activity trends, market participation |
| **Calculation** | AVERAGE(volume[last 30 days]) per stock |
| **Formula** | `AVG(volume) OVER (PARTITION BY ticker ORDER BY date ROWS BETWEEN 29 PRECEDING AND CURRENT ROW)` |
| **Warmup Period** | First 30 days per stock have NaN. Day 31 onwards = calculated |
| **Completeness** | 98.34% (142,320 values) |
| **Notes** | Higher = more liquid. Use to identify trading opportunities. NaN before day 30 is CORRECT |

---

### EXTERNAL DATA (Merged from other sources)

#### **12. tunindex_close**
| Property | Value |
|----------|-------|
| Data Type | Decimal (2 decimals) |
| Format | Index points |
| Null Values | 580 (0.40%) - EXPECTED |
| Range | 4,600 to 13,300 |
| Example | 8,234.50 |
| **Definition** | **TUNINDEX (Tunisian Stock Exchange Market Index) closing value** |
| **Usage** | Market benchmark, correlation analysis, market condition indicator |
| **Calculation** | Merged from Tunindex Historical Data.csv by date (LEFT JOIN) |
| **Source** | Tunindex Historical Data.csv (3,969 rows) |
| **Availability** | Starts 2010-01-25 (before that = NaN) |
| **Missing Dates** | 580 rows (mostly early 2010 before index started trading) |
| **Formula for Daily Return** | `(tunindex_close - LAG(tunindex_close) OVER (ORDER BY date)) / LAG(tunindex_close) OVER (ORDER BY date) × 100` |
| **Usage in Correlation** | Used to calculate beta and correlation with individual stock returns |
| **Notes** | Represents overall market. Use as benchmark. NaN before 2010-01-25 is EXPECTED |

---

#### **13. market_cap_m**
| Property | Value |
|----------|-------|
| Data Type | Decimal (1 decimal) |
| Format | Millions TND |
| Null Values | 144,639 (99.94%) - EXPECTED |
| Range | 0.1 to 4,500 M TND |
| Example | 3,285.0 M TND |
| **Definition** | **Market capitalization = Share price × Shares outstanding (in millions)** |
| **Unit** | Millions of Tunisian Dinars (M TND) |
| **Calculation** | From ilboursa.com scraper |
| **Source** | Daily web scraper (2025 data only) |
| **Availability** | Only 88 values (2025-12-23) |
| **Missing Data** | 99.94% - All historical (2010-2022) missing |
| **Why Missing** | Kaggle historical data never included market cap. Would need separate source |
| **Recommendation** | **SKIP for 2010-2022 analysis. OK for 2025 current analysis** |
| **Future Plan** | Can fill in Phase 2 if needed (requires source research) |
| **Notes** | Data limitation, not a bug. Don't use for historical rankings. |

---

## dim_date - Date Dimension Table

**Purpose:** Time dimension for Power BI time intelligence and date-based filtering.

**Row Count:** 3,236 (unique trading dates)  
**Columns:** 8  
**Date Range:** 2010-01-04 to 2025-12-23  
**Grain:** Daily

---

### Date Dimension Columns

#### **1. date**
| Property | Value |
|----------|-------|
| Data Type | Date |
| Format | YYYY-MM-DD |
| Unique Values | 3,236 |
| Example | 2025-12-23 |
| **Definition** | **Trading date (primary key)** |
| **Usage** | Link to fact_stock_daily.date. Filter by date. Time slicers. |

---

#### **2. year**
| Property | Value |
|----------|-------|
| Data Type | Whole Number |
| Range | 2010 to 2025 |
| Example | 2025 |
| **Definition** | **Calendar year** |
| **Usage** | Year-over-year comparisons, annual returns, historical trends |

---

#### **3. month**
| Property | Value |
|----------|-------|
| Data Type | Whole Number |
| Range | 1 to 12 |
| Example | 12 (December) |
| **Definition** | **Calendar month** |
| **Usage** | Month-over-month analysis, seasonal patterns, quarterly analysis |

---

#### **4. quarter**
| Property | Value |
|----------|-------|
| Data Type | Whole Number |
| Range | 1 to 4 |
| Example | 4 (Q4) |
| **Definition** | **Quarter (Q1-Q4)** |
| **Usage** | Quarterly performance analysis, earnings comparisons |

---

#### **5. week**
| Property | Value |
|----------|-------|
| Data Type | Whole Number |
| Range | 1 to 53 |
| Example | 51 (week 51) |
| **Definition** | **ISO week number** |
| **Usage** | Weekly analysis, trading patterns |

---

#### **6. day_of_week**
| Property | Value |
|----------|-------|
| Data Type | Whole Number |
| Range | 1 to 7 (1=Monday, 7=Sunday) |
| Example | 2 (Tuesday) |
| **Definition** | **Day of week numeric** |
| **Usage** | Day-of-week effects analysis, Monday effect studies |

---

#### **7. day_name**
| Property | Value |
|----------|-------|
| Data Type | Text |
| Format | Full name |
| Values | Monday, Tuesday, Wednesday, Thursday, Friday |
| Example | Tuesday |
| **Definition** | **Day of week text name** |
| **Usage** | Reports, visualizations, readable labels |
| **Notes** | Only weekdays (BVMT closed Sat-Sun) |

---

#### **8. is_trading_day**
| Property | Value |
|----------|-------|
| Data Type | Whole Number (Boolean: 0 or 1) |
| Values | 1 = Trading day, 0 = Non-trading |
| Example | 1 |
| **Definition** | **Trading day indicator** |
| **Usage** | Filter analysis to trading days only. Exclude holidays/weekends. |
| **Notes** | All dates in dim_date are trading days (value = 1) |

---

## dim_stock - Stock Dimension Table

**Purpose:** Stock reference data for filtering and grouping analysis by company.

**Row Count:** 91 (unique stocks)  
**Columns:** 3  
**Update Frequency:** Static (unless new stocks added)

---

### Stock Dimension Columns

#### **1. ticker**
| Property | Value |
|----------|-------|
| Data Type | Text |
| Format | Uppercase, 3-5 characters |
| Unique Values | 91 |
| Example | TJARI |
| **Definition** | **Stock ticker symbol (primary key)** |
| **Usage** | Link to fact_stock_daily.ticker. Filter/group by stock. |

---

#### **2. sector**
| Property | Value |
|----------|-------|
| Data Type | Text |
| Null Values | 8 rows (8.8%) - Some tickers missing sector assignment |
| Examples | Financials, Industrial, Telecom, Energy, Services |
| **Definition** | **Industry sector classification** |
| **Usage** | Sector analysis, sector performance comparisons, diversification |
| **Source** | sector_mapping.csv (created from BVMT classification) |
| **Common Sectors** | Banking/Financial, Industrial, Telecom, Energy, Real Estate, Consumer, Services |
| **Missing Values** | 8 stocks without sector. Assign manually in Power BI or source data. |

---

#### **3. company**
| Property | Value |
|----------|-------|
| Data Type | Text |
| Null Values | Some rows may be empty |
| Examples | Tunisie Leasing & Factoring, Banque de l'Industrie et Mines |
| **Definition** | **Full company name** |
| **Usage** | Company identification, reports, drill-down analysis |
| **Source** | sector_mapping.csv |

---

## enriched_data - Full Dataset (Reference)

**Purpose:** Complete dataset with all intermediate columns. For reference and exploratory analysis only. NOT used in Power BI.

**Row Count:** 144,727  
**Columns:** 22  
**Note:** This contains all columns from fact_stock_daily PLUS additional intermediate fields

**Extra Columns (not in fact_stock_daily):**
- year (extracted from date)
- sector (merged from dim_stock)
- company (merged from dim_stock)
- dividend_per_share (raw dividend data)
- tunindex_open, tunindex_high, tunindex_low (market index OHLC)
- Others

**Usage:** For data exploration, validation, and detailed audits. Not needed for Power BI.

---

## Data Quality Summary

### Completeness by Column

| Column | Complete | Null | % Complete | Status |
|--------|----------|------|------------|--------|
| **date** | 144,727 | 0 | 100.0% | ✅ Perfect |
| **ticker** | 144,727 | 0 | 100.0% | ✅ Perfect |
| **open** | 144,727 | 0 | 100.0% | ✅ Perfect |
| **high** | 144,727 | 0 | 100.0% | ✅ Perfect |
| **low** | 144,727 | 0 | 100.0% | ✅ Perfect |
| **close** | 144,727 | 0 | 100.0% | ✅ Perfect |
| **volume** | 144,727 | 0 | 100.0% | ✅ Perfect |
| **daily_return_pct** | 144,636 | 91 | 99.94% | ✅ Expected (first row/stock) |
| **volatility_30d** | 142,238 | 2,489 | 98.28% | ✅ Expected (30-day warmup) |
| **dividend_yield_pct** | 144,727 | 0 | 100.0% | ✅ 0 for non-payers is correct |
| **avg_volume_30d** | 142,320 | 2,407 | 98.34% | ✅ Expected (30-day warmup) |
| **tunindex_close** | 144,147 | 580 | 99.60% | ✅ Expected (index started late) |
| **market_cap_m** | 88 | 144,639 | 0.06% | ⚠️ Expected (source limitation) |

### Data Grade: **A+ (Excellent)**

---


## Related Documentation

- **[ETL_PIPELINE.md](ETL_PIPELINE.md)** - How data was created
- **[DATA_QUALITY_REVIEW.md](DATA_QUALITY_REVIEW.md)** - Detailed audit
- **[POWERBI_IMPLEMENTATION_GUIDE.md](POWERBI_IMPLEMENTATION_GUIDE.md)** - How to use in Power BI
- **[CLEANUP_AND_FUTURE_STRATEGY.md](CLEANUP_AND_FUTURE_STRATEGY.md)** - Future enhancements

