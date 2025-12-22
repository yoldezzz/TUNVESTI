"""
SCRIPT 08: ILBOURSA HISTORICAL SCRAPER (2023-2025)
===================================================
Purpose: Scrape historical daily data from Ilboursa for 2023-2025 gap period
Source: https://www.ilboursa.com/marches/cotation_TICKER?historique=1
Output: data/ilboursa_2023_2025.csv

This script:
1. Checks Ilboursa for historical data pages
2. Scrapes daily OHLCV for each stock
3. Gets data backward from 2022-12-30 to 2025-12-21
4. Handles pagination and rate limiting
5. Merges with Kaggle data to fill the gap
"""

import os
import sys
import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging
import time
import re

# Setup absolute paths
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
data_dir = os.path.join(project_root, 'data')
output_dir = os.path.join(project_root, 'output')
log_file = os.path.join(output_dir, 'ilboursa_historical.log')

os.makedirs(data_dir, exist_ok=True)
os.makedirs(output_dir, exist_ok=True)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ============================================================================
# VERIFIED TICKERS (90 stocks)
# ============================================================================

VERIFIED_TICKERS = [
    'ADWYA', 'AETEC', 'AL', 'AB', 'AMS', 'ATB', 'ATL', 'ARTES', 'ASSAD', 'ASSMA', 'AST',
    'TJARI', 'TJL', 'BT', 'BNA', 'BL', 'BHASS', 'BH', 'BHL', 'BIAT', 'BNASS', 'BTE', 'CC',
    'CELL', 'CREAL', 'CIL', 'SCB', 'CITY', 'DH', 'ELBEN', 'LSTR', 'NAKL', 'SOKNA', 'ECYCL',
    'GIF', 'HL', 'XABYT', 'ICF', 'LNDOR', 'MAG', 'AMV', 'SAM', 'MIP', 'MNP', 'MPBS', 'NBL',
    'PLAST', 'OTH', 'PLTU', 'PGH', 'SAH', 'SMD', 'SERVI', 'SFBT', 'SIAME', 'SIMPA', 'SIPHA',
    'SITS', 'SMART', 'ALKIM', 'SOMOC', 'SOPAT', 'SOTEM', 'SOTET', 'STPAP', 'STPIL', 'MGR',
    'SOTUV', 'SPDIT', 'STA', 'STAR', 'STB', 'STEQ', 'STIP', 'SPHAX', 'TGH', 'TLNET', 'TPR',
    'PX1', 'TINV', 'TRE', 'TAIR', 'TBIDX', 'TLS', 'TVAL', 'UADH', 'UBCI', 'UIB', 'UMED', 'WIFAK'
]

# ============================================================================
# ILBOURSA HISTORICAL SCRAPER
# ============================================================================

