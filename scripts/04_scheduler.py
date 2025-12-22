"""
TUNVESTI - Step 4: Automated Daily Update Scheduler
This script runs the web scraper and merge process on a schedule
"""

import schedule
import time
import subprocess
import os
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('../output/scheduler.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Get the directory where scripts are located
SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
PYTHON_EXECUTABLE = os.path.join(os.path.dirname(SCRIPTS_DIR), '.venv', 'Scripts', 'python.exe')

# Alternative if above doesn't work
if not os.path.exists(PYTHON_EXECUTABLE):
    PYTHON_EXECUTABLE = 'python'

def run_scraper():
    """
    Run the web scraper to collect daily data
    """
    logger.info("=== RUNNING WEB SCRAPER ===")
    
    try:
        script_path = os.path.join(SCRIPTS_DIR, '02_scrape_ilboursa_daily.py')
        result = subprocess.run(
            [PYTHON_EXECUTABLE, script_path],
            cwd=SCRIPTS_DIR,
            capture_output=True,
            text=True,
            timeout=300  # 5 minutes timeout
        )
        
        if result.returncode == 0:
            logger.info("Web scraper completed successfully")
            logger.info(f"STDOUT:\n{result.stdout}")
        else:
            logger.error(f"Web scraper failed with code {result.returncode}")
            logger.error(f"STDERR:\n{result.stderr}")
    
    except subprocess.TimeoutExpired:
        logger.error("Web scraper timed out")
    except Exception as e:
        logger.error(f"Error running web scraper: {str(e)}")

def run_merger():
    """
    Run the data merge script to combine historical and recent data
    """
    logger.info("=== RUNNING DATA MERGER ===")
    
    try:
        script_path = os.path.join(SCRIPTS_DIR, '03_merge_data.py')
        result = subprocess.run(
            [PYTHON_EXECUTABLE, script_path],
            cwd=SCRIPTS_DIR,
            capture_output=True,
            text=True,
            timeout=300  # 5 minutes timeout
        )
        
        if result.returncode == 0:
            logger.info("Data merger completed successfully")
            logger.info(f"STDOUT:\n{result.stdout}")
        else:
            logger.error(f"Data merger failed with code {result.returncode}")
            logger.error(f"STDERR:\n{result.stderr}")
    
    except subprocess.TimeoutExpired:
        logger.error("Data merger timed out")
    except Exception as e:
        logger.error(f"Error running data merger: {str(e)}")

def daily_update_job():
    """
    Complete daily update job: scrape + merge
    """
    logger.info(f"\n{'='*60}")
    logger.info(f"DAILY UPDATE JOB STARTED at {datetime.now()}")
    logger.info(f"{'='*60}\n")
    
    # Run scraper first
    run_scraper()
    
    # Wait a moment
    time.sleep(5)
    
    # Then run merger
    run_merger()
    
    logger.info(f"\n{'='*60}")
    logger.info(f"DAILY UPDATE JOB COMPLETED at {datetime.now()}")
    logger.info(f"{'='*60}\n")

def schedule_jobs():
    """
    Schedule the daily update job
    """
    
    # Schedule for 3 PM (15:00) daily, Monday to Friday
    # Adjust time to match your market close time (typically 2-3 PM Tunisia time)
    schedule.every().monday.at("15:00").do(daily_update_job)
    schedule.every().tuesday.at("15:00").do(daily_update_job)
    schedule.every().wednesday.at("15:00").do(daily_update_job)
    schedule.every().thursday.at("15:00").do(daily_update_job)
    schedule.every().friday.at("15:00").do(daily_update_job)
    
    logger.info("Scheduler initialized:")
    logger.info("  - Daily updates: Monday-Friday at 15:00 (3 PM)")
    logger.info("  - Adjust time in this script if needed")

def main():
    """
    Main scheduler loop
    """
    
    logger.info("="*60)
    logger.info("TUNVESTI AUTOMATED UPDATE SCHEDULER STARTED")
    logger.info("="*60)
    logger.info(f"Current time: {datetime.now()}")
    logger.info(f"Python executable: {PYTHON_EXECUTABLE}")
    logger.info(f"Scripts directory: {SCRIPTS_DIR}\n")
    
    # Schedule jobs
    schedule_jobs()
    
    # Main loop
    logger.info("Scheduler running. Press Ctrl+C to stop.\n")
    
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    
    except KeyboardInterrupt:
        logger.info("\nScheduler stopped by user")
    except Exception as e:
        logger.error(f"Scheduler error: {str(e)}", exc_info=True)

if __name__ == "__main__":
    main()
