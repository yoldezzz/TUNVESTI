"""
TUNVESTI Data Integration & Enrichment Script
==============================================
Merges historical stock data, daily updates, TUNINDEX, sectors, and dividends.
Creates fact and dimension tables suitable for Power BI/Streamlit dashboards.

Author: BI Project Team
Date: 2025-12-23
"""

import pandas as pd
import numpy as np
from pathlib import Path
import logging
from datetime import datetime

# ============================================================================
# CONFIGURATION & LOGGING
# ============================================================================

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Define paths
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / 'data'
OUTPUT_DIR = BASE_DIR / 'output'

# Input files
INPUT_FILES = {
    'historical': DATA_DIR / 'historical_stocks_2010_2022.csv',
    'scraped': OUTPUT_DIR / 'daily_updates',  # We'll find latest file
    'tunindex': DATA_DIR / 'Tunindex Historical Data.csv',
    'sectors': DATA_DIR / 'sector_mapping.csv',
    'dividends': DATA_DIR / 'dividend20217-2024.csv'
}

# Output files
OUTPUT_FILES = {
    'merged_clean': OUTPUT_DIR / 'merged_clean_data.csv',
    'enriched': OUTPUT_DIR / 'enriched_data.csv',
    'fact_table': OUTPUT_DIR / 'fact_stock_daily.csv',
    'dim_date': OUTPUT_DIR / 'dim_date.csv',
    'dim_stock': OUTPUT_DIR / 'dim_stock.csv'
}

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def safe_convert_numeric(value):
    """
    Convert value to numeric, handling French format (comma as decimal).
    E.g., "13,291.00" or "13.291,00" -> float
    """
    if pd.isna(value) or value == '':
        return np.nan
    
    if isinstance(value, (int, float)):
        return float(value)
    
    value_str = str(value).strip()
    
    # Remove spaces
    value_str = value_str.replace(' ', '')
    
    # Handle French format: comma is decimal separator
    # First, remove thousands separators (dots), then replace comma with dot
    if ',' in value_str and '.' in value_str:
        # Could be "13.291,00" (French) or "13,291.00" (US)
        # If comma is after dot, it's French: remove dot, replace comma with dot
        if value_str.rfind(',') > value_str.rfind('.'):
            value_str = value_str.replace('.', '').replace(',', '.')
        else:
            # US format: just remove comma
            value_str = value_str.replace(',', '')
    elif ',' in value_str:
        # Only comma present: assume French format
        value_str = value_str.replace(',', '.')
    
    # Remove % sign if present
    value_str = value_str.replace('%', '')
    
    try:
        return float(value_str)
    except ValueError:
        logger.warning(f"Could not convert '{value}' to numeric")
        return np.nan


def find_latest_scraped_file():
    """Find the most recent scraped data file."""
    daily_dir = INPUT_FILES['scraped']
    if not daily_dir.exists():
        logger.warning(f"Daily updates directory not found: {daily_dir}")
        return None
    
    csv_files = list(daily_dir.glob('updated_stocks_*.csv'))
    if not csv_files:
        logger.warning(f"No scraped files found in {daily_dir}")
        return None
    
    # Sort by filename (YYYY-MM-DD format) and return latest
    latest = sorted(csv_files)[-1]
    logger.info(f"Found latest scraped file: {latest.name}")
    return latest


# ============================================================================
# STEP 1: LOAD DATA
# ============================================================================

