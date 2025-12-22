"""
TUNVESTI - Step 1: Load Kaggle Historical Data (2010-2022)
This script loads all individual stock CSV files from Kaggle and merges them
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
        logging.FileHandler('../output/data_loading.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def load_kaggle_data(kaggle_folder):
    """
    Load all CSV files from Kaggle dataset folder
    
    Parameters:
    kaggle_folder (str): Path to folder containing individual stock CSVs
    
    Returns:
    pd.DataFrame: Merged dataframe with all stocks
    """
    
    logger.info("Starting Kaggle data loading...")
    logger.info(f"Looking for CSV files in: {kaggle_folder}")
    
    if not os.path.exists(kaggle_folder):
        logger.error(f"Folder not found: {kaggle_folder}")
        raise FileNotFoundError(f"Kaggle folder not found: {kaggle_folder}")
    
    # Find all CSV files
    csv_files = glob(os.path.join(kaggle_folder, '*.csv'))
    logger.info(f"Found {len(csv_files)} CSV files")
    
    if len(csv_files) == 0:
        logger.error("No CSV files found in Kaggle folder!")
        raise FileNotFoundError("No CSV files found in the Kaggle folder")
    
    dataframes = []
    
    # Load each file
    for file in sorted(csv_files):
        try:
            ticker = os.path.basename(file).replace('.csv', '')
            df = pd.read_csv(file)
            
            # Add ticker column
            df['Ticker'] = ticker
            
            # Convert Date column to datetime
            df['Date'] = pd.to_datetime(df['Date'])
            
            # Filter to 2022 or earlier
            df = df[df['Date'] <= '2022-12-31']
            
            dataframes.append(df)
            logger.info(f"Loaded {ticker}: {len(df)} rows")
            
        except Exception as e:
            logger.warning(f"Error loading {file}: {str(e)}")
            continue
    
    if not dataframes:
        logger.error("No data could be loaded!")
        raise ValueError("No data could be loaded from CSV files")
    
    # Merge all dataframes
    logger.info("Merging all data...")
    merged_df = pd.concat(dataframes, ignore_index=True)
    
    # Sort by Ticker and Date
    merged_df.sort_values(['Ticker', 'Date'], inplace=True)
    
    logger.info(f"\n=== MERGE SUMMARY ===")
    logger.info(f"Total rows: {len(merged_df)}")
    logger.info(f"Date range: {merged_df['Date'].min()} to {merged_df['Date'].max()}")
    logger.info(f"Unique tickers: {merged_df['Ticker'].nunique()}")
    logger.info(f"Tickers: {sorted(merged_df['Ticker'].unique())}")
    logger.info(f"Columns: {merged_df.columns.tolist()}")
    
    return merged_df

def save_data(df, output_path):
    """
    Save merged dataframe to CSV
    
    Parameters:
    df (pd.DataFrame): Data to save
    output_path (str): Path to output file
    """
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)
    logger.info(f"Data saved to: {output_path}")
    logger.info(f"Total rows: {len(df)}")
    logger.info(f"Total columns: {len(df.columns)}")

def main():
    """
    Main execution function
    """
    
    try:
        logger.info("=== TUNVESTI Step 1: Load Kaggle Data ===\n")
        
        # Get absolute paths
        import os
        script_dir = os.path.dirname(os.path.abspath(__file__))
        base_dir = os.path.dirname(script_dir)  # Parent of scripts folder
        kaggle_folder = os.path.join(base_dir, 'data', 'kaggle_source')
        output_path = os.path.join(base_dir, 'data', 'historical_stocks_2010_2022.csv')
        
        # Load data
        merged_df = load_kaggle_data(kaggle_folder)
        
        # Save merged data
        save_data(merged_df, output_path)
        
        # Display sample
        logger.info("\n=== SAMPLE DATA (First 10 rows) ===")
        logger.info(f"\n{merged_df.head(10).to_string()}")
        
        logger.info("\n=== KAGGLE DATA LOADED SUCCESSFULLY ===\n")
        
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}", exc_info=True)
        raise

if __name__ == "__main__":
    main()
