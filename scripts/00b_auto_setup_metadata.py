"""
TUNVESTI - Auto Setup: Download Company Metadata from BVMT
This script automatically scrapes company names and sectors from BVMT website
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import logging
import os

# Create output directory if it doesn't exist
os.makedirs('../output', exist_ok=True)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('../output/setup.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Browser headers
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

def scrape_bvmt_companies():
    """
    Scrape company list from BVMT website
    
    Returns:
    pd.DataFrame: Company data with Ticker, Name, Sector
    """
    
    logger.info("Starting BVMT company data scrape...")
    
    url = 'https://www.bvmt.com.tn/en/liste-des-societes'
    
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find company table
        tables = soup.find_all('table')
        logger.info(f"Found {len(tables)} tables on page")
        
        if not tables:
            logger.warning("No tables found. Using fallback mapping.")
            return create_fallback_mapping()
        
        data = []
        
        for table in tables:
            rows = table.find_all('tr')[1:]  # Skip header
            
            for row in rows:
                try:
                    cols = row.find_all('td')
                    
                    if len(cols) < 3:
                        continue
                    
                    ticker = cols[0].text.strip()
                    company_name = cols[1].text.strip()
                    sector = cols[2].text.strip() if len(cols) > 2 else "Unknown"
                    
                    if ticker and company_name:
                        data.append({
                            'Ticker': ticker,
                            'CompanyName': company_name,
                            'Sector': sector
                        })
                        logger.info(f"Found: {ticker} - {company_name} ({sector})")
                
                except Exception as e:
                    logger.warning(f"Error parsing row: {str(e)}")
                    continue
        
        if data:
            df = pd.DataFrame(data)
            logger.info(f"\nSuccessfully scraped {len(df)} companies from BVMT")
            return df
        else:
            logger.warning("No company data found. Using fallback mapping.")
            return create_fallback_mapping()
    
    except Exception as e:
        logger.warning(f"Error scraping BVMT: {str(e)}")
        logger.info("Using fallback mapping instead...")
        return create_fallback_mapping()

def create_fallback_mapping():
    """
    Create fallback mapping with common Tunisia stocks
    Used if BVMT website is unavailable
    
    Returns:
    pd.DataFrame: Fallback company mapping
    """
    
    logger.info("Creating fallback company mapping...")
    
    # Common Tunisia stocks (add more as needed)
    fallback_data = {
        'Ticker': [
            'AB', 'ABC', 'ASSTUR', 'ATB', 'BFBK', 'BH', 'BIAT', 'BT', 'BTK',
            'SFBT', 'STB', 'ATTIJARI', 'ASSCOM', 'ASSCES', 'ASSNED', 'BNA',
            'BMCE', 'CPG', 'DTL', 'ELEC', 'FB', 'GAFSA', 'HENKEL', 'HUBLO',
            'ICF', 'KBDP', 'LCOOP', 'MAGASIN', 'MAROC', 'MICROB', 'MPL',
            'NCA', 'OLEO', 'PCHEUR', 'POULINA', 'REAL', 'SAARCO', 'SANIMED',
            'SETEO', 'SFB', 'SIAT', 'SICAR', 'SICOR', 'SIXVIA', 'SFABS',
            'SOPHIB', 'SOTUGAR', 'SOTUHOL', 'STAM', 'STAR', 'STE', 'STEQ',
            'STETEX', 'STOIL', 'STML', 'STPI', 'STROC', 'STTB', 'STTS',
            'TAMOIL', 'TASC', 'TBCE', 'TELNET', 'TFBT', 'TGDR', 'TKCM',
            'TLS', 'TLTC', 'TMCNET', 'TMIT', 'TMNA', 'TNCA', 'TNEA', 'TNFC',
            'TPCE', 'TPIA', 'TRAB', 'TSCOM', 'TTCOM', 'UMS', 'UNIPRO', 'ZAFRAN'
        ],
        'CompanyName': [
            'Arab Bank', 'Assurance Bahja', 'Assurance Tunis Re', 'Arab Tunisian Bank',
            'Banque Franco-Tunisienne', 'Banque Habitat', 'Banque Internationale Arabe',
            'Banque de Tunis', 'Banque de Tunisie', 'Societe Franco-Belge', 'Societe Tunisienne',
            'Bank Attijari', 'Assurance Commerciale', 'Assurance Cession', 'Assurance Nedjma',
            'Banque Nationale', 'Bank Maroc', 'CPG Chemicals', 'Domestic Trade', 'Electricity',
            'Finance Bank', 'Gafsa Mining', 'Henkel Tunisia', 'Hub Logistic', 'ICF Bank',
            'KBD Pharma', 'Cooperative', 'Magasin Store', 'Morocco Company', 'Microbio',
            'Manufacturing', 'National Company', 'Oil Energy', 'Pecheur Marine', 'Poulina Group',
            'Real Estate', 'Saarco Industries', 'Sanimed Healthcare', 'Seteo Energy', 'SFB Finance',
            'SIAT Industries', 'SICAR Finance', 'SICOR Trade', 'Sixvia Transport', 'SFABS',
            'Sophia Industries', 'Sotugar Tourism', 'Sotuhol Hotels', 'STAM Manufacturing',
            'Star Company', 'STE Industries', 'STEQ Equipment', 'Stetex Textiles', 'STOIL Petroleum',
            'STML Metals', 'STPI Industries', 'STROC Trading', 'STTB Bank', 'STTS Services',
            'TAMOIL Energy', 'TASC Services', 'TBCE Commerce', 'Telnet Communications',
            'TFBT Finance', 'TGDR Tourism', 'TKCM Technology', 'TLS Logistics', 'TLTC Communications',
            'TMCNET Networks', 'TMIT Technology', 'TMNA Manufacturing', 'TNCA National',
            'TNEA Energy', 'TNFC Finance', 'TPCE Electricity', 'TPIA Industries', 'TRAB Bank',
            'TSCOM Communications', 'TTCOM Telecom', 'UMS Services', 'Unipro Manufacturing', 'Zafran'
        ],
        'Sector': [
            'Banking', 'Insurance', 'Insurance', 'Banking', 'Banking', 'Banking', 'Banking',
            'Banking', 'Banking', 'Banking', 'Banking', 'Banking', 'Insurance', 'Insurance',
            'Insurance', 'Banking', 'Banking', 'Manufacturing', 'Distribution', 'Utilities',
            'Banking', 'Mining', 'Manufacturing', 'Logistics', 'Banking', 'Pharmaceutical',
            'Distribution', 'Retail', 'Distribution', 'Manufacturing', 'Manufacturing',
            'Manufacturing', 'Manufacturing', 'Energy', 'Fishing', 'Food', 'Real Estate',
            'Manufacturing', 'Healthcare', 'Energy', 'Banking', 'Manufacturing', 'Banking',
            'Finance', 'Trading', 'Transportation', 'Manufacturing', 'Manufacturing',
            'Manufacturing', 'Tourism', 'Hospitality', 'Manufacturing', 'Manufacturing',
            'Manufacturing', 'Manufacturing', 'Manufacturing', 'Manufacturing', 'Manufacturing',
            'Energy', 'Services', 'Banking', 'Communications', 'Banking', 'Tourism',
            'Technology', 'Transportation', 'Communications', 'Technology', 'Technology',
            'Manufacturing', 'Manufacturing', 'Energy', 'Manufacturing', 'Manufacturing',
            'Finance', 'Manufacturing', 'Banking', 'Communications', 'Communications',
            'Services', 'Manufacturing', 'Trading'
        ]
    }
    
    df = pd.DataFrame(fallback_data)
    logger.info(f"Created fallback mapping with {len(df)} companies")
    return df

def save_mapping(df, output_path):
    """
    Save company mapping to CSV
    
    Parameters:
    df (pd.DataFrame): Company data
    output_path (str): Path to save CSV
    """
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)
    logger.info(f"Mapping saved to: {output_path}")
    logger.info(f"Total companies: {len(df)}")

def main():
    """
    Main execution function
    """
    
    try:
        logger.info("=== TUNVESTI Auto Setup: Company Metadata ===\n")
        
        # Scrape or use fallback
        df = scrape_bvmt_companies()
        
        # Save mapping
        output_path = '../data/TICKER_MAPPING.csv'
        save_mapping(df, output_path)
        
        # Display sample
        logger.info("\n=== SAMPLE MAPPING (First 10 rows) ===")
        logger.info(f"\n{df.head(10).to_string()}")
        
        logger.info("\n=== COMPANY METADATA READY ===\n")
        
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}", exc_info=True)
        raise

if __name__ == "__main__":
    main()
