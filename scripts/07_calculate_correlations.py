"""
SCRIPT 07: CALCULATE STOCK CORRELATIONS
========================================
Purpose: Calculate correlation matrices between stocks and TUNINDEX
Output: 
  - data/correlation_stock_to_stock.csv (full correlation matrix)
  - data/correlation_stock_to_tunindex.csv (stock-to-benchmark correlations)
  - data/correlation_sector_to_tunindex.csv (sector-to-benchmark correlations)

This script:
1. Loads merged stock data and TUNINDEX data
2. Calculates 60-day rolling correlations
3. Creates correlation matrices for visualization
4. Identifies diversification opportunities
5. Calculates sector correlation to TUNINDEX
"""

import os
import sys
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging

# Setup absolute paths
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
data_dir = os.path.join(project_root, 'data')
output_dir = os.path.join(project_root, 'output')
log_file = os.path.join(output_dir, 'processing.log')

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
# DATA LOADING
# ============================================================================

def load_stock_data():
    """Load merged stock data with returns"""
    
    logger.info("=" * 70)
    logger.info("Loading stock data...")
    logger.info("=" * 70)
    
    data_path = os.path.join(output_dir, 'final_tunvesti_dataset.csv')
    
    if not os.path.exists(data_path):
        logger.error(f"Stock data not found at {data_path}")
        logger.info("Please run scripts 01-03 first to prepare data")
        return None
    
    try:
        df_stocks = pd.read_csv(data_path)
        df_stocks['Date'] = pd.to_datetime(df_stocks['Date'])
        
        logger.info(f"✓ Loaded {len(df_stocks)} stock records")
        logger.info(f"  Tickers: {df_stocks['Ticker'].nunique()}")
        logger.info(f"  Date range: {df_stocks['Date'].min()} to {df_stocks['Date'].max()}")
        
        return df_stocks
        
    except Exception as e:
        logger.error(f"Error loading stock data: {e}")
        return None

def load_tunindex_data():
    """Load TUNINDEX data"""
    
    logger.info("Loading TUNINDEX data...")
    
    data_path = os.path.join(data_dir, 'tunindex_historical.csv')
    
    if not os.path.exists(data_path):
        logger.warning(f"TUNINDEX data not found at {data_path}")
        logger.info("Please run script 06_scrape_tunindex.py first")
        return None
    
    try:
        df_tunindex = pd.read_csv(data_path)
        df_tunindex['Date'] = pd.to_datetime(df_tunindex['Date'])
        
        logger.info(f"✓ Loaded {len(df_tunindex)} TUNINDEX records")
        logger.info(f"  Date range: {df_tunindex['Date'].min()} to {df_tunindex['Date'].max()}")
        
        # Calculate TUNINDEX returns
        df_tunindex = df_tunindex.sort_values('Date').reset_index(drop=True)
        df_tunindex['TUNINDEX_Return'] = df_tunindex['Close'].pct_change()
        
        return df_tunindex[['Date', 'Close', 'TUNINDEX_Return']]
        
    except Exception as e:
        logger.error(f"Error loading TUNINDEX data: {e}")
        return None

def load_sector_mapping():
    """Load sector classification"""
    
    logger.info("Loading sector mapping...")
    
    data_path = os.path.join(data_dir, 'sector_mapping.csv')
    
    if not os.path.exists(data_path):
        logger.warning(f"Sector mapping not found at {data_path}")
        logger.info("Please run script 05_scrape_sector_classification.py first")
        return None
    
    try:
        df_sectors = pd.read_csv(data_path)
        logger.info(f"✓ Loaded sector mapping for {len(df_sectors)} stocks")
        return df_sectors
        
    except Exception as e:
        logger.error(f"Error loading sector mapping: {e}")
        return None

# ============================================================================
# CORRELATION CALCULATIONS
# ============================================================================