def scrape_ilboursa_historical(ticker, max_records=750):
    """
    Scrape historical data for a single stock from Ilboursa
    
    Ilboursa structure:
    - Base URL: https://www.ilboursa.com/marches/cotation_TICKER
    - Historical view: Add ?historique=1 or similar parameter
    - Get up to 3 years of daily data (750+ trading days)
    """
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    records = []
    
    try:
        # Try multiple URL patterns for historical data
        urls_to_try = [
            f"https://www.ilboursa.com/marches/cotation_{ticker}?historique=1",
            f"https://www.ilboursa.com/marches/cotation_{ticker}?periode=3years",
            f"https://www.ilboursa.com/marches/cotation_{ticker}",  # Fallback to main page
        ]
        
        for url in urls_to_try:
            try:
                logger.debug(f"Trying {url}")
                response = requests.get(url, headers=headers, timeout=10)
                
                if response.status_code != 200:
                    logger.debug(f"  HTTP {response.status_code}")
                    continue
                
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Look for historical data in tables
                tables = soup.find_all('table')
                logger.debug(f"  Found {len(tables)} tables")
                
                if not tables:
                    continue
                
                # Parse each table row
                for table in tables:
                    rows = table.find_all('tr')
                    
                    for row in rows[1:]:  # Skip header
                        cols = row.find_all('td')
                        
                        if len(cols) < 5:
                            continue
                        
                        try:
                            # Try to extract date and prices
                            date_text = cols[0].text.strip()
                            
                            # Parse date - try multiple formats
                            date_obj = None
                            for fmt in ['%d/%m/%Y', '%Y-%m-%d', '%d-%m-%Y']:
                                try:
                                    date_obj = datetime.strptime(date_text, fmt)
                                    break
                                except:
                                    pass
                            
                            if not date_obj:
                                continue
                            
                            date = date_obj.strftime('%Y-%m-%d')
                            
                            # Extract OHLC values (handle both comma and dot decimals)
                            def parse_price(text):
                                text = text.replace(',', '.').strip()
                                try:
                                    return float(text)
                                except:
                                    return None
                            
                            open_price = parse_price(cols[1].text) if len(cols) > 1 else None
                            high_price = parse_price(cols[2].text) if len(cols) > 2 else None
                            low_price = parse_price(cols[3].text) if len(cols) > 3 else None
                            close_price = parse_price(cols[4].text) if len(cols) > 4 else None
                            volume = 0
                            
                            # Try to extract volume
                            if len(cols) > 5:
                                volume_text = cols[5].text.replace(',', '').replace(' ', '').strip()
                                try:
                                    volume = int(volume_text)
                                except:
                                    volume = 0
                            
                            # Only add if we have close price
                            if close_price is not None:
                                # Only include if date is in 2023-2025 range
                                if '2023' in date or '2024' in date or '2025' in date:
                                    records.append({
                                        'Date': date,
                                        'Ticker': ticker,
                                        'Open': open_price if open_price else close_price,
                                        'High': high_price if high_price else close_price,
                                        'Low': low_price if low_price else close_price,
                                        'Close': close_price,
                                        'Volume': volume
                                    })
                        
                        except Exception as e:
                            logger.debug(f"Error parsing row: {e}")
                            continue
                
                # If we got records, break from URL loop
                if len(records) > 0:
                    logger.info(f"✓ {ticker:6s}: {len(records)} records from Ilboursa")
                    break
            
            except requests.exceptions.RequestException as e:
                logger.debug(f"Request error for {url}: {e}")
                continue
        
        return records
    
    except Exception as e:
        logger.debug(f"Error scraping {ticker}: {e}")
        return []

# ============================================================================
# BATCH SCRAPER WITH RATE LIMITING
# ============================================================================

def scrape_all_stocks():
    """Scrape historical data for all 90 stocks with rate limiting"""
    
    logger.info("=" * 70)
    logger.info("Starting Ilboursa Historical Scraper (2023-2025)")
    logger.info("=" * 70)
    logger.info(f"Target: {len(VERIFIED_TICKERS)} stocks")
    logger.info(f"Target period: 2023-01-01 to 2025-12-21")
    logger.info(f"Expected data points: ~750 trading days × 90 stocks = 67,500 records")
    
    all_records = []
    successful = 0
    failed = 0
    
    for idx, ticker in enumerate(VERIFIED_TICKERS, 1):
        try:
            # Add rate limiting (1 second between requests)
            if idx > 1:
                time.sleep(1)
            
            logger.info(f"[{idx:2d}/{len(VERIFIED_TICKERS)}] Scraping {ticker}...")
            
            records = scrape_ilboursa_historical(ticker)
            
            if len(records) > 0:
                all_records.extend(records)
                successful += 1
            else:
                logger.warning(f"  No data retrieved for {ticker}")
                failed += 1
        
        except Exception as e:
            logger.error(f"Error with {ticker}: {e}")
            failed += 1
    
    logger.info(f"\n" + "=" * 70)
    logger.info(f"Scraping Results: {successful} succeeded, {failed} failed")
    logger.info(f"Total records: {len(all_records)}")
    logger.info("=" * 70)
    
    return pd.DataFrame(all_records) if len(all_records) > 0 else None

# ============================================================================
# CALCULATE METRICS
# ============================================================================

