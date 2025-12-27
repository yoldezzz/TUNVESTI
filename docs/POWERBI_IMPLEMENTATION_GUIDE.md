# Power BI Dashboard Implementation Guide

**Date:** December 23, 2025  
**Status:** Data Ready - Proceeding to Power BI  
**Audience:** Team member implementing Power BI dashboard

---

## Executive Summary

**The data pipeline is complete and validated.** We are now moving to Power BI dashboard development.

**Key Facts:**
- 144,727 clean stock records ready
- Star schema structure (1 fact table + 2 dimensions)
- 100% OHLCV completeness
- 5 calculated metrics (returns, volatility, dividends, volumes, index)
- Daily auto-updates configured

**Next Phase:** Build Power BI dashboard with DAX calculations and visualizations

---

## Part 1: What We Have

### Data Files Ready for Power BI

```
Location: C:\Users\NOUIRA\Documents\junior\BI project\output\

PRIMARY FILES:
├─ fact_stock_daily.csv (16.4 MB)
│  └─ 144,727 rows × 13 columns
│  └─ MAIN DATA SOURCE for Power BI
│  └─ Columns: date, ticker, open, high, low, close, volume,
│              daily_return_pct, volatility_30d, dividend_yield_pct,
│              avg_volume_30d, tunindex_close, market_cap_m
│
├─ dim_date.csv (0.1 MB)
│  └─ 3,236 unique trading dates
│  └─ Time dimension with year, month, quarter, week, day info
│
└─ dim_stock.csv (2.3 KB)
   └─ 91 stocks
   └─ Columns: ticker, sector, company
```

### Data Quality Summary

| Metric | Status | Notes |
|--------|--------|-------|
| OHLCV Data | COMPLETE | Perfect - no issues |
| Daily Returns | 99.9% | First row/stock is NaN (expected) |
| Volatility 30D | 98.3% | First 30 days/stock is NaN (expected) |
| Dividend Yield | 100% | Most are 0 (correct - no dividend) |
| Market Index | 99.6% | Complete for all active dates |
| Market Cap | WARNING 0.06% | Only 2025 data (skip for 2010-2022) |

**Recommendation:** Use all columns except market_cap (too sparse)

---

## Part 2: Power BI Setup Steps

### Step 1: Load Data into Power BI

```
1. Open Power BI Desktop
2. Click "Get Data" → "Text/CSV"
3. Navigate to: C:\Users\NOUIRA\Documents\junior\BI project\output\
4. Select: fact_stock_daily.csv
5. Click "Load"
6. Wait for data import (~30 seconds)
7. Verify: 144,727 rows loaded
```

### Step 2: Load Dimension Tables

```
Repeat for each dimension:

DIM_DATE:
1. Get Data → Text/CSV
2. Select: dim_date.csv
3. Load
4. Verify: 3,236 rows

DIM_STOCK:
1. Get Data → Text/CSV
2. Select: dim_stock.csv
3. Load
4. Verify: 91 rows
```

### Step 3: Create Relationships

```
In Power BI Data View:

FACT ← DIM_DATE:
  Drag: fact_stock_daily.date → dim_date.date
  Cardinality: Many-to-One
  Direction: Single (DIM_DATE filters FACT)

FACT ← DIM_STOCK:
  Drag: fact_stock_daily.ticker → dim_stock.ticker
  Cardinality: Many-to-One
  Direction: Single (DIM_STOCK filters FACT)

Result: Star schema complete
```

### Step 4: Set Data Types

```
In Power Query Editor, ensure correct data types:

fact_stock_daily:
  - date: Date (not datetime)
  - ticker: Text
  - open, high, low, close, volume: Decimal
  - daily_return_pct: Decimal
  - volatility_30d: Decimal
  - dividend_yield_pct: Decimal
  - avg_volume_30d: Decimal
  - tunindex_close: Decimal
  - market_cap_m: Decimal

dim_date:
  - date: Date
  - year, month, quarter, week: Whole Number
  - day_of_week, is_trading_day: Whole Number
  - day_name: Text

dim_stock:
  - ticker: Text
  - sector: Text
  - company: Text
```