def calculate_stock_correlations(df_stocks):
    """
    Calculate stock-to-stock correlation matrix
    
    Uses rolling 60-day window to identify current market relationships
    """
    
    logger.info("\n" + "=" * 70)
    logger.info("Calculating Stock-to-Stock Correlations")
    logger.info("=" * 70)
    
    try:
        # Pivot to get daily returns by ticker
        df_pivot = df_stocks.pivot_table(
            index='Date',
            columns='Ticker',
            values='Return',
            aggfunc='first'
        )
        
        logger.info(f"Prepared pivot table: {df_pivot.shape[0]} dates × {df_pivot.shape[1]} tickers")
        
        # Calculate correlation matrix using ALL available data (not just 60 days)
        # This gives more stable correlation estimates with historical data
        df_recent = df_pivot.dropna(axis=1, how='all')  # Remove tickers with all NaN
        
        logger.info(f"Using {len(df_recent)} trading days for correlation (full historical period)")
        
        # Calculate correlation
        correlation_matrix = df_recent.corr()
        
        logger.info(f"✓ Correlation matrix calculated: {correlation_matrix.shape}")
        
        # Find highly correlated pairs (useful for diversification analysis)
        logger.info("\n" + "-" * 70)
        logger.info("TOP CORRELATED PAIRS (Useful for Diversification)")
        logger.info("-" * 70)
        
        # Get upper triangle of correlation matrix
        corr_pairs = []
        for i in range(len(correlation_matrix.columns)):
            for j in range(i+1, len(correlation_matrix.columns)):
                ticker1 = correlation_matrix.columns[i]
                ticker2 = correlation_matrix.columns[j]
                corr_value = correlation_matrix.iloc[i, j]
                
                corr_pairs.append({
                    'Ticker1': ticker1,
                    'Ticker2': ticker2,
                    'Correlation': corr_value
                })
        
        df_corr_pairs = pd.DataFrame(corr_pairs)
        df_corr_pairs = df_corr_pairs.sort_values('Correlation', ascending=False)
        
        # Show top positive correlations
        logger.info("\nHighly Correlated Pairs (AVOID combining - less diversification):")
        for idx, row in df_corr_pairs.head(10).iterrows():
            logger.info(f"  {row['Ticker1']:6s} ↔ {row['Ticker2']:6s} = {row['Correlation']:7.3f}")
        
        # Show negative correlations (good for diversification)
        logger.info("\nNegatively Correlated Pairs (GOOD for diversification):")
        for idx, row in df_corr_pairs.tail(10).iterrows():
            logger.info(f"  {row['Ticker1']:6s} ↔ {row['Ticker2']:6s} = {row['Correlation']:7.3f}")
        
        return correlation_matrix, df_corr_pairs
        
    except Exception as e:
        logger.error(f"Error calculating stock correlations: {e}", exc_info=True)
        return None, None

def calculate_stock_to_tunindex_correlation(df_stocks, df_tunindex):
    """
    Calculate correlation of each stock to TUNINDEX benchmark
    
    Measures how closely each stock follows the overall market
    High correlation = follows market trends
    Low correlation = independent/diversified
    """
    
    logger.info("\n" + "=" * 70)
    logger.info("Calculating Stock-to-TUNINDEX Correlations")
    logger.info("=" * 70)
    
    if df_tunindex is None:
        logger.warning("TUNINDEX data not available, skipping this calculation")
        return None
    
    try:
        # Merge stock and TUNINDEX data
        df_merged = df_stocks[['Date', 'Ticker', 'Return']].copy()
        df_merged = df_merged.merge(df_tunindex[['Date', 'TUNINDEX_Return']], on='Date')
        
        # Calculate correlation for each stock
        correlations = []
        
        for ticker in df_merged['Ticker'].unique():
            ticker_data = df_merged[df_merged['Ticker'] == ticker].copy()
            
            # Remove NaN values
            ticker_data = ticker_data.dropna(subset=['Return', 'TUNINDEX_Return'])
            
            if len(ticker_data) > 30:  # Need at least 30 days
                corr = ticker_data['Return'].corr(ticker_data['TUNINDEX_Return'])
                
                # Also calculate 60-day rolling correlation (volatility of correlation)
                rolling_corr = ticker_data.set_index('Date')['Return'].rolling(60).corr(
                    ticker_data.set_index('Date')['TUNINDEX_Return']
                )
                corr_std = rolling_corr.std() if len(rolling_corr) > 1 else 0
                
                correlations.append({
                    'Ticker': ticker,
                    'Correlation_to_TUNINDEX': corr,
                    'Correlation_Volatility': corr_std,
                    'Data_Points': len(ticker_data)
                })
        
        df_tunindex_corr = pd.DataFrame(correlations)
        df_tunindex_corr = df_tunindex_corr.sort_values('Correlation_to_TUNINDEX', ascending=False)
        
        logger.info(f"✓ Calculated correlations for {len(df_tunindex_corr)} stocks")
        
        logger.info("\nStocks Most Correlated to TUNINDEX (Follow market closely):")
        for idx, row in df_tunindex_corr.head(10).iterrows():
            logger.info(f"  {row['Ticker']:6s}: {row['Correlation_to_TUNINDEX']:7.3f}")
        
        logger.info("\nStocks Least Correlated to TUNINDEX (Good diversifiers):")
        for idx, row in df_tunindex_corr.tail(10).iterrows():
            logger.info(f"  {row['Ticker']:6s}: {row['Correlation_to_TUNINDEX']:7.3f}")
        
        return df_tunindex_corr
        
    except Exception as e:
        logger.error(f"Error calculating stock-to-TUNINDEX correlation: {e}", exc_info=True)
        return None