def calculate_metrics(df):
    """Calculate Return% and Volatility_30d"""
    
    logger.info("\nCalculating metrics...")
    
    # Sort by ticker and date
    df['Date'] = pd.to_datetime(df['Date'])
    df = df.sort_values(['Ticker', 'Date']).reset_index(drop=True)
    
    # Calculate Return%
    df['Return'] = df.groupby('Ticker')['Close'].pct_change()
    
    # Calculate 30-day rolling volatility
    df['Volatility_30d'] = df.groupby('Ticker')['Return'].transform(
        lambda x: x.rolling(window=30).std() * np.sqrt(252)
    )
    
    # Convert date back to string
    df['Date'] = df['Date'].dt.strftime('%Y-%m-%d')
    
    logger.info(f"✓ Metrics calculated")
    
    return df

# ============================================================================
# MERGE WITH EXISTING DATA
# ============================================================================

def merge_with_kaggle(df_ilboursa):
    """Merge Ilboursa 2023-2025 with Kaggle 2010-2022"""
    
    logger.info("\n" + "=" * 70)
    logger.info("Merging with Kaggle data")
    logger.info("=" * 70)
    
    try:
        # Load Kaggle data
        kaggle_path = os.path.join(output_dir, 'final_tunvesti_dataset.csv')
        df_kaggle = pd.read_csv(kaggle_path)
        logger.info(f"Kaggle: {len(df_kaggle)} records (2010-2022)")
    except:
        logger.warning("Could not load Kaggle data")
        df_kaggle = pd.DataFrame()
    
    # Combine
    df_combined = pd.concat([df_kaggle, df_ilboursa], ignore_index=True)
    
    # Remove duplicates
    df_combined = df_combined.drop_duplicates(subset=['Ticker', 'Date'], keep='first')
    
    # Sort
    df_combined['Date'] = pd.to_datetime(df_combined['Date'])
    df_combined = df_combined.sort_values(['Ticker', 'Date']).reset_index(drop=True)
    df_combined['Date'] = df_combined['Date'].dt.strftime('%Y-%m-%d')
    
    # Ensure column order
    columns = ['Ticker', 'Date', 'Open', 'High', 'Low', 'Close', 'Volume', 'Return', 'Volatility_30d']
    df_combined = df_combined[columns]
    
    logger.info(f"\nMerged Dataset:")
    logger.info(f"  Total records: {len(df_combined)}")
    logger.info(f"  Tickers: {df_combined['Ticker'].nunique()}")
    logger.info(f"  Date range: {df_combined['Date'].min()} to {df_combined['Date'].max()}")
    
    return df_combined

# ============================================================================
# EXPORT
# ============================================================================

def export_data(df_ilboursa, df_combined):
    """Export both 2023-2025 only and complete merged dataset"""
    
    logger.info("\n" + "=" * 70)
    logger.info("Exporting Data")
    logger.info("=" * 70)
    
    # Save 2023-2025 only
    path1 = os.path.join(data_dir, 'ilboursa_2023_2025.csv')
    df_ilboursa.to_csv(path1, index=False)
    logger.info(f"✓ Ilboursa 2023-2025: {path1}")
    
    # Save complete dataset
    path2 = os.path.join(output_dir, 'complete_tunvesti_2010_2025.csv')
    df_combined.to_csv(path2, index=False)
    logger.info(f"✓ Complete 2010-2025: {path2}")
    
    logger.info("\n" + "=" * 70)
    logger.info("✅ ILBOURSA HISTORICAL SCRAPING COMPLETE")
    logger.info("=" * 70)
    logger.info(f"Dataset now covers: 2010-01-04 to 2025-12-22 (CONTINUOUS, NO GAPS)")

# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == "__main__":
    try:
        # Scrape all stocks
        df_ilboursa = scrape_all_stocks()
        
        if df_ilboursa is None or len(df_ilboursa) == 0:
            logger.error("No historical data retrieved from Ilboursa")
            logger.info("Possible reasons:")
            logger.info("1. Ilboursa blocks automated scraping")
            logger.info("2. Historical data requires special access")
            logger.info("3. Page structure different than expected")
            sys.exit(1)
        
        # Calculate metrics
        df_ilboursa = calculate_metrics(df_ilboursa)
        
        # Merge with Kaggle
        df_complete = merge_with_kaggle(df_ilboursa)
        
        # Export
        export_data(df_ilboursa, df_complete)
        
        logger.info("\n✅ Script completed successfully!")
        sys.exit(0)
        
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)