---

## Part 3: DAX Formulas

### Key Measures to Create

#### **1. Total Stock Count**
```dax
Total Stocks = DISTINCTCOUNT(dim_stock[ticker])
```
**Use:** KPI card showing 91 stocks

---

#### **2. Average Closing Price**
```dax
Avg Close Price = AVERAGE(fact_stock_daily[close])
```
**Use:** KPI card or line chart trend

---

#### **3. Total Trading Volume**
```dax
Total Volume = SUM(fact_stock_daily[volume])
```
**Use:** KPI card or bar chart

---

#### **4. Average Daily Return (%)**
```dax
Avg Daily Return = AVERAGE(fact_stock_daily[daily_return_pct])
```
**Use:** KPI card showing market trend

---

#### **5. Average Volatility (30-Day)**
```dax
Avg Volatility 30D = AVERAGE(fact_stock_daily[volatility_30d])
```
**Use:** Risk assessment KPI card

---

#### **6. Dividend Paying Stocks**
```dax
Dividend Paying Stocks = CALCULATE(
  DISTINCTCOUNT(dim_stock[ticker]),
  FILTER(fact_stock_daily, fact_stock_daily[dividend_yield_pct] > 0)
)
```
**Use:** KPI card for income investors

---

#### **7. Average Dividend Yield**
```dax
Avg Dividend Yield = CALCULATE(
  AVERAGE(fact_stock_daily[dividend_yield_pct]),
  FILTER(fact_stock_daily, fact_stock_daily[dividend_yield_pct] > 0)
)
```
**Use:** Income analysis card

---

#### **8. Best Performing Stock (Today)**
```dax
Best Stock Today = MAXX(
  VALUES(dim_stock[ticker]),
  CALCULATE(
    MAX(fact_stock_daily[daily_return_pct]),
    FILTER(fact_stock_daily, 
      fact_stock_daily[date] = MAX(fact_stock_daily[date]))
  )
)
```
**Use:** Card visual

---

#### **9. Worst Performing Stock (Today)**
```dax
Worst Stock Today = MINX(
  VALUES(dim_stock[ticker]),
  CALCULATE(
    MIN(fact_stock_daily[daily_return_pct]),
    FILTER(fact_stock_daily, 
      fact_stock_daily[date] = MAX(fact_stock_daily[date]))
  )
)
```
**Use:** Card visual

---

#### **10. Market Return vs TUNINDEX**
```dax
Market Return = AVERAGE(fact_stock_daily[tunindex_daily_return_pct])
```
**Use:** Benchmark comparison

---

#### **11. Volatility Spike Indicator**
```dax
High Volatility Stocks = CALCULATE(
  DISTINCTCOUNT(dim_stock[ticker]),
  FILTER(fact_stock_daily, fact_stock_daily[volatility_30d] > 30)
)
```
**Use:** Risk alert card

---

#### **12. Stock Price Range (Min/Max)**
```dax
Min Price = MIN(fact_stock_daily[low])

Max Price = MAX(fact_stock_daily[high])

Price Range = [Max Price] - [Min Price]
```
**Use:** Data exploration

---

#### **13. Sector Performance**
```dax
Sector Avg Return = CALCULATE(
  AVERAGE(fact_stock_daily[daily_return_pct]),
  FILTER(fact_stock_daily, 
    dim_stock[sector] = SELECTEDVALUE(dim_stock[sector]))
)
```
**Use:** Sector analysis chart

---

#### **14. Trading Activity (Volume Trend)**
```dax
Volume 30D Avg = AVERAGE(fact_stock_daily[avg_volume_30d])
```
**Use:** Liquidity assessment

---

### Advanced DAX: Correlation Matrix