def load_data():
    """Load all 5 data sources."""
    logger.info("=" * 70)
    logger.info("STEP 1: LOADING DATA")
    logger.info("=" * 70)
    
    dfs = {}
    
    # 1.1 Historical stocks
    try:
        dfs['historical'] = pd.read_csv(INPUT_FILES['historical'])
        logger.info(f"✓ Historical stocks: {len(dfs['historical'])} rows, {list(dfs['historical'].columns)}")
    except FileNotFoundError:
        logger.error(f"✗ Historical file not found: {INPUT_FILES['historical']}")
        return None
    
    # 1.2 Scraped recent data
    try:
        latest_scraped = find_latest_scraped_file()
        if latest_scraped:
            dfs['scraped'] = pd.read_csv(latest_scraped)
            logger.info(f"✓ Scraped recent: {len(dfs['scraped'])} rows from {latest_scraped.name}")
        else:
            logger.warning("⚠ No scraped data found; will continue without recent updates")
            dfs['scraped'] = pd.DataFrame()
    except Exception as e:
        logger.error(f"✗ Error loading scraped data: {e}")
        dfs['scraped'] = pd.DataFrame()
    
    # 1.3 TUNINDEX
    try:
        dfs['tunindex'] = pd.read_csv(INPUT_FILES['tunindex'])
        logger.info(f"✓ TUNINDEX: {len(dfs['tunindex'])} rows, {list(dfs['tunindex'].columns)}")
    except FileNotFoundError:
        logger.warning(f"⚠ TUNINDEX file not found: {INPUT_FILES['tunindex']}")
        dfs['tunindex'] = pd.DataFrame()
    
    # 1.4 Sectors
    try:
        dfs['sectors'] = pd.read_csv(INPUT_FILES['sectors'])
        logger.info(f"✓ Sectors: {len(dfs['sectors'])} rows, {list(dfs['sectors'].columns)}")
    except FileNotFoundError:
        logger.warning(f"⚠ Sectors file not found: {INPUT_FILES['sectors']}")
        dfs['sectors'] = pd.DataFrame()
    
    # 1.5 Dividends
    try:
        dfs['dividends'] = pd.read_csv(INPUT_FILES['dividends'])
        logger.info(f"✓ Dividends: {len(dfs['dividends'])} rows, {list(dfs['dividends'].columns)}")
    except FileNotFoundError:
        logger.warning(f"⚠ Dividends file not found: {INPUT_FILES['dividends']}")
        dfs['dividends'] = pd.DataFrame()
    
    return dfs


# ============================================================================
# STEP 2: CLEAN DATA
# ============================================================================

def clean_data(dfs):
    """Clean all dataframes."""
    logger.info("\n" + "=" * 70)
    logger.info("STEP 2: CLEANING DATA")
    logger.info("=" * 70)
    
    # 2.1 Historical stocks
    logger.info("\n→ Cleaning historical stocks...")
    df_hist = dfs['historical'].copy()
    
    # Ensure column names are lowercase for consistency
    df_hist.columns = df_hist.columns.str.lower()
    
    # Convert date
    if 'date' in df_hist.columns:
        df_hist['date'] = pd.to_datetime(df_hist['date'], errors='coerce')
    
    # Convert numeric columns
    for col in ['open', 'high', 'low', 'close', 'volume']:
        if col in df_hist.columns:
            df_hist[col] = df_hist[col].apply(safe_convert_numeric)
    
    # Drop rows with missing Date or Close
    df_hist = df_hist.dropna(subset=['date', 'close'])
    logger.info(f"  → After cleaning: {len(df_hist)} rows")
    
    # 2.2 Scraped recent data
    logger.info("\n→ Cleaning scraped data...")
    df_scraped = dfs['scraped'].copy()
    if len(df_scraped) > 0:
        df_scraped.columns = df_scraped.columns.str.lower()
        if 'date' in df_scraped.columns:
            df_scraped['date'] = pd.to_datetime(df_scraped['date'], errors='coerce')
        
        for col in ['open', 'high', 'low', 'close', 'volume', 'volatility', 'market_cap_m']:
            if col in df_scraped.columns:
                df_scraped[col] = df_scraped[col].apply(safe_convert_numeric)
        
        df_scraped = df_scraped.dropna(subset=['date', 'close'])
        logger.info(f"  → After cleaning: {len(df_scraped)} rows")
    else:
        logger.info(f"  → Empty dataset (no scraped data)")
    
    # 2.3 TUNINDEX
    logger.info("\n→ Cleaning TUNINDEX...")
    df_tunindex = dfs['tunindex'].copy()
    if len(df_tunindex) > 0:
        df_tunindex.columns = df_tunindex.columns.str.lower()
        
        # Rename "price" to "tunindex_close" if it exists
        if 'price' in df_tunindex.columns:
            df_tunindex.rename(columns={'price': 'tunindex_close'}, inplace=True)
        
        # Convert date
        if 'date' in df_tunindex.columns:
            df_tunindex['date'] = pd.to_datetime(df_tunindex['date'], errors='coerce')
        
        # Clean numeric columns
        for col in ['tunindex_close', 'open', 'high', 'low', 'vol.', 'change %']:
            if col in df_tunindex.columns:
                df_tunindex[col] = df_tunindex[col].apply(safe_convert_numeric)
        
        # Rename 'vol.' if it exists
        if 'vol.' in df_tunindex.columns:
            df_tunindex.rename(columns={'vol.': 'tunindex_volume'}, inplace=True)
        
        # Rename 'change %' if it exists
        if 'change %' in df_tunindex.columns:
            df_tunindex.rename(columns={'change %': 'tunindex_change_pct'}, inplace=True)
        
        df_tunindex = df_tunindex.dropna(subset=['date', 'tunindex_close'])
        logger.info(f"  → After cleaning: {len(df_tunindex)} rows")
    else:
        logger.info(f"  → Empty dataset")
    
    # 2.4 Sectors
    logger.info("\n→ Cleaning sectors...")
    df_sectors = dfs['sectors'].copy()
    if len(df_sectors) > 0:
        df_sectors.columns = df_sectors.columns.str.lower()
        logger.info(f"  → Columns: {list(df_sectors.columns)}")
    else:
        logger.info(f"  → Empty dataset")
    
    # 2.5 Dividends
    logger.info("\n→ Cleaning dividends...")
    df_divs = dfs['dividends'].copy()
    if len(df_divs) > 0:
        df_divs.columns = df_divs.columns.str.lower()
        
        # Ensure Year is integer
        if 'year' in df_divs.columns:
            df_divs['year'] = df_divs['year'].astype('Int64')
        
        # Convert dividend to numeric
        if 'dividend_per_share' in df_divs.columns:
            df_divs['dividend_per_share'] = df_divs['dividend_per_share'].apply(safe_convert_numeric)
        
        logger.info(f"  → After cleaning: {len(df_divs)} rows")
    else:
        logger.info(f"  → Empty dataset")
    
    return {
        'historical': df_hist,
        'scraped': df_scraped,
        'tunindex': df_tunindex,
        'sectors': df_sectors,
        'dividends': df_divs
    }