def calculate_sector_correlations(df_stocks, df_tunindex, df_sectors):
    """
    Calculate average correlation by sector to TUNINDEX
    
    Shows which sectors move with or against the overall market
    """
    
    logger.info("\n" + "=" * 70)
    logger.info("Calculating Sector-to-TUNINDEX Correlations")
    logger.info("=" * 70)
    
    if df_sectors is None or df_tunindex is None:
        logger.warning("Sector or TUNINDEX data not available, skipping sector correlations")
        return None
    
    try:
        # Merge with sector information
        df_merged = df_stocks[['Date', 'Ticker', 'Return']].copy()
        df_merged = df_merged.merge(df_sectors[['Ticker', 'Sector']], on='Ticker')
        df_merged = df_merged.merge(df_tunindex[['Date', 'TUNINDEX_Return']], on='Date')
        
        # Calculate correlation by sector
        sector_correlations = []
        
        for sector in df_merged['Sector'].unique():
            sector_data = df_merged[df_merged['Sector'] == sector].copy()
            sector_data = sector_data.dropna(subset=['Return', 'TUNINDEX_Return'])
            
            if len(sector_data) > 30:
                corr = sector_data['Return'].corr(sector_data['TUNINDEX_Return'])
                
                sector_correlations.append({
                    'Sector': sector,
                    'Correlation_to_TUNINDEX': corr,
                    'Stocks_in_Sector': sector_data['Ticker'].nunique(),
                    'Data_Points': len(sector_data)
                })
        
        df_sector_corr = pd.DataFrame(sector_correlations)
        df_sector_corr = df_sector_corr.sort_values('Correlation_to_TUNINDEX', ascending=False)
        
        logger.info(f"✓ Calculated correlations for {len(df_sector_corr)} sectors")
        
        logger.info("\nSector Correlations to TUNINDEX:")
        for idx, row in df_sector_corr.iterrows():
            logger.info(f"  {row['Sector']:20s}: {row['Correlation_to_TUNINDEX']:7.3f} ({row['Stocks_in_Sector']} stocks)")
        
        return df_sector_corr
        
    except Exception as e:
        logger.error(f"Error calculating sector correlations: {e}", exc_info=True)
        return None

# ============================================================================
# EXPORT RESULTS
# ============================================================================

def export_correlations(corr_matrix, corr_pairs, tunindex_corr, sector_corr):
    """Export all correlation results"""
    
    logger.info("\n" + "=" * 70)
    logger.info("EXPORTING CORRELATION MATRICES")
    logger.info("=" * 70)
    
    # Export stock-to-stock correlation matrix
    if corr_matrix is not None:
        output_path = os.path.join(data_dir, 'correlation_stock_to_stock.csv')
        corr_matrix.to_csv(output_path)
        logger.info(f"✓ Stock-to-stock correlation matrix: {output_path}")
    
    # Export correlation pairs
    if corr_pairs is not None:
        output_path = os.path.join(data_dir, 'correlation_pairs.csv')
        corr_pairs.to_csv(output_path, index=False)
        logger.info(f"✓ Correlation pairs analysis: {output_path}")
    
    # Export stock-to-TUNINDEX correlations
    if tunindex_corr is not None:
        output_path = os.path.join(data_dir, 'correlation_stock_to_tunindex.csv')
        tunindex_corr.to_csv(output_path, index=False)
        logger.info(f"✓ Stock-to-TUNINDEX correlation matrix: {output_path}")
    
    # Export sector-to-TUNINDEX correlations
    if sector_corr is not None:
        output_path = os.path.join(data_dir, 'correlation_sector_to_tunindex.csv')
        sector_corr.to_csv(output_path, index=False)
        logger.info(f"✓ Sector-to-TUNINDEX correlation matrix: {output_path}")
    
    logger.info("\n" + "=" * 70)
    logger.info("✅ CORRELATION ANALYSIS COMPLETE")
    logger.info("=" * 70)
    logger.info("\nKey Insights:")
    logger.info("• Use stock-to-stock correlations to identify diversification opportunities")
    logger.info("• Combine stocks with LOW correlation for better risk management")
    logger.info("• Stocks with LOW TUNINDEX correlation are good diversifiers")
    logger.info("• Sectors with HIGH TUNINDEX correlation move with overall market")
    logger.info("• Sectors with LOW TUNINDEX correlation offer hedge opportunities")

# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == "__main__":
    try:
        # Load data
        df_stocks = load_stock_data()
        df_tunindex = load_tunindex_data()
        df_sectors = load_sector_mapping()
        
        if df_stocks is None:
            logger.error("Cannot proceed without stock data")
            sys.exit(1)
        
        # Calculate correlations
        corr_matrix, corr_pairs = calculate_stock_correlations(df_stocks)
        tunindex_corr = calculate_stock_to_tunindex_correlation(df_stocks, df_tunindex)
        sector_corr = calculate_sector_correlations(df_stocks, df_tunindex, df_sectors)
        
        # Export results
        export_correlations(corr_matrix, corr_pairs, tunindex_corr, sector_corr)
        
        logger.info("\n✅ Script completed successfully!")
        sys.exit(0)
        
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)