```dax
Correlation [Stock1] vs [Stock2] = 
CALCULATE(
  VAR Stock1Returns = FILTER(fact_stock_daily, dim_stock[ticker] = "TJARI"),
  VAR Stock2Returns = FILTER(fact_stock_daily, dim_stock[ticker] = "BIAT"),
  CORRELATIONX(Stock1Returns, Stock1Returns[daily_return_pct], 
               Stock2Returns[daily_return_pct])
)
```
**Note:** Power BI doesn't have native CORRELATIONX; use R/Python visual or calculate in Python, then load

---

## Part 4: Recommended Visualizations

### Page 1: Market Overview

```
Layout:
┌─────────────────────────────────────────┐
│ MARKET OVERVIEW - December 23, 2025     │
├─────────────────────────────────────────┤
│                                         │
│  [91 Stocks]  [Avg +0.5%]  [Vol 95M]   │
│   KPI Card     KPI Card     KPI Card   │
│                                         │
│  ┌─────────────────────────────────┐   │
│  │ Daily Returns by Sector         │   │
│  │ (Bar Chart)                     │   │
│  │ Financials:  +0.8%              │   │
│  │ Energy:      +0.2%              │   │
│  │ Telecom:     -0.1%              │   │
│  └─────────────────────────────────┘   │
│                                         │
│  ┌─────────────────────────────────┐   │
│  │ Market Index (TUNINDEX)         │   │
│  │ (Line Chart: Last 12 months)    │   │
│  │ Trend: ↑ +2.3%                  │   │
│  └─────────────────────────────────┘   │
│                                         │
└─────────────────────────────────────────┘
```

**Visuals:**
1. KPI Cards (top):
   - Total Stocks: 91
   - Avg Daily Return: [Avg Daily Return]
   - Total Volume: [Total Volume]
   - Avg Volatility: [Avg Volatility 30D]

2. Bar Chart (Sector Performance):
   - X-axis: Sector
   - Y-axis: [Sector Avg Return]
   - Filter: Date = Today

3. Line Chart (Market Index Trend):
   - X-axis: Date (last 12 months)
   - Y-axis: tunindex_close
   - Title: "TUNINDEX Performance"

---

### Page 2: Stock Details & Ranking

```
Layout:
┌─────────────────────────────────────────┐
│ STOCK ANALYSIS - Top & Bottom Performers│
├─────────────────────────────────────────┤
│                                         │
│  [Highest Return] [Lowest Return]       │
│  [Highest Vol]    [Lowest Vol]          │
│  KPI Cards        KPI Cards             │
│                                         │
│  ┌─────────────────────────────────┐   │
│  │ Top 10 Stocks (by 30D Return)   │   │
│  │ Table: Ticker | Return | Vol    │   │
│  │                                 │   │
│  │ 1. TJARI  +15.2%  28.5%         │   │
│  │ 2. BIAT   +12.1%  22.1%         │   │
│  │ 3. AB     +8.3%   15.2%         │   │
│  │ ...                             │   │
│  └─────────────────────────────────┘   │
│                                         │
│  ┌─────────────────────────────────┐   │
│  │ Volatility Scatter Plot         │   │
│  │ X: Avg Return, Y: Volatility    │   │
│  │ Size: Volume, Color: Sector     │   │
│  └─────────────────────────────────┘   │
│                                         │
└─────────────────────────────────────────┘
```

**Visuals:**
1. KPI Cards:
   - Best Performer (Return): [Best Stock Today]
   - Worst Performer (Return)
   - Highest Volatility
   - Lowest Volatility

2. Table (Top Stocks):
   - Columns: ticker, daily_return_pct, volatility_30d, volume
   - Sort by: daily_return_pct descending
   - Filter: volatility_30d is not null

3. Scatter Plot (Risk vs Return):
   - X-axis: [Avg Daily Return]
   - Y-axis: [Avg Volatility 30D]
   - Size: [Total Volume]
   - Legend: sector
   - Title: "Risk-Return Profile"

---

### Page 3: Income Analysis (Dividends)

