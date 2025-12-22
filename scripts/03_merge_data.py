"""
TUNVESTI - Step 3: Merge Historical and Scraped Data
This script merges Kaggle historical data (2010-2022) with daily scraped data (2023+)
"""

import pandas as pd
import os
from glob import glob
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('../output/merge_results.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def merge_historical_and_updates(historical_path, updates_folder):
    """
    Merge historical Kaggle data with daily scraped updates
    
    Parameters:
    historical_path (str): Path to historical_stocks_2010_2022.csv
    updates_folder (str): Path to folder containing updated_stocks_*.csv files
    
    Returns:
    pd.DataFrame: Merged dataframe with all historical and recent data
    """
    
    logger.info("Starting merge process...")
    
    # Load historical data
    if not os.path.exists(historical_path):
        logger.error(f"Historical file not found: {historical_path}")
        raise FileNotFoundError(f"Historical file not found: {historical_path}")
    
    logger.info(f"Loading historical data from: {historical_path}")
    historical_df = pd.read_csv(historical_path)
    historical_df['Date'] = pd.to_datetime(historical_df['Date'])
    logger.info(f"Loaded {len(historical_df)} rows from historical data")
    
    # Load all update files
    if not os.path.exists(updates_folder):
        logger.warning(f"Updates folder not found: {updates_folder}")
        logger.info("Proceeding with historical data only...")
        update_dfs = []
    else:
        update_files = sorted(glob(os.path.join(updates_folder, 'updated_stocks_*.csv')))
        logger.info(f"Found {len(update_files)} update files")
        
        update_dfs = []
        for file in update_files:
            try:
                df = pd.read_csv(file)
                df['Date'] = pd.to_datetime(df['Date'])
                update_dfs.append(df)
                logger.info(f"Loaded {file} ({len(df)} rows)")
            except Exception as e:
                logger.warning(f"Error loading {file}: {str(e)}")
                continue
    
    # Load TUNINDEX data
    tunindex_files = sorted(glob(os.path.join(updates_folder, 'updated_index_*.csv')))
    tunindex_dfs = []
    for file in tunindex_files:
        try:
            df = pd.read_csv(file)
            df['Date'] = pd.to_datetime(df['Date'])
            tunindex_dfs.append(df)
            logger.info(f"Loaded TUNINDEX from {file}")
        except Exception as e:
            logger.warning(f"Error loading TUNINDEX {file}: {str(e)}")
            continue
    
    if tunindex_dfs:
        tunindex_merged = pd.concat(tunindex_dfs, ignore_index=True)
        tunindex_merged = tunindex_merged.drop_duplicates(subset=['Date'], keep='first')
        logger.info(f"Loaded TUNINDEX data for {len(tunindex_merged)} dates")
    else:
        tunindex_merged = None
        logger.warning("No TUNINDEX data found")
    
    # Concatenate all data
    if update_dfs:
        logger.info("Merging historical and update data...")
        updates_df = pd.concat(update_dfs, ignore_index=True)
        logger.info(f"Total update rows: {len(updates_df)}")
        
        full_df = pd.concat([historical_df, updates_df], ignore_index=True)
    else:
        logger.info("No updates to merge, using historical data only")
        full_df = historical_df.copy()
    
    # Merge TUNINDEX data
    if tunindex_merged is not None:
        logger.info("Merging TUNINDEX data...")
        full_df = full_df.merge(tunindex_merged, on='Date', how='left')
        logger.info("TUNINDEX data merged successfully")
    
    # Remove duplicates (keep first occurrence)
    logger.info("Removing duplicates...")
    initial_rows = len(full_df)
    full_df = full_df.drop_duplicates(subset=['Date', 'Ticker'], keep='first')
    removed_rows = initial_rows - len(full_df)
    logger.info(f"Removed {removed_rows} duplicate rows")
    
    # Sort by Ticker and Date
    full_df.sort_values(['Ticker', 'Date'], inplace=True)
    
    logger.info(f"\n=== MERGE SUMMARY ===")
    logger.info(f"Total rows: {len(full_df)}")
    logger.info(f"Date range: {full_df['Date'].min()} to {full_df['Date'].max()}")
    logger.info(f"Unique tickers: {full_df['Ticker'].nunique()}")
    logger.info(f"Columns: {full_df.columns.tolist()}")
    
    return full_df

def calculate_basic_metrics(df):
    """
    Calculate basic financial metrics for the dataset
    
    Parameters:
    df (pd.DataFrame): Stock data with Close prices
    
    Returns:
    pd.DataFrame: Updated dataframe with Return and Volatility columns
    """
    
    logger.info("Calculating returns and volatility...")
    
    # Reset index to make groupby work properly
    df = df.reset_index(drop=True)
    
    # Calculate daily returns grouped by ticker
    df['Return'] = df.groupby('Ticker')['Close'].pct_change(fill_method=None)
    
    # Calculate 30-day rolling volatility (annualized) - fix index issue
    volatility_list = []
    for ticker in df['Ticker'].unique():
        ticker_data = df[df['Ticker'] == ticker].copy()
        ticker_data['Volatility_30d'] = ticker_data['Return'].rolling(30).std() * (252**0.5)
        volatility_list.append(ticker_data)
    
    df = pd.concat(volatility_list, ignore_index=True)
    df = df.sort_values(['Ticker', 'Date']).reset_index(drop=True)
    
    logger.info("Basic metrics calculated successfully")
    
    return df

def save_merged_data(df, output_path):
    """
    Save merged dataset to CSV
    
    Parameters:
    df (pd.DataFrame): Dataframe to save
    output_path (str): Path where to save the CSV
    """
    
    output_dir = os.path.dirname(output_path)
    os.makedirs(output_dir, exist_ok=True)
    
    df.to_csv(output_path, index=False)
    logger.info(f"Merged data saved to: {output_path}")

def generate_data_quality_report(df):
    """
    Generate a data quality report
    
    Parameters:
    df (pd.DataFrame): Dataframe to analyze
    """
    
    logger.info("\n=== DATA QUALITY REPORT ===")
    
    # Missing values
    logger.info("\nMissing values:")
    missing = df.isnull().sum()
    for col, count in missing.items():
        if count > 0:
            pct = (count / len(df)) * 100
            logger.info(f"  {col}: {count} ({pct:.2f}%)")
    
    # Data type check
    logger.info("\nData types:")
    for col, dtype in df.dtypes.items():
        logger.info(f"  {col}: {dtype}")
    
    # Statistics
    logger.info("\nNumeric statistics:")
    logger.info(df.describe().to_string())
    
    # Per-ticker row count
    logger.info("\nRows per ticker (sample of top 10):")
    ticker_counts = df['Ticker'].value_counts()
    for ticker, count in ticker_counts.head(10).items():
        logger.info(f"  {ticker}: {count} rows")

def main():
    """
    Main execution function
    """
    
    logger.info("=== TUNVESTI Data Merge Started ===\n")
    
    try:
        # Define paths (with absolute path handling)
        import os
        script_dir = os.path.dirname(os.path.abspath(__file__))
        base_dir = os.path.dirname(script_dir)
        historical_path = os.path.join(base_dir, 'data', 'historical_stocks_2010_2022.csv')
        updates_folder = os.path.join(base_dir, 'output', 'daily_updates')
        output_path = os.path.join(base_dir, 'output', 'final_tunvesti_dataset.csv')
        
        # Merge data
        merged_df = merge_historical_and_updates(historical_path, updates_folder)
        
        # Calculate metrics
        merged_df = calculate_basic_metrics(merged_df)
        
        # Save merged data
        save_merged_data(merged_df, output_path)
        
        # Generate quality report
        generate_data_quality_report(merged_df)
        
        # Display sample
        logger.info("\n=== SAMPLE DATA (First 10 rows) ===")
        logger.info(f"\n{merged_df.head(10).to_string()}")
        
        logger.info("\n=== MERGE COMPLETED SUCCESSFULLY ===\n")
        
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}", exc_info=True)
        raise

if __name__ == "__main__":
    main()