# ============================================================================
# STEP 3: MERGE DATA
# ============================================================================

def merge_data(dfs_clean):
    """Merge all data sources into one master dataframe."""
    logger.info("\n" + "=" * 70)
    logger.info("STEP 3: MERGING DATA")
    logger.info("=" * 70)
    
    # 3.1 Concatenate historical + scraped (stock price data)
    logger.info("\n→ Concatenating historical + scraped stock data...")
    
    dfs_to_concat = [dfs_clean['historical']]
    if len(dfs_clean['scraped']) > 0:
        dfs_to_concat.append(dfs_clean['scraped'])
    
    df_stocks = pd.concat(dfs_to_concat, ignore_index=True)
    logger.info(f"  → Before dedup: {len(df_stocks)} rows")
    
    # Remove exact duplicates (same Date + Ticker)
    df_stocks = df_stocks.drop_duplicates(subset=['date', 'ticker'], keep='last')
    logger.info(f"  → After dedup: {len(df_stocks)} rows")
    
    # Sort by ticker and date
    df_stocks = df_stocks.sort_values(['ticker', 'date']).reset_index(drop=True)
    
    # 3.2 Merge TUNINDEX (broadcast to all stocks by Date)
    logger.info("\n→ Merging TUNINDEX data...")
    if len(dfs_clean['tunindex']) > 0:
        # Select only date and tunindex_close for merge
        tunindex_cols = ['date', 'tunindex_close']
        tunindex_cols += [c for c in ['tunindex_open', 'tunindex_high', 'tunindex_low', 
                                       'tunindex_volume', 'tunindex_change_pct'] 
                          if c in dfs_clean['tunindex'].columns]
        
        df_tunindex_merge = dfs_clean['tunindex'][tunindex_cols].copy()
        df_stocks = df_stocks.merge(df_tunindex_merge, on='date', how='left')
        logger.info(f"  → Merged; now {len(df_stocks)} rows, TUNINDEX available for {df_stocks['tunindex_close'].notna().sum()} rows")
    else:
        logger.info(f"  → No TUNINDEX data to merge")
    
    # 3.3 Merge Sectors on Ticker
    logger.info("\n→ Merging sector information...")
    if len(dfs_clean['sectors']) > 0:
        # Map ticker to uppercase for consistency
        df_stocks['ticker'] = df_stocks['ticker'].str.upper()
        dfs_clean['sectors']['ticker'] = dfs_clean['sectors']['ticker'].str.upper()
        
        # Merge, keeping only ticker and sector columns
        sector_cols = [c for c in ['ticker', 'sector', 'company', 'company name', 'company_name'] 
                       if c in dfs_clean['sectors'].columns]
        
        # Rename to standardized format
        sectors_to_merge = dfs_clean['sectors'][sector_cols].copy()
        if 'company name' in sectors_to_merge.columns:
            sectors_to_merge.rename(columns={'company name': 'company'}, inplace=True)
        if 'company_name' in sectors_to_merge.columns:
            sectors_to_merge.rename(columns={'company_name': 'company'}, inplace=True)
        
        sectors_to_merge = sectors_to_merge.drop_duplicates(subset=['ticker'])
        
        df_stocks = df_stocks.merge(sectors_to_merge, on='ticker', how='left')
        logger.info(f"  → Merged; {df_stocks['sector'].notna().sum()} rows with sector info")
    else:
        logger.info(f"  → No sector data to merge")
    
    # 3.4 Add Year, then merge Dividends
    logger.info("\n→ Merging dividend data...")
    df_stocks['year'] = df_stocks['date'].dt.year
    
    if len(dfs_clean['dividends']) > 0:
        # Merge on ticker + year
        df_divs = dfs_clean['dividends'][['ticker', 'year', 'dividend_per_share']].copy()
        df_divs['ticker'] = df_divs['ticker'].str.upper()
        df_divs = df_divs.drop_duplicates(subset=['ticker', 'year'])
        
        df_stocks = df_stocks.merge(df_divs, on=['ticker', 'year'], how='left')
        
        # Fill missing dividends with 0
        df_stocks['dividend_per_share'] = df_stocks['dividend_per_share'].fillna(0)
        
        logger.info(f"  → Merged; {(df_stocks['dividend_per_share'] > 0).sum()} rows with non-zero dividends")
    else:
        logger.info(f"  → No dividend data to merge")
        df_stocks['dividend_per_share'] = 0
    
    logger.info(f"\n✓ Merge complete: {len(df_stocks)} rows")
    
    return df_stocks