```
Layout:
┌─────────────────────────────────────────┐
│ DIVIDEND INCOME ANALYSIS                │
├─────────────────────────────────────────┤
│                                         │
│ [91 Stocks] [23 Dividend Payers]        │
│ [Avg Yield: 2.5%]                       │
│ KPI Cards                               │
│                                         │
│ ┌─────────────────────────────────┐    │
│ │ Dividend Yield by Stock         │    │
│ │ Bar Chart (Top 15)              │    │
│ │                                 │    │
│ │ TJARI:   3.5%  ███████          │    │
│ │ BIAT:    2.8%  ██████           │    │
│ │ AB:      1.2%  ██               │    │
│ │ ...                             │    │
│ └─────────────────────────────────┘    │
│                                         │
│ ┌─────────────────────────────────┐    │
│ │ Sector Dividend Comparison      │    │
│ │ Pie/Donut Chart                 │    │
│ │ Financials: 45%                 │    │
│ │ Industrial: 30%                 │    │
│ │ Energy:     25%                 │    │
│ └─────────────────────────────────┘    │
│                                         │
└─────────────────────────────────────────┘
```

**Visuals:**
1. KPI Cards:
   - Total Stocks: [Total Stocks]
   - Dividend Payers: [Dividend Paying Stocks]
   - Avg Yield: [Avg Dividend Yield]

2. Bar Chart (Dividend Yields):
   - X-axis: ticker
   - Y-axis: dividend_yield_pct
   - Sort: descending
   - Top 15 stocks

3. Pie Chart (by Sector):
   - Values: SUM of dividend_yield_pct
   - Legend: sector

---

### Page 4: Historical Trends (12+ Years)

```
Layout:
┌─────────────────────────────────────────┐
│ HISTORICAL ANALYSIS (2010-2025)         │
├─────────────────────────────────────────┤
│                                         │
│ Date Slicer: [2010]──[2025] ←────────│ │
│                                         │
│ ┌─────────────────────────────────┐    │
│ │ Average Closing Price Trend     │    │
│ │ Line Chart (Monthly)            │    │
│ │                                 │    │
│ │ 50├──────────────────────────   │    │
│ │   │   ╱╲      ╱╲      ╱╲        │    │
│ │ 40├─ ╱  ╲    ╱  ╲    ╱  ╲       │    │
│ │   │╱      ╲  ╱    ╲  ╱         │    │
│ │ 30├────────────────────         │    │
│ │   └─────────────────────────    │    │
│ │   2010  2015  2020  2025        │    │
│ └─────────────────────────────────┘    │
│                                         │
│ ┌─────────────────────────────────┐    │
│ │ Annual Returns (by Year)        │    │
│ │ Column Chart                    │    │
│ │ 2010: +5.2%  2015: -1.3%        │    │
│ │ 2011: +2.1%  2016: +3.8%        │    │
│ │ 2012: -0.5%  2017: +2.2%        │    │
│ │ ...                             │    │
│ └─────────────────────────────────┘    │
│                                         │
└─────────────────────────────────────────┘
```

**Visuals:**
1. Slicer (Date Range):
   - Field: dim_date[year]
   - Type: Dropdown or Between

2. Line Chart (Price Trend):
   - X-axis: dim_date[month] or [date]
   - Y-axis: [Avg Close Price]
   - Filter: Date range from slicer
   - Title: "Stock Price Trend"

3. Column Chart (Annual Returns):
   - X-axis: dim_date[year]
   - Y-axis: CALCULATE(AVERAGE(daily_return_pct), ALL dates in year)
   - Title: "Average Annual Returns"

---

### Page 5: Sector Dashboard

