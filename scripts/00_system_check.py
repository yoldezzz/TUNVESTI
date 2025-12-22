"""
TUNVESTI - System Configuration and Testing Utility
Verifies that all dependencies are installed and environment is ready
"""

import sys
import os
import subprocess
import logging
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def check_python_version():
    """Check if Python version is 3.8 or higher"""
    logger.info("Checking Python version...")
    version = sys.version_info
    
    if version.major >= 3 and version.minor >= 8:
        logger.info(f"✓ Python {version.major}.{version.minor}.{version.micro} - OK")
        return True
    else:
        logger.error(f"✗ Python {version.major}.{version.minor} - REQUIRES 3.8+")
        return False

def check_packages():
    """Check if all required packages are installed"""
    logger.info("\nChecking required packages...")
    
    required_packages = {
        'pandas': 'pandas',
        'requests': 'requests',
        'bs4': 'beautifulsoup4',
        'lxml': 'lxml',
        'schedule': 'schedule'
    }
    
    all_ok = True
    
    for import_name, package_name in required_packages.items():
        try:
            __import__(import_name)
            logger.info(f"✓ {package_name} - OK")
        except ImportError:
            logger.error(f"✗ {package_name} - NOT INSTALLED")
            all_ok = False
    
    return all_ok

def check_directories():
    """Check if all required directories exist"""
    logger.info("\nChecking directory structure...")
    
    directories = [
        'scripts',
        'data',
        'output',
        'output/daily_updates'
    ]
    
    all_ok = True
    
    for dir_name in directories:
        dir_path = os.path.join('..', dir_name)
        if os.path.exists(dir_path):
            logger.info(f"✓ {dir_name}/ - EXISTS")
        else:
            logger.warning(f"⚠ {dir_name}/ - MISSING (will be created)")
    
    return all_ok

def check_scripts():
    """Check if all required scripts exist"""
    logger.info("\nChecking script files...")
    
    scripts = [
        '01_load_kaggle_data.py',
        '02_scrape_ilboursa_daily.py',
        '03_merge_data.py',
        '04_scheduler.py'
    ]
    
    all_ok = True
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    for script in scripts:
        script_path = os.path.join(script_dir, script)
        if os.path.exists(script_path):
            logger.info(f"✓ {script} - EXISTS")
        else:
            logger.error(f"✗ {script} - NOT FOUND")
            all_ok = False
    
    return all_ok

def test_imports():
    """Test that all imports work correctly"""
    logger.info("\nTesting imports...")
    
    try:
        import pandas as pd
        logger.info(f"✓ pandas {pd.__version__}")
    except Exception as e:
        logger.error(f"✗ pandas import failed: {str(e)}")
        return False
    
    try:
        import requests
        logger.info(f"✓ requests {requests.__version__}")
    except Exception as e:
        logger.error(f"✗ requests import failed: {str(e)}")
        return False
    
    try:
        from bs4 import BeautifulSoup
        logger.info(f"✓ BeautifulSoup4")
    except Exception as e:
        logger.error(f"✗ BeautifulSoup4 import failed: {str(e)}")
        return False
    
    try:
        import schedule
        logger.info(f"✓ schedule {schedule.__version__}")
    except Exception as e:
        logger.error(f"✗ schedule import failed: {str(e)}")
        return False
    
    return True

def test_internet_connection():
    """Test internet connectivity"""
    logger.info("\nTesting internet connection...")
    
    try:
        response = requests.get('https://www.google.com', timeout=5)
        if response.status_code == 200:
            logger.info("✓ Internet connection - OK")
            return True
    except:
        pass
    
    logger.warning("⚠ Cannot reach internet (may affect web scraping)")
    return False

def test_ilboursa_access():
    """Test if Ilboursa.com is accessible"""
    logger.info("\nTesting Ilboursa.com access...")
    
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get('https://www.ilboursa.com/marches/cours', headers=headers, timeout=10)
        if response.status_code == 200:
            logger.info("✓ Ilboursa.com - ACCESSIBLE")
            return True
        else:
            logger.warning(f"⚠ Ilboursa.com returned status {response.status_code}")
            return False
    except Exception as e:
        logger.warning(f"⚠ Cannot access Ilboursa.com: {str(e)}")
        return False

def generate_report(results):
    """Generate a summary report"""
    logger.info("\n" + "="*60)
    logger.info("SYSTEM CONFIGURATION REPORT")
    logger.info("="*60)
    
    if all(results.values()):
        logger.info("\n✅ ALL CHECKS PASSED - System ready!")
        logger.info("\nNext steps:")
        logger.info("1. Run: python 01_load_kaggle_data.py")
        logger.info("2. Run: python 02_scrape_ilboursa_daily.py")
        logger.info("3. Run: python 03_merge_data.py")
    else:
        logger.info("\n⚠️ SOME CHECKS FAILED - Review above errors")
        logger.info("\nTo fix:")
        logger.info("- Install packages: pip install -r ../requirements.txt")
        logger.info("- Create missing directories")
        logger.info("- Check internet connection")
    
    logger.info("\n" + "="*60)

def main():
    """Run all checks"""
    
    logger.info("="*60)
    logger.info("TUNVESTI SYSTEM CONFIGURATION CHECK")
    logger.info(f"Started at: {datetime.now()}")
    logger.info("="*60 + "\n")
    
    results = {
        'Python Version': check_python_version(),
        'Required Packages': check_packages(),
        'Directory Structure': check_directories(),
        'Script Files': check_scripts(),
        'Imports': test_imports(),
        'Internet Connection': test_internet_connection(),
        'Ilboursa Access': test_ilboursa_access()
    }
    
    generate_report(results)
    
    logger.info(f"Completed at: {datetime.now()}\n")
    
    return all(results.values())

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