# ============================================================================
# STEP 4: DERIVE METRICS
# ============================================================================

def derive_metrics(df):
    """Calculate derived metrics."""
    logger.info("\n" + "=" * 70)
    logger.info("STEP 4: DERIVING METRICS")
    logger.info("=" * 70)
    
    df = df.copy()
    
    # 4.1 Daily Return (%)
    logger.info("\n→ Calculating Daily_Return...")
    df['daily_return_pct'] = 0.0
    
    for ticker in df['ticker'].unique():
        mask = df['ticker'] == ticker
        df.loc[mask, 'daily_return_pct'] = df.loc[mask, 'close'].pct_change() * 100
    
    # Set first row per ticker to NaN (no previous day)
    df.loc[df.groupby('ticker').cumcount() == 0, 'daily_return_pct'] = np.nan
    
    logger.info(f"  → Calculated; {df['daily_return_pct'].notna().sum()} values")
    
    # 4.2 TUNINDEX Daily Return (%)
    logger.info("\n→ Calculating TUNINDEX_Daily_Return...")
    if 'tunindex_close' in df.columns:
        # Unique dates with their tunindex values
        tunindex_returns = df[['date', 'tunindex_close']].drop_duplicates()
        tunindex_returns = tunindex_returns.sort_values('date').reset_index(drop=True)
        tunindex_returns['tunindex_daily_return_pct'] = tunindex_returns['tunindex_close'].pct_change() * 100
        
        # Merge back
        df = df.merge(tunindex_returns[['date', 'tunindex_daily_return_pct']], on='date', how='left')
        logger.info(f"  → Calculated; {df['tunindex_daily_return_pct'].notna().sum()} values")
    else:
        df['tunindex_daily_return_pct'] = np.nan
        logger.info(f"  → TUNINDEX not available")
    
    # 4.3 Volatility_30d (rolling 30-day annualized volatility of daily returns)
    logger.info("\n→ Calculating Volatility_30d...")
    df['volatility_30d'] = np.nan
    
    for ticker in df['ticker'].unique():
        mask = df['ticker'] == ticker
        ticker_data = df.loc[mask, 'daily_return_pct']
        
        # Rolling 30-day std of returns, annualized
        rolling_std = ticker_data.rolling(window=30).std()
        volatility_30d = rolling_std * np.sqrt(252)  # Annualize (252 trading days)
        
        df.loc[mask, 'volatility_30d'] = volatility_30d
    
    logger.info(f"  → Calculated; {df['volatility_30d'].notna().sum()} values")
    
    # 4.4 Dividend_Yield (%)
    logger.info("\n→ Calculating Dividend_Yield...")
    df['dividend_yield_pct'] = 0.0
    
    # Only calculate where we have dividend data and close price > 0
    valid_mask = (df['dividend_per_share'] > 0) & (df['close'] > 0)
    df.loc[valid_mask, 'dividend_yield_pct'] = (df.loc[valid_mask, 'dividend_per_share'] / 
                                                   df.loc[valid_mask, 'close']) * 100
    
    logger.info(f"  → Calculated; {valid_mask.sum()} rows with dividend yield > 0")
    
    # 4.5 Avg_Volume_30d
    logger.info("\n→ Calculating Avg_Volume_30d...")
    df['avg_volume_30d'] = np.nan
    
    for ticker in df['ticker'].unique():
        mask = df['ticker'] == ticker
        ticker_data = df.loc[mask, 'volume']
        
        # Rolling 30-day average volume
        avg_vol_30d = ticker_data.rolling(window=30).mean()
        
        df.loc[mask, 'avg_volume_30d'] = avg_vol_30d
    
    logger.info(f"  → Calculated; {df['avg_volume_30d'].notna().sum()} values")
    
    logger.info(f"\n✓ Derivations complete")
    
    return df