```
Layout:
┌─────────────────────────────────────────┐
│ SECTOR ANALYSIS                         │
├─────────────────────────────────────────┤
│                                         │
│ [Sector Filter: All ▼]                  │
│                                         │
│ ┌─────────────────────────────────┐    │
│ │ Sector Performance Matrix       │    │
│ │ Bubble Chart                    │    │
│ │ X: Return, Y: Volatility        │    │
│ │ Size: Avg Volume, Color: Sector │    │
│ │                                 │    │
│ │ Financials ●●●●                 │    │
│ │ Industrial   ●●●                │    │
│ │ Energy        ●●                │    │
│ └─────────────────────────────────┘    │
│                                         │
│ ┌─────────────────────────────────┐    │
│ │ Top Stocks per Sector           │    │
│ │ Table (Filtered by Sector)      │    │
│ │                                 │    │
│ │ Ticker | Return | Volatility    │    │
│ │ TJARI  |  1.5%  |   30.2%       │    │
│ │ BIAT   |  1.2%  |   22.1%       │    │
│ └─────────────────────────────────┘    │
│                                         │
└─────────────────────────────────────────┘
```

**Visuals:**
1. Slicer (Sector Filter):
   - Field: dim_stock[sector]
   - Multi-select enabled

2. Bubble Chart (Sector Performance):
   - X-axis: [Sector Avg Return]
   - Y-axis: CALCULATE(AVERAGE(volatility_30d), by sector)
   - Size: CALCULATE(SUM(volume), by sector)
   - Legend: sector

3. Table (Top Stocks per Sector):
   - Columns: ticker, daily_return_pct, volatility_30d
   - Filter: By selected sector(s)

---

## Part 5: Step-by-Step Implementation

### Week 1: Basic Setup

**Day 1-2: Data Import & Structure**
```
1. Load fact_stock_daily.csv
2. Load dim_date.csv
3. Load dim_stock.csv
4. Create relationships
5. Verify data types
Time: 2-3 hours
```

**Day 3-4: KPI Cards & Basic Measures**
```
1. Create 5 KPI measures
2. Create 5 KPI cards on Page 1
3. Test filters
Time: 2-3 hours
```

**Day 5: Market Overview Page**
```
1. Create sector performance bar chart
2. Create TUNINDEX line chart
3. Add date slicer
4. Format and polish
Time: 3-4 hours
```

### Week 2: Advanced Visualizations

**Day 1-2: Stock Details Page**
```
1. Create top stocks table
2. Create risk-return scatter plot
3. Add stock ticker filter
Time: 3-4 hours
```

**Day 3-4: Income Analysis Page**
```
1. Create dividend yields bar chart
2. Create sector distribution pie chart
3. Filter by dividend payers
Time: 2-3 hours
```

**Day 5: Bonus Pages**
```
1. Historical trends with date slicer
2. Sector dashboard with filters
3. Dashboard formatting & branding
Time: 3-4 hours
```

### Week 3: Refinement & Deployment

**Day 1-2: Testing & Optimization**
```
1. Test all filters and slicers
2. Optimize query performance
3. Add bookmarks for navigation
Time: 2-3 hours
```

**Day 3-4: Documentation & Training**
```
1. Add tooltips to visuals
2. Create user guide
3. Record video walkthrough
Time: 3-4 hours
```

**Day 5: Deployment**
```
1. Publish to Power BI Service
2. Set up refresh schedule (daily)
3. Share with stakeholders
Time: 1-2 hours
```

---

## Part 6: Ongoing Updates

### Daily Auto-Updates

Data is automatically updated daily at 3 PM via Script 04:

```
Timeline:
  3:00 PM → Script 02 scrapes ilboursa.com
  3:05 PM → Script 03 merges & enriches
  3:10 PM → fact_stock_daily.csv updated
  3:15 PM → Power BI refreshes (if connected to file)
```

### Manual Refresh (If File-based)

```
If using .pbix file with CSV import:

1. Save Power BI file
2. Each morning, Power BI can refresh
   - Set refresh schedule: Daily 4:00 PM
   - Or: Publish to Power BI Service for cloud refresh

Better option:
3. Upload fact_stock_daily.csv to Power BI Service
4. Create dataset + reports
5. Auto-refresh daily
```

---

## Part 7: Common Questions

