"""
TUNVESTI - Step 2: Web Scraper for Ilboursa Daily Data (2025+)
This script scrapes daily stock market data from Ilboursa.com using Selenium
URL pattern: https://www.ilboursa.com/marches/cotation_TICKER
Extracts: Open, High, Low, Close, Volume
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import logging
import os
import time
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# Setup absolute paths
script_dir = os.path.dirname(os.path.abspath(__file__))
base_dir = os.path.dirname(script_dir)
output_dir = os.path.join(base_dir, 'output')
daily_updates_dir = os.path.join(output_dir, 'daily_updates')

# Create output directory if it doesn't exist
os.makedirs(daily_updates_dir, exist_ok=True)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(output_dir, 'web_scraping.log')),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Browser headers to avoid being blocked
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

# All ACTIVE Tunisia BVMT stock tickers - VERIFIED WORKING URLS
TUNISIA_TICKERS = [
    'ADWYA', 'AETEC', 'AL', 'AB', 'AMS', 'ATB', 'ATL', 'ARTES', 'ASSAD', 'ASSMA',
    'AST', 'TJARI', 'TJL', 'BT', 'BNA', 'BL', 'BHASS', 'BH', 'BHL', 'BIAT',
    'BNASS', 'BTE', 'CC', 'CELL', 'CREAL', 'CIL', 'SCB', 'CITY', 'DH', 'ELBEN',
    'LSTR', 'NAKL', 'SOKNA', 'ECYCL', 'GIF', 'HL', 'XABYT', 'ICF', 'LNDOR', 'MAG',
    'AMV', 'SAM', 'MIP', 'MNP', 'MPBS', 'NBL', 'PLAST', 'OTH', 'PLTU', 'PGH',
    'SAH', 'SMD', 'SERVI', 'SFBT', 'SIAME', 'SIMPA', 'SIPHA', 'SITS', 'SMART',
    'ALKIM', 'SOMOC', 'SOPAT', 'SOTEM', 'SOTET', 'STPAP', 'STPIL', 'MGR', 'SOTUV',
    'SPDIT', 'STA', 'STAR', 'STB', 'STEQ', 'STIP', 'SPHAX', 'TGH', 'TLNET', 'TPR',
    'PX1', 'TINV', 'TRE', 'TAIR', 'TBIDX', 'TLS', 'TVAL', 'UADH', 'UBCI', 'UIB',
    'UMED', 'WIFAK'
]

def scrape_ilboursa_daily():
    """
    Scrape current market data from Ilboursa.com using Selenium for JavaScript rendering
    Extracts: COURS (Close), OUVERTURE (Open), HAUT (High), BAS (Low), VOLUME
    
    Returns:
    pd.DataFrame: Daily market data with columns: Date, Ticker, Open, High, Low, Close, Volume
    """
    
    logger.info(f"Starting Ilboursa daily scrape for {len(TUNISIA_TICKERS)} stocks...")
    logger.info("Using Selenium for JavaScript rendering...")
    logger.info("Looking for: COURS, OUVERTURE, HAUT, BAS, VOLUME, VOLATILITE")
    
    data = []
    today = datetime.now().strftime("%Y-%m-%d")
    success_count = 0
    
    # Setup Chrome options (headless mode - faster, no GUI)
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
    
    driver = None
    try:
        driver = webdriver.Chrome(options=chrome_options)
        logger.info("Chrome WebDriver initialized")
        
        for idx, ticker in enumerate(TUNISIA_TICKERS, 1):
            try:
                url = f'https://www.ilboursa.com/marches/cotation_{ticker}'
                logger.debug(f"[{idx}/{len(TUNISIA_TICKERS)}] Fetching {ticker}...")
                
                driver.get(url)
                time.sleep(2)  # Wait for page to fully load
                
                # Parse the rendered HTML
                soup = BeautifulSoup(driver.page_source, 'html.parser')
                all_text = soup.get_text()
                
                # Extract OHLCV + Volatility + Market Cap using French labels found on the page
                # Pattern: Label followed by price value(s)
                open_price = None
                high_price = None
                low_price = None
                close_price = None
                volume = 0
                volatility = None
                market_cap = None
                
                # Split text into lines for easier parsing
                lines = all_text.split('\n')
                
                for i, line in enumerate(lines):
                    line_clean = line.strip()
                    
                    # Look for COURS (Close price)
                    if line_clean.upper() == 'COURS' and i + 1 < len(lines):
                        try:
                            price_str = lines[i + 1].strip().replace(',', '.').replace(' ', '')
                            if '%' not in price_str:  # Skip percentage lines
                                close_price = float(price_str)
                        except:
                            pass
                    
                    # Look for OUVERTURE (Open price)
                    if line_clean.upper() == 'OUVERTURE' and i + 1 < len(lines):
                        try:
                            price_str = lines[i + 1].strip().replace(',', '.').replace(' ', '')
                            if '%' not in price_str:
                                open_price = float(price_str)
                        except:
                            pass
                    
                    # Look for HAUT (High price)
                    if 'HAUT' in line_clean.upper() and i + 1 < len(lines):
                        try:
                            price_str = lines[i + 1].strip().replace(',', '.').replace(' ', '')
                            if '%' not in price_str:
                                high_price = float(price_str)
                        except:
                            pass
                    
                    # Look for BAS (Low price)
                    if line_clean.upper() == 'BAS' and i + 1 < len(lines):
                        try:
                            price_str = lines[i + 1].strip().replace(',', '.').replace(' ', '')
                            if '%' not in price_str:
                                low_price = float(price_str)
                        except:
                            pass
                    
                    # Look for VOLUME - check next 3 lines for the volume number
                    if line_clean.upper() == 'VOLUME':
                        # Search next 3 lines for actual volume (skip empty lines)
                        for j in range(i + 1, min(i + 4, len(lines))):
                            vol_candidate = lines[j].strip()
                            # Skip empty lines, continue to next
                            if not vol_candidate:
                                continue
                            # Remove ALL types of spaces (regular space, non-breaking space \xa0, tabs)
                            vol_cleaned = vol_candidate.replace(' ', '').replace('\xa0', '').replace(',', '').replace('\t', '')
                            
                            # Must be numeric
                            if vol_cleaned and vol_cleaned.isdigit():
                                vol_num = int(vol_cleaned)
                                # Accept volume if it's reasonable (0 to 1 billion)
                                if 0 < vol_num < 1_000_000_000:
                                    volume = vol_num
                                    break
                    
                    # Look for VOLATILITE (Volatility percentage)
                    if line_clean.upper() == 'VOLATILITE' and i + 1 < len(lines):
                        try:
                            # Remove %, comma, spaces, and + sign
                            vol_str = lines[i + 1].strip().replace(',', '.').replace('%', '').replace(' ', '').replace('+', '')
                            if vol_str and vol_str.replace('.', '').replace('-', '').isdigit():
                                volatility = float(vol_str)
                        except:
                            pass
                    
                    # Look for VALORISATION (Market Cap in millions TND)
                    if line_clean.upper() == 'VALORISATION' and i + 1 < len(lines):
                        try:
                            cap_str = lines[i + 1].strip().upper()
                            # Format: "1664 MTND" or "176,3 MTND" (comma = decimal in French)
                            cap_cleaned = cap_str.replace(' ', '').replace('\xa0', '').replace('MTND', '').replace('M', '').replace(',', '.')
                            # Now parse as float
                            if cap_cleaned and cap_cleaned.replace('.', '').replace('-', '').isdigit():
                                market_cap = float(cap_cleaned)  # In millions
                        except:
                            pass
                
                # Fallback: if OHLC not found properly, try regex extraction
                if not close_price:
                    price_pattern = r'(\d+[.,]\d{1,2})'
                    prices = re.findall(price_pattern, all_text)
                    if prices:
                        try:
                            close_price = float(prices[0].replace(',', '.'))
                        except:
                            pass
                
                # Fill missing OHLC values with Close price
                if not open_price and close_price:
                    open_price = close_price
                if not high_price and close_price:
                    high_price = close_price
                if not low_price and close_price:
                    low_price = close_price
                
                # Save if we have close price
                if close_price and close_price > 0:
                    record = {
                        'Date': today,
                        'Ticker': ticker,
                        'Open': round(open_price, 4) if open_price else close_price,
                        'High': round(high_price, 4) if high_price else close_price,
                        'Low': round(low_price, 4) if low_price else close_price,
                        'Close': round(close_price, 4),
                        'Volume': volume,
                        'Volatility': round(volatility, 2) if volatility else None,
                        'Market_Cap_M': round(market_cap, 2) if market_cap else None
                    }
                    data.append(record)
                    logger.info(f"  ✓ {ticker}: C={record['Close']}, V={volume}, Vol%={volatility}, MCap={market_cap}M")
                    success_count += 1
                else:
                    logger.debug(f"  ✗ {ticker}: No close price found")
                
                time.sleep(1)  # Increased delay to avoid rate limiting
            
            except TimeoutException:
                logger.warning(f"  {ticker}: Timeout waiting for page")
                continue
            except ConnectionError as e:
                logger.warning(f"  {ticker}: Connection error (rate limited?) - {str(e)}")
                time.sleep(5)  # Wait longer if rate limited
                continue
            except Exception as e:
                logger.debug(f"  {ticker}: Error - {str(e)}")
                continue
    
    finally:
        if driver:
            driver.quit()
            logger.info("Chrome WebDriver closed")
    
    logger.info(f"Successfully extracted {success_count}/{len(TUNISIA_TICKERS)} stocks")
    
    if data:
        return pd.DataFrame(data)
    else:
        logger.warning("No stocks data collected")
        return pd.DataFrame()

def scrape_tunindex():
    """
    Scrape TUNINDEX data
    
    Returns:
    pd.DataFrame: TUNINDEX data
    """
    
    logger.info("Starting TUNINDEX scrape...")
    
    try:
        url = 'https://www.ilboursa.com/marches/cotation_TUNINDEX'
        logger.info(f"Fetching TUNINDEX from: {url}")
        
        response = requests.get(url, headers=HEADERS, timeout=10)
        
        if response.status_code != 200:
            logger.warning(f"Failed with status {response.status_code}")
            return pd.DataFrame()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Look for price value
        all_text = soup.get_text()
        prices = re.findall(r'(\d+[.,]\d{1,2}(?:\d+)?)', all_text)
        
        if prices:
            try:
                close = float(prices[0].replace(',', '.'))
                today = datetime.now().strftime("%Y-%m-%d")
                
                logger.info(f"Found TUNINDEX: {close}")
                return pd.DataFrame([{
                    'Date': today,
                    'Ticker': 'TUNINDEX',
                    'Close': close,
                    'Volume': 0
                }])
            except:
                pass
        
        logger.warning("Could not extract TUNINDEX value")
        return pd.DataFrame()
    
    except Exception as e:
        logger.warning(f"Error scraping TUNINDEX: {str(e)}")
        return pd.DataFrame()

def save_daily_data(df, data_type):
    """
    Save daily data to CSV
    
    Parameters:
    df (pd.DataFrame): Data to save
    data_type (str): Type of data (stocks or index)
    """
    
    if df.empty:
        logger.warning(f"No data to save for {data_type}")
        return None
    
    os.makedirs(daily_updates_dir, exist_ok=True)
    
    date_str = datetime.now().strftime("%Y-%m-%d")
    filename = f"updated_{data_type}_{date_str}.csv"
    output_path = os.path.join(daily_updates_dir, filename)
    
    df.to_csv(output_path, index=False)
    logger.info(f"Saved: {output_path}")
    logger.info(f"Columns: {', '.join(df.columns.tolist())}")
    logger.info(f"Rows: {len(df)}")
    
    return output_path

def main():
    """
    Main execution function
    """
    
    logger.info("=== TUNVESTI Web Scraper Started ===")
    
    # Scrape stocks
    stocks_df = scrape_ilboursa_daily()
    if not stocks_df.empty:
        save_daily_data(stocks_df, 'stocks')
        logger.info(f"Stocks summary:\n{stocks_df.head()}")
    else:
        logger.warning("No stocks data collected")
    
    time.sleep(2)
    
    # Scrape TUNINDEX
    tunindex_df = scrape_tunindex()
    if not tunindex_df.empty:
        save_daily_data(tunindex_df, 'index')
        logger.info(f"TUNINDEX data:\n{tunindex_df}")
    else:
        logger.warning("No TUNINDEX data collected")
    
    logger.info("=== Web Scraper Completed ===\n")

if __name__ == "__main__":
    main()