# ============================================================================
# STEP 5: CREATE FACT & DIMENSION TABLES
# ============================================================================

def create_dimension_tables(df):
    """Create dimension tables for Power BI."""
    logger.info("\n" + "=" * 70)
    logger.info("STEP 5: CREATING DIMENSION TABLES")
    logger.info("=" * 70)
    
    # 5.1 dim_date
    logger.info("\n→ Creating dim_date...")
    dim_date = df[['date']].drop_duplicates().sort_values('date').reset_index(drop=True)
    dim_date['year'] = dim_date['date'].dt.year
    dim_date['month'] = dim_date['date'].dt.month
    dim_date['quarter'] = dim_date['date'].dt.quarter
    dim_date['week'] = dim_date['date'].dt.isocalendar().week
    dim_date['day_of_week'] = dim_date['date'].dt.dayofweek  # 0=Monday, 6=Sunday
    dim_date['day_name'] = dim_date['date'].dt.day_name()
    dim_date['is_trading_day'] = 1  # All rows in our data are trading days
    
    logger.info(f"  → {len(dim_date)} unique dates")
    
    # 5.2 dim_stock
    logger.info("\n→ Creating dim_stock...")
    cols_for_dim = ['ticker', 'sector', 'company']
    cols_to_use = [c for c in cols_for_dim if c in df.columns]
    
    dim_stock = df[cols_to_use].drop_duplicates().reset_index(drop=True)
    dim_stock = dim_stock.sort_values('ticker')
    
    logger.info(f"  → {len(dim_stock)} unique stocks")
    
    return dim_date, dim_stock


# ============================================================================
# STEP 6: CREATE FACT TABLE
# ============================================================================

def create_fact_table(df):
    """Create fact table for Power BI."""
    logger.info("\n→ Creating fact_stock_daily...")
    
    # Select only relevant columns
    fact_cols = [
        'date', 'ticker', 'open', 'high', 'low', 'close', 'volume',
        'daily_return_pct', 'volatility_30d', 'dividend_yield_pct', 'avg_volume_30d',
        'tunindex_close', 'market_cap_m'
    ]
    
    fact_cols = [c for c in fact_cols if c in df.columns]
    
    fact_table = df[fact_cols].copy()
    
    # Sort by ticker and date
    fact_table = fact_table.sort_values(['ticker', 'date']).reset_index(drop=True)
    
    logger.info(f"  → {len(fact_table)} rows")
    
    return fact_table


# ============================================================================
# STEP 7: SAVE OUTPUTS
# ============================================================================