### Q: Why is market_cap mostly NULL?
**A:** Market cap is only available from 2025 scraper data. Historical Kaggle data doesn't have it. This is expected. Skip market cap analysis for 2010-2022.

### Q: Can I add P/E ratios?
**A:** Not yet. Requires financial data (earnings). This is Phase 2 work. Start with OHLCV analysis first.

### Q: Why is 2023-2024 data missing?
**A:** Kaggle data ends 2022, historical scraping failed. Decision: Accept gap for now. Can fill manually in Phase 2 if needed.

### Q: How do I filter by date range?
**A:** Add Date slicer to each page:
```
Insert → Slicer → dim_date[date]
Format as Between range
```

### Q: Can I export data from Power BI?
**A:** Yes:
```
Right-click any visual → Export data → CSV
Or use Data Export feature in Power BI Service
```

---

## Part 8: Support & Troubleshooting

### If Data Doesn't Update

```
Problem: fact_stock_daily.csv hasn't changed in 2+ days
Solution:
1. Check Script 04 logs in output/scheduler.log
2. Check if ilboursa.com is accessible
3. Run Script 02 manually:
   python scripts/02_scrape_ilboursa_daily.py
4. Run Script 03 manually:
   python scripts/03_merge_and_enrich_data.py
```

### If Power BI Won't Refresh

```
Problem: CSV data loaded but not updating in Power BI
Solution:
1. If file-based (.pbix):
   - Manually open and save fact_stock_daily.csv
   - Refresh in Power BI (Ctrl+R)
   
2. If Power BI Service:
   - Configure gateway for file refresh
   - Or use Power Query Web.Contents() to refresh
   
3. Better: Move to SQL Server or Azure SQL
   - Import CSV into database
   - Power BI connects to DB
   - Auto-refresh works smoothly
```

### If Formulas Show Errors

```
Common DAX Issues:

Error: "DAX expression cannot be summarized"
Fix: Wrap in CALCULATE()
  WRONG: AVERAGE(fact_stock_daily[daily_return_pct])
  RIGHT: CALCULATE(AVERAGE(fact_stock_daily[daily_return_pct]))

Error: "Relationship not found"
Fix: Check relationships in Model View
  - Ensure fact_stock_daily.date links to dim_date.date
  - Ensure fact_stock_daily.ticker links to dim_stock.ticker

Error: "Circular dependency"
Fix: Review formula - likely using same field in numerator & denominator
```

---

## Next Steps

### Immediate (This Week):
- [ ] Load 3 CSV files into Power BI
- [ ] Create relationships
- [ ] Build 5 KPI cards
- [ ] Create Market Overview page

### This Month:
- [ ] Complete 5-page dashboard
- [ ] Test all filters
- [ ] Publish to Power BI Service
- [ ] Set up auto-refresh

### Next Month (Phase 2):
- [ ] Add technical indicators
- [ ] Add financial fundamentals
- [ ] Fill 2023-2024 data gap
- [ ] Train users

---

## Resources

**Data Files:**
- Location: `C:\Users\NOUIRA\Documents\junior\BI project\output\`
- Files: fact_stock_daily.csv, dim_date.csv, dim_stock.csv

**Documentation:**
- [ETL_PIPELINE.md](ETL_PIPELINE.md) - Technical details
- [DATA_QUALITY_REVIEW.md](DATA_QUALITY_REVIEW.md) - Data validation
- [CLEANUP_AND_FUTURE_STRATEGY.md](CLEANUP_AND_FUTURE_STRATEGY.md) - Roadmap

**Scripts:**
- `scripts/02_scrape_ilboursa_daily.py` - Daily scraper
- `scripts/03_merge_and_enrich_data.py` - Data merge & enrichment
- `scripts/04_scheduler.py` - Auto-update scheduler

---

**Questions?** Contact data team or check documentation.

**Status:** Ready to Build - Data is Clean & Complete!

---

**Last Updated:** December 23, 2025  
**Next Checkpoint:** January 6, 2026 (Power BI launch)
