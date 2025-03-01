from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from app.tasks import check_alerts
from time import sleep
import json
import random
import time
import schedule
import threading
from datetime import datetime, timezone
import os
import pytz
# Global variable to track scraper status
scraper_running = False

def is_trading_hours():
    """Returns True if the current time is within 9:20 AM to 4:40 PM on weekdays in Pakistan time"""
    # Get current time in Pakistan timezone
    pakistan_tz = pytz.timezone('Asia/Karachi')
    now = datetime.now(pytz.UTC).astimezone(pakistan_tz)
    return now.weekday() < 5 and (9, 20) <= (now.hour, now.minute) <= (16, 40)

def scrape_psx():
    # Load tickers from JSON file
    try:
        # Get the directory where the script is located
        script_dir = os.path.dirname(os.path.abspath(__file__))
        # Build the absolute path to the tickers.json file
        tickers_path = os.path.join(script_dir, "data", "tickers.json")
        with open(tickers_path, "r") as f:
            tickers_data = json.load(f)
        print(f"Loaded {len(tickers_data)} tickers from tickers.json")
    except Exception as e:
        print(f"Error loading tickers: {e}")
        return
    
    options = Options()
    options.add_argument("--headless")  # Run Chrome in headless mode
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    # Set up the Chrome WebDriver
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    url = "https://dps.psx.com.pk/"
    driver.get(url)
    print('url loaded')
    stock_data = []
    
    try:
        # First wait for the page to load and the select element to be present
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "select[name='DataTables_Table_0_length']"))
        )
        print('Page loaded')
        sleep(2)
        
        # Set display to show all entries
        select_element = driver.find_element(By.CSS_SELECTOR, "select[name='DataTables_Table_0_length']")
        driver.execute_script("arguments[0].value = '-1'; arguments[0].dispatchEvent(new Event('change'));", select_element)
        print('Select element set to "All" using JavaScript')
        
        # Wait for table to fully load with all entries
        sleep(5)  # Give time for all data to load
        
        # Process each ticker
        for ticker_entry in tickers_data:
            ticker_symbol = ticker_entry["symbol"]
            ticker_name = ticker_entry["name"]
            
            try:
                # Find the element with the current ticker symbol
                element = driver.find_element(By.CSS_SELECTOR, f"td[data-search='{ticker_symbol}']")
                parent_row = element.find_element(By.XPATH, "./parent::tr")
                td_elements = parent_row.find_elements(By.TAG_NAME, "td")[:6]
                
                if len(td_elements) < 6:
                    print(f"Not enough columns found for {ticker_symbol}")
                    continue

                # Extract values
                ticker = td_elements[0].get_attribute('textContent').strip()
                ldcp = td_elements[1].get_attribute('textContent').strip()
                open_price = td_elements[2].get_attribute('textContent').strip()
                high = td_elements[3].get_attribute('textContent').strip()
                low = td_elements[4].get_attribute('textContent').strip()
                current = td_elements[5].get_attribute('textContent').strip()
                
                # Add to our results
                stock_data.append({
                    "symbol": ticker,
                    "name": ticker_name,
                    "ldcp": ldcp,
                    "open": open_price,
                    "high": high,
                    "low": low,
                    "current": current
                })
                
                print(f"Processed {ticker_symbol}: {current}")
                
            except Exception as e:
                print(f"Error processing ticker {ticker_symbol}: {e}")
                # Continue with next ticker even if this one fails
                continue
        
        # Save all collected data to a JSON file
        script_dir = os.path.dirname(os.path.abspath(__file__))
        tickers_path = os.path.join(script_dir, "data", "latest_stock_price.json")
        with open(tickers_path, "w") as f:
            json.dump(stock_data, f, indent=4)
          
        print(f"Successfully processed {len(stock_data)} stocks. Data saved to latest_stock_price.json")
        sleep(2)
        check_alerts()

    except Exception as e:
        print(f"Error in main processing: {e}")
    finally:
        driver.quit()


def scraper():
    global scraper_running
    scraper_running = True
    print(f"Scraping data at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    # scrape_psx()
    check_alerts()
    # Schedule the next run with a random interval (8 to 15 minutes)
    next_interval = random.randint(8, 15)
    print(f"Next scrape in {next_interval} minutes")
    schedule.every(next_interval).minutes.do(scraper)



def run_scheduler():
    """Background thread function to run the scraper only during trading hours."""
    global scraper_running
    print("Background scraper started...")
    
    while True:
        if is_trading_hours():
            if not scraper_running:
                scraper()  # Start scraping if not already running
            schedule.run_pending()
        else:
            scraper_running = False  # Stop scraper outside trading hours
        time.sleep(600)  # Sleep to optimize CPU usage

# Initialize global thread variable
scraper_thread = None

def start_scheduler():
    """Function to start the scheduler thread when the FastAPI app starts."""
    global scraper_thread
    if scraper_thread is None or not scraper_thread.is_alive():
        scraper_thread = threading.Thread(target=run_scheduler, daemon=True)
        scraper_thread.start()
        print("PSX Scraper scheduler started")
    else:
        print("PSX Scraper scheduler already running")

def stop_scheduler():
    """Function to stop the scheduler thread when the FastAPI app shuts down."""
    global scraper_running, scraper_thread
    scraper_running = False
    schedule.clear()  # Clear all scheduled jobs
    print("PSX Scraper scheduler stopped")

# Start the scraper in a separate thread
# scraper_thread = threading.Thread(target=run_scheduler, daemon=True)
# scraper_thread.start()
