"""
TUNVESTI - Step 2: Web Scraper for Ilboursa Daily Data (2023+)
This script scrapes daily stock market data from Ilboursa.com
Direct URL pattern: https://www.ilboursa.com/marches/cotation_TICKER
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import logging
import os
import time
import re

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
    Scrape current market data from Ilboursa.com using direct URL pattern
    
    Returns:
    pd.DataFrame: Daily market data with columns: Date, Ticker, Close, Volume
    """
    
    logger.info(f"Starting Ilboursa daily scrape for {len(TUNISIA_TICKERS)} stocks...")
    
    data = []
    today = datetime.now().strftime("%Y-%m-%d")
    success_count = 0
    
    for idx, ticker in enumerate(TUNISIA_TICKERS, 1):
        try:
            # Direct URL for each stock
            url = f'https://www.ilboursa.com/marches/cotation_{ticker}'
            
            logger.debug(f"[{idx}/{len(TUNISIA_TICKERS)}] Fetching {ticker}...")
            response = requests.get(url, headers=HEADERS, timeout=10)
            
            if response.status_code != 200:
                logger.debug(f"  {ticker}: HTTP {response.status_code}")
                continue
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Try multiple selectors to find the price
            price_value = None
            volume_value = 0
            
            # Try multiple selectors to find the price
            price_selectors = [
                'span[id*="LblCours"]',
                'span[id*="cours"]',
                'span[class*="prix"]',
                'span[class*="price"]',
                'div[class*="cours"] span',
            ]
            
            for selector in price_selectors:
                try:
                    elements = soup.select(selector)
                    if elements:
                        price_text = elements[0].text.strip()
                        # Clean the price text
                        price_text = price_text.replace(',', '.').replace(' ', '')
                        
                        try:
                            price_value = float(price_text)
                            if price_value > 0:
                                break
                        except:
                            continue
                except:
                    continue
            
            # If no price found, try generic approach
            if not price_value:
                # Look for any number that looks like a price (3-4 digits with decimals)
                all_text = soup.get_text()
                prices = re.findall(r'(\d+[.,]\d{1,2}(?:\d+)?)', all_text)
                if prices:
                    try:
                        price_value = float(prices[0].replace(',', '.'))
                    except:
                        pass
            
            # Try to extract volume data
            # Volume might be in various formats: "1.5B", "1500M", "1,500", etc.
            all_text = soup.get_text()
            
            # Look for volume patterns (e.g., "1.50B", "482.51M", "1500")
            volume_patterns = re.findall(r'(\d+[.,]\d+)[BMK]?', all_text)
            if volume_patterns:
                try:
                    # Get one of the larger numbers that's likely volume
                    for vol_str in volume_patterns[-3:]:  # Check last 3 numbers
                        vol_val = float(vol_str.replace(',', '.'))
                        if vol_val > 100:  # Likely volume if > 100
                            volume_value = int(vol_val)
                            break
                except:
                    pass
            
            # If we found a price, save it
            if price_value and price_value > 0:
                data.append({
                    'Date': today,
                    'Ticker': ticker,
                    'Close': price_value,
                    'Volume': volume_value
                })
                logger.info(f"  ✓ {ticker}: {price_value}")
                success_count += 1
            else:
                logger.debug(f"  ✗ {ticker}: No price found")
            
            # Small delay to avoid hammering the server
            time.sleep(0.5)
        
        except requests.Timeout:
            logger.warning(f"  {ticker}: Timeout")
            continue
        except Exception as e:
            logger.debug(f"  {ticker}: Error - {str(e)}")
            continue
    
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