def save_outputs(df_merged_clean, df_enriched, fact_table, dim_date, dim_stock):
    """Save all output files."""
    logger.info("\n" + "=" * 70)
    logger.info("STEP 6: SAVING OUTPUT FILES")
    logger.info("=" * 70)
    
    # Ensure output directory exists
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # 6.1 merged_clean_data.csv
    logger.info(f"\n→ Saving {OUTPUT_FILES['merged_clean'].name}...")
    df_merged_clean.to_csv(OUTPUT_FILES['merged_clean'], index=False)
    logger.info(f"  ✓ {len(df_merged_clean)} rows saved")
    
    # 6.2 enriched_data.csv
    logger.info(f"\n→ Saving {OUTPUT_FILES['enriched'].name}...")
    df_enriched.to_csv(OUTPUT_FILES['enriched'], index=False)
    logger.info(f"  ✓ {len(df_enriched)} rows saved")
    
    # 6.3 fact_stock_daily.csv
    logger.info(f"\n→ Saving {OUTPUT_FILES['fact_table'].name}...")
    fact_table.to_csv(OUTPUT_FILES['fact_table'], index=False)
    logger.info(f"  ✓ {len(fact_table)} rows saved")
    
    # 6.4 dim_date.csv
    logger.info(f"\n→ Saving {OUTPUT_FILES['dim_date'].name}...")
    dim_date.to_csv(OUTPUT_FILES['dim_date'], index=False)
    logger.info(f"  ✓ {len(dim_date)} rows saved")
    
    # 6.5 dim_stock.csv
    logger.info(f"\n→ Saving {OUTPUT_FILES['dim_stock'].name}...")
    dim_stock.to_csv(OUTPUT_FILES['dim_stock'], index=False)
    logger.info(f"  ✓ {len(dim_stock)} rows saved")


# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Main execution function."""
    logger.info("\n")
    logger.info("╔" + "=" * 68 + "╗")
    logger.info("║" + " " * 15 + "TUNVESTI DATA INTEGRATION SCRIPT" + " " * 21 + "║")
    logger.info("║" + " " * 10 + "Merging historical, daily, sectors, TUNINDEX, dividends" + " " * 1 + "║")
    logger.info("╚" + "=" * 68 + "╝")
    
    try:
        # Load
        dfs = load_data()
        if dfs is None:
            logger.error("✗ Failed to load data")
            return
        
        # Clean
        dfs_clean = clean_data(dfs)
        
        # Merge
        df_merged = merge_data(dfs_clean)
        
        # Save merged before derivations
        logger.info(f"\n→ Saving merged_clean_data.csv before metric derivation...")
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        df_merged.to_csv(OUTPUT_FILES['merged_clean'], index=False)
        logger.info(f"  ✓ {len(df_merged)} rows saved")
        
        # Derive metrics
        df_enriched = derive_metrics(df_merged)
        
        # Create dimension tables
        dim_date, dim_stock = create_dimension_tables(df_enriched)
        
        # Create fact table
        fact_table = create_fact_table(df_enriched)
        
        # Save all outputs
        save_outputs(df_merged, df_enriched, fact_table, dim_date, dim_stock)
        
        # Final summary
        logger.info("\n" + "=" * 70)
        logger.info("✓ INTEGRATION COMPLETE")
        logger.info("=" * 70)
        logger.info(f"\nSummary:")
        logger.info(f"  • Merged dataset: {len(df_enriched)} rows, {len(df_enriched.columns)} columns")
        logger.info(f"  • Date range: {df_enriched['date'].min()} to {df_enriched['date'].max()}")
        logger.info(f"  • Unique stocks: {df_enriched['ticker'].nunique()}")
        logger.info(f"  • Unique dates: {df_enriched['date'].nunique()}")
        logger.info(f"  • Dimension tables:")
        logger.info(f"    - dim_date: {len(dim_date)} rows")
        logger.info(f"    - dim_stock: {len(dim_stock)} rows")
        logger.info(f"  • Fact table: {len(fact_table)} rows")
        logger.info(f"\nOutput files created in: {OUTPUT_DIR}")
        
    except Exception as e:
        logger.error(f"\n✗ Error during execution: {e}", exc_info=True)
        return


if __name__ == '__main__':
    main()
