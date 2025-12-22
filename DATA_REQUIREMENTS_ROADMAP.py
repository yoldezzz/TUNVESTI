"""
TUNVESTI - DATA REQUIREMENTS & ENHANCEMENT ROADMAP
Comprehensive Analysis of Current Data vs Needed Data for Full BI Solution
"""

print("""
================================================================================
                    TUNVESTI DATA AUDIT & EXPANSION STRATEGY
================================================================================

PROJECT SCOPE: Complete BI Dashboard for Young Tunisian Investors
TARGET: 14 Analytical Questions + 10 KPIs + Technical Analysis + Portfolio Optimization

================================================================================
                        PART 1: DATA WE CURRENTLY HAVE
================================================================================

✓ PRICE DATA (Complete for 2010-2022):
  • Open, High, Low, Close prices for 88 stocks
  • Historical trading volume
  • 185,892 rows of processed data
  • Daily granularity
  • Source: Kaggle + Ilboursa scraping

✓ CALCULATED METRICS:
  • Daily Return% (price change)
  • 30-Day Rolling Volatility
  • Ready for Power BI/Tableau

✓ CURRENT COVERAGE:
  • 90 actively traded stocks (from your scraped list)
  • BVMT listed companies
  • Multiple sectors (Banking, Tech, Distribution, etc.)

================================================================================
                    PART 2: CRITICAL DATA GAPS (MISSING)
================================================================================

❌ MISSING DATA FOR KPI #1: SECTOR YOY RETURN
   What we need:
   • Sector classification for each stock
   • Which stocks belong to: Banking, Technology, Distribution, Telecom, etc.
   • Current: ❌ NO sector mapping
   
   Impact: Cannot calculate "Which sectors achieved highest 2025 YOY returns?"
   Priority: HIGH ⚠️

❌ MISSING DATA FOR KPI #3: DIVIDEND YIELD
   What we need:
   • Dividend per share (DPS)
   • Dividend payment dates
   • Current: ❌ NO dividend data at all
   
   Impact: Cannot answer "Which stocks provide risk-adjusted dividend yields >4%?"
   Cannot calculate Sharpe Ratio accurately
   Priority: HIGH ⚠️

❌ MISSING DATA FOR KPI #4 & #9: TUNINDEX DATA
   What we need:
   • Daily TUNINDEX closing values (benchmark index)
   • TUNINDEX composition (which stocks are in the index)
   • Weights of each stock in the index
   • Current: ❌ NO TUNINDEX data collected
   
   Impact: Cannot calculate TUNINDEX Daily % Change
   Cannot calculate TUNINDEX Correlation for diversification analysis
   Priority: CRITICAL 🔴

❌ MISSING FUNDAMENTAL ANALYSIS DATA:
   For Financial Statement Analysis (like the student project):
   • Revenue (annual/quarterly)
   • Net Profit
   • Earnings Per Share (EPS)
   • Dividend Per Share (DPS)
   • Book Value Per Share
   • Debt-to-Equity Ratio
   • Return on Equity (ROE)
   • Net Profit Margin
   • Current Ratio (Liquidity)
   • Price-to-Earnings (P/E) Ratio
   • Price-to-Book (P/B) Ratio
   
   Current: ❌ NONE of these available
   
   Impact: Cannot perform fundamental analysis for stock selection
   Cannot answer "How do macroeconomic shifts influence sector prices?"
   Priority: HIGH ⚠️

❌ MISSING TECHNICAL ANALYSIS INDICATORS:
   What analysts use (from student project):
   • Moving Averages (MA20, MA50, MA200)
   • Relative Strength Index (RSI)
   • MACD (Moving Average Convergence Divergence)
   • Bollinger Bands
   • Volume weighted metrics
   
   Current: ❌ Only have basic Volume, NO technical indicators
   
   Impact: Cannot provide "clear, actionable signals" for beginners
   Priority: MEDIUM 🟡

❌ MISSING MACROECONOMIC DATA:
   What we need:
   • Inflation rates (by month)
   • Interest rates
   • GDP growth
   • Currency exchange rates
   • Economic forecasts
   
   Current: ❌ NONE collected
   
   Impact: Cannot correlate stock performance with macro factors
   Cannot answer "How do macroeconomic shifts influence prices?"
   Priority: MEDIUM 🟡

❌ MISSING CORPORATE ACTIONS DATA:
   What we need:
   • Stock splits
   • Rights offerings
   • Name changes
   • Delisting events
   • Corporate restructuring
   
   Current: ❌ NO adjustments for corporate actions
   
   Impact: Historical prices may be inaccurate for companies with splits
   Priority: LOW 🟢

❌ MISSING MARKET SENTIMENT DATA:
   What we need:
   • News sentiment (positive/negative/neutral)
   • Analyst ratings
   • Short interest
   • Insider trading activity
   
   Current: ❌ NO sentiment analysis
   
   Impact: Cannot answer "What prevailing sentiment surrounds major sectors?"
   Priority: MEDIUM 🟡

❌ MISSING CORRELATION DATA:
   What we need:
   • Correlation matrix between all stocks
   • Stock-to-TUNINDEX correlation coefficients
   • Sector correlation analysis
   
   Current: ❌ Not pre-calculated, need to add
   
   Impact: Cannot identify diversification opportunities
   Cannot answer "How strongly does TUNINDEX correlate with sectors?"
   Priority: HIGH ⚠️

================================================================================
                PART 3: DATA SOURCES TO ADD & HOW TO SCRAPE THEM
================================================================================

🔴 CRITICAL: SECTOR CLASSIFICATION
─────────────────────────────────
Source: BVMT Official Website (bvmt.com.tn)
URL: https://www.bvmt.com.tn/en/liste-des-societes

What to extract:
  • Stock Ticker
  • Company Name
  • Sector/Industry Classification
  • Market Capitalization

Code approach:
  import requests
  from bs4 import BeautifulSoup
  
  url = 'https://www.bvmt.com.tn/en/liste-des-societes'
  response = requests.get(url)
  soup = BeautifulSoup(response.text, 'html.parser')
  
  # Extract table with sector classifications
  for row in soup.find_all('tr')[1:]:
    cols = row.find_all('td')
    ticker = cols[0].text
    company = cols[1].text
    sector = cols[2].text  # Look for sector column
    market_cap = cols[3].text
    
Output file: data/sector_classification.csv
Priority: IMPLEMENT IMMEDIATELY


🔴 CRITICAL: TUNINDEX DATA
────────────────────────
Source: Ilboursa TUNINDEX page
URL: https://www.ilboursa.com/marches/indice/TUNINDEX

What to extract daily:
  • TUNINDEX closing value
  • TUNINDEX daily % change
  • Index composition (which stocks are included)
  • Historical TUNINDEX values (for correlation)

Code approach:
  # Add to existing scraper (02_scrape_ilboursa_daily.py)
  url = 'https://www.ilboursa.com/marches/indice/TUNINDEX'
  
  # Extract: Index Value, % Change, Date
  # Store in: output/daily_updates/TUNINDEX_YYYY-MM-DD.csv

Output file: output/tunindex_historical.csv
Priority: IMPLEMENT IMMEDIATELY


🟡 HIGH: DIVIDEND DATA
──────────────────────
Source 1: BVMT Announcements (dividends declared)
URL: https://www.bvmt.com.tn/en/bulletins-des-operations

Source 2: Company Investor Relations pages
  https://www.bankoftunis.tn/investors  (for BT)
  https://www.biat.tn/investors         (for BIAT)
  etc.

What to extract:
  • Company Name
  • Dividend Per Share (DPS)
  • Dividend Yield (DPS / Current Price)
  • Payment Date
  • Announcement Date

Code approach:
  # Create new script: scrape_dividend_data.py
  companies = [
    {'ticker': 'BT', 'url': 'https://www.bankoftunis.tn/investors'},
    {'ticker': 'BIAT', 'url': 'https://www.biat.tn/investors'},
    # ... add all 90 companies
  ]
  
  for company in companies:
    # Extract dividend information from each company's IR page
    # Parse PDF reports if needed (use PyPDF2 library)

Output file: data/dividend_data.csv
Priority: HIGH (needed for KPI #3)


🟡 HIGH: FUNDAMENTAL DATA (Financial Statements)
─────────────────────────────────────────────
Source: BVMT Official Filings
URL: https://www.bvmt.com.tn/en/rapports-financiers

What to extract (annually):
  • Revenue (Chiffre d'affaires)
  • Net Profit (Résultat Net)
  • Total Assets
  • Total Liabilities
  • Equity
  • Earnings Per Share (EPS)

Code approach:
  # Create new script: scrape_financial_statements.py
  # Most BVMT filings are in PDF format
  
  import PyPDF2
  import requests
  
  # Download PDF financial reports
  # Parse using PyPDF2 or tabula-py
  # Extract key metrics using regex patterns

Output files:
  • data/company_financials_annual.csv
  • data/earnings_per_share.csv
  • data/balance_sheet.csv
  
Priority: HIGH (needed for fundamental analysis)


🟡 MEDIUM: TECHNICAL INDICATORS
────────────────────────────────
Source: Calculate from existing price data

What to calculate:
  • Moving Averages (MA20, MA50, MA200)
  • RSI (Relative Strength Index)
  • MACD (Moving Average Convergence Divergence)
  • Bollinger Bands

Code approach:
  # Create new script: calculate_technical_indicators.py
  import pandas as pd
  import numpy as np
  
  df = pd.read_csv('output/final_tunvesti_dataset.csv')
  
  # Moving Averages
  df['MA20'] = df.groupby('Ticker')['Close'].rolling(20).mean()
  df['MA50'] = df.groupby('Ticker')['Close'].rolling(50).mean()
  df['MA200'] = df.groupby('Ticker')['Close'].rolling(200).mean()
  
  # RSI Calculation
  def calculate_rsi(prices, period=14):
    gains = prices.diff().apply(lambda x: x if x > 0 else 0)
    losses = prices.diff().apply(lambda x: -x if x < 0 else 0)
    
    avg_gain = gains.rolling(period).mean()
    avg_loss = losses.rolling(period).mean()
    
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi
  
  df['RSI'] = df.groupby('Ticker')['Close'].apply(calculate_rsi)
  
  # MACD Calculation
  df['EMA12'] = df.groupby('Ticker')['Close'].ewm(span=12).mean()
  df['EMA26'] = df.groupby('Ticker')['Close'].ewm(span=26).mean()
  df['MACD'] = df['EMA12'] - df['EMA26']
  df['Signal_Line'] = df.groupby('Ticker')['MACD'].ewm(span=9).mean()
  df['MACD_Histogram'] = df['MACD'] - df['Signal_Line']
  
  # Bollinger Bands
  df['BB_Middle'] = df.groupby('Ticker')['Close'].rolling(20).mean()
  df['BB_Std'] = df.groupby('Ticker')['Close'].rolling(20).std()
  df['BB_Upper'] = df['BB_Middle'] + (df['BB_Std'] * 2)
  df['BB_Lower'] = df['BB_Middle'] - (df['BB_Std'] * 2)

Output file: output/final_tunvesti_dataset_with_indicators.csv
Priority: MEDIUM (improves dashboard quality)


🟡 MEDIUM: MACROECONOMIC DATA
─────────────────────────────
Source: Trading Economics API / Tunisia Central Bank

What to collect:
  • Inflation rate (monthly)
  • Interest rates
  • GDP growth
  • USD/TND exchange rate

Code approach:
  # Use Trading Economics API
  import requests
  
  api_key = "YOUR_TRADING_ECONOMICS_API_KEY"
  
  indicators = [
    'TNINFCPI',  # Tunisia Inflation
    'TNRATE',    # Tunisia Interest Rate
    'TNGDPYOY',  # Tunisia GDP YoY
  ]
  
  for indicator in indicators:
    url = f'https://api.tradingeconomics.com/indicators/?ticker={indicator}&token={api_key}'
    response = requests.get(url)
    data = response.json()
    # Store in database

Output file: data/macro_indicators.csv
Priority: MEDIUM


🟢 LOW: SENTIMENT & NEWS DATA
──────────────────────────────
Source: Financial news aggregators

Options:
  1. NewsAPI (newsapi.org) - Free tier available
  2. Finnhub - Free tier available
  3. Alpha Vantage News API

Code approach:
  from newsapi import NewsApiClient
  
  newsapi = NewsApiClient(api_key='YOUR_API_KEY')
  
  for ticker in tickers:
    articles = newsapi.get_everything(
      q=ticker,
      language='en',
      sort_by='publishedAt'
    )
    
    # Sentiment analysis
    from textblob import TextBlob
    
    for article in articles['articles']:
      sentiment = TextBlob(article['title']).sentiment.polarity
      # Store: date, ticker, sentiment (-1 to 1)

Output file: data/news_sentiment.csv
Priority: LOW


================================================================================
                    PART 4: IMPLEMENTATION ROADMAP
================================================================================

PHASE 1: CRITICAL (Week 1)
─────────────────────────

1. ✅ Add Sector Classification
   • Scrape BVMT sector data
   • Create: data/sector_mapping.csv
   • Link each stock to sector
   • Time: 2-3 hours

2. ✅ Add TUNINDEX Data
   • Extend scraper to fetch TUNINDEX
   • Create: output/tunindex_historical.csv
   • Start daily collection
   • Time: 1-2 hours

3. ✅ Calculate Correlations
   • Add correlation matrix to final dataset
   • Stock-to-stock correlations
   • Stock-to-TUNINDEX correlations
   • Time: 1 hour

Result: Can now answer 8/14 analytical questions


PHASE 2: HIGH PRIORITY (Weeks 2-3)
──────────────────────────────────

4. ✅ Add Dividend Data
   • Scrape BVMT dividend announcements
   • Scrape company IR pages
   • Create: data/dividend_data.csv
   • Time: 4-6 hours

5. ✅ Add Financial Statements
   • Scrape financial reports (PDF)
   • Extract key metrics
   • Create: data/company_financials.csv
   • Time: 8-10 hours

6. ✅ Calculate Technical Indicators
   • Add MA20, MA50, MA200
   • Add RSI, MACD, Bollinger Bands
   • Time: 3-4 hours

Result: Can now answer 12/14 analytical questions
Can perform stock selection like student project


PHASE 3: MEDIUM PRIORITY (Weeks 4-5)
────────────────────────────────────

7. ✅ Add Macroeconomic Data
   • Collect inflation, rates, GDP
   • Create: data/macro_indicators.csv
   • Time: 2-3 hours

8. ✅ Add News Sentiment
   • Scrape financial news
   • Perform sentiment analysis
   • Time: 4-5 hours

Result: Can answer all 14 analytical questions
Complete BI solution ready


================================================================================
                PART 5: ENHANCED PYTHON SCRIPTS NEEDED
================================================================================

NEW SCRIPTS TO CREATE:

1. scrape_sector_classification.py
   • Extract sector data from BVMT
   • Output: sector_mapping.csv

2. scrape_tunindex.py
   • Daily TUNINDEX values
   • Output: tunindex_historical.csv

3. scrape_dividend_data.py
   • Company dividend information
   • Output: dividend_data.csv

4. scrape_financial_statements.py
   • Annual financial reports
   • Output: company_financials.csv

5. calculate_technical_indicators.py
   • MA, RSI, MACD, Bollinger Bands
   • Output: enhanced_dataset.csv

6. calculate_correlations.py
   • Correlation matrix
   • Stock-to-TUNINDEX correlation
   • Output: correlation_matrix.csv

7. scrape_macro_data.py
   • Economic indicators
   • Output: macro_indicators.csv

8. scrape_news_sentiment.py
   • News articles + sentiment scores
   • Output: news_sentiment.csv

9. 05_prepare_for_powerbi.py
   • Merge all data sources
   • Create star schema
   • Output: Ready for Power BI import

================================================================================
                    PART 6: DATA MODEL FOR POWER BI
================================================================================

STAR SCHEMA DESIGN:

FACT TABLE: Fact_Stock_Trades
├── Date Key (FK)
├── Stock Key (FK)
├── Index Key (FK)
├── Open Price
├── High Price
├── Low Price
├── Close Price
├── Volume
├── Daily Return %
├── Daily Volatility
├── RSI
├── MACD
├── Bollinger Band Position
└── Technical Signal (Buy/Sell/Hold)

DIMENSION TABLE: Dim_Stock
├── Stock Key (PK)
├── Ticker
├── Company Name
├── Sector Key (FK)
├── Market Cap
├── Company Size (Large/Mid/Small)
├── Dividend Per Share
├── P/E Ratio
├── ROE %
├── Debt-to-Equity
└── Last Updated

DIMENSION TABLE: Dim_Sector
├── Sector Key (PK)
├── Sector Name
├── Number of Companies
├── Sector YOY Return
├── Average Volatility
└── Sector Performance Signal

DIMENSION TABLE: Dim_Index
├── Index Key (PK)
├── TUNINDEX Value
├── Index Daily Change %
├── Year-to-Date Return %
└── 30-Day Volatility

DIMENSION TABLE: Dim_Date
├── Date Key (PK)
├── Date
├── Day of Week
├── Month
├── Quarter
├── Year
├── Is Trading Day
└── Market Holiday Flag

DIMENSION TABLE: Dim_MacroEconomic
├── Date Key (FK)
├── Inflation Rate
├── Interest Rate
├── GDP Growth
├── Exchange Rate (USD/TND)
└── Economic Outlook

DIMENSION TABLE: Dim_Corporate_Actions
├── Stock Key (FK)
├── Date Key (FK)
├── Action Type (Dividend/Split/Rights)
├── Amount/Ratio
└── Adjustment Factor

================================================================================
                    ESTIMATED EFFORT & TIMELINE
================================================================================

Current State:
  • Time spent: ~4-5 hours
  • Data collected: Price data only
  • Completeness: 20% of requirements

After Phase 1 (1 week):
  • Sectors, TUNINDEX, Correlations
  • Completeness: 60%

After Phase 2 (3 weeks):
  • + Dividends, Financials, Technical Indicators
  • Completeness: 85%
  • Ready for professional dashboard

After Phase 3 (5 weeks):
  • + Macro, Sentiment
  • Completeness: 100%
  • Full AI-powered analysis possible

================================================================================
                            NEXT IMMEDIATE STEPS
================================================================================

1. ✅ Create: scrape_sector_classification.py (TODAY)
   Output: Link all 90 stocks to sectors

2. ✅ Extend: 02_scrape_ilboursa_daily.py
   Add: TUNINDEX daily values

3. ✅ Create: calculate_correlations.py
   Output: Correlation matrix

4. ✅ Create: 05_prepare_for_powerbi.py
   Merge all data into star schema format

5. ✅ Test in Power BI
   Create prototype dashboard with available data

TARGET: Professional dashboard ready in 2-3 weeks

================================================================================
""")
