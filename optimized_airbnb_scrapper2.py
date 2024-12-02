import logging
import urllib.parse
import time
from typing import List, Dict, Tuple
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.options import Options
import pandas as pd
import streamlit as st
from datetime import datetime, timedelta
import sqlite3
from pathlib import Path
import requests
import re
import traceback
import subprocess


# Constants
CACHE_TTL_HOURS = 24
DB_FILE = "locations_cache.db"
WAIT_TIMEOUT = 10
PAGE_LOAD_DELAY = 3
CURRENCY_API_KEY = "cur_live_3JddjDyXw3TlQEHbmeThynFz81KeoCxsFe9tLPxI"  # Replace with your actual API key
BASE_CURRENCY = "INR"
TARGET_CURRENCIES = ["SAR", "AED", "USD"]

# Setup logging
def setup_logging():
    """Setup logging configuration."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    return logging.getLogger(__name__)

logger = setup_logging()

def init_db():
    """Initialize SQLite database for storing location cache metadata."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS location_cache(
            location TEXT PRIMARY KEY,
            timestamp TEXT
        )
    """)

    # Create currency rates table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS currency_rates(
            base_currency TEXT,
            target_currency TEXT,
            rate REAL,
            timestamp TEXT,
            PRIMARY KEY (base_currency, target_currency)
        )
    """)
    conn.commit()
    conn.close()

def get_currency_rates() -> Tuple[Dict[str, float], str]:
    """
    Get currency rates from database or API, ensuring daily rate updates.

    Returns:
    Tuple[Dict[str, float], str]: Dictionary of currency rates with target currencies as keys and the timestamp
    """
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    try:
        # Get today's date in the current timezone
        today = datetime.now().date().strftime("%Y-%m-%d")
        logger.info(f"Checking for currency rates for today: {today}")

        # Check for rates for today
        cursor.execute("""
            SELECT target_currency, rate, timestamp
            FROM currency_rates 
            WHERE base_currency = ? AND date(timestamp) = ?
        """, (BASE_CURRENCY, today))

        existing_rates = cursor.fetchall()
        logger.info(f"Existing rates found: {existing_rates}")

        # If rates exist for all target currencies, return them
        if len(existing_rates) == len(TARGET_CURRENCIES):
            rates_dict = {rate[0]: rate[1] for rate in existing_rates}
            # Assume all timestamps are the same; take the first one
            timestamp = existing_rates[0][2]
            logger.info(f"Returning cached rates: {rates_dict} at {timestamp}")
            return rates_dict, timestamp

        # If not, fetch new rates from API
        url = "https://api.currencyapi.com/v3/latest"
        params = {
            "apikey": CURRENCY_API_KEY,
            "base_currency": BASE_CURRENCY,
            "currencies": ",".join(TARGET_CURRENCIES)
        }

        response = requests.get(url, params=params)
        logger.info(f"API Response Status Code: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            logger.info(f"API Response Data: {data}")

            rates = {}
            # Use the exact current timestamp for storage
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # Clear old rates for this base currency
            cursor.execute("DELETE FROM currency_rates WHERE base_currency = ?", (BASE_CURRENCY,))

            # Store new rates
            for currency in TARGET_CURRENCIES:
                rate = data['data'][currency]['value']
                rates[currency] = rate
                logger.info(f"Storing rate for {currency}: {rate}")
                cursor.execute("""
                    INSERT INTO currency_rates (base_currency, target_currency, rate, timestamp)
                    VALUES (?, ?, ?, ?)
                """, (BASE_CURRENCY, currency, rate, timestamp))

            conn.commit()
            logger.info(f"Final rates to return: {rates} at {timestamp}")
            return rates, timestamp
        else:
            logger.error(f"Failed to fetch currency rates: {response.status_code}")
            return {}, ""
            
    except Exception as e:
        logger.error(f"Error getting currency rates: {str(e)}")
        return {}, ""
    finally:
        conn.close()

def extract_price_value(price_str: str) -> float:
    """Extract numeric price value from string."""
    try:
        # Remove ₹ symbol and any commas, then convert to float
        numeric_str = re.sub(r'[^\d.]', '', price_str)
        return float(numeric_str)
    except:
        return 0.0

def convert_price(price_str: str, rates: Dict[str, float]) -> Dict[str, str]:
    """Convert price to multiple currencies."""
    price_value = extract_price_value(price_str)
    converted_prices = {
        'INR': f"₹{price_value:,.2f}",
        'SAR': f"SAR {price_value * rates.get('SAR', 0):,.2f}",
        'AED': f"AED {price_value * rates.get('AED', 0):,.2f}",
        'USD': f"${price_value * rates.get('USD', 0):,.2f}"
    }
    return converted_prices

def is_location_cached(location: str) -> bool:
    """Check if location is cached and within TTL."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT timestamp FROM location_cache WHERE location = ?", (location,))
        row = cursor.fetchone()
        if row:
            cached_time = datetime.strptime(row[0], "%Y-%m-%d %H:%M:%S")
            return datetime.now() - cached_time < timedelta(hours=CACHE_TTL_HOURS)
        return False
    finally:
        conn.close()

def update_location_cache(location: str):
    """Update cache timestamp for a location."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    try:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("""
            INSERT OR REPLACE INTO location_cache (location, timestamp)
            VALUES (?, ?)
        """, (location, timestamp))
        conn.commit()
    finally:
        conn.close()

def get_cached_locations() -> List[Tuple[str, str]]:
    """Get all cached locations with their timestamps."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    try:
        return cursor.execute("SELECT location, timestamp FROM location_cache").fetchall()
    finally:
        conn.close()

def clear_location_cache(location: str):
    """Clear cache for specific location."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM location_cache WHERE location = ?", (location,))
        conn.commit()
        # Also clear the corresponding Streamlit cache
        st.cache_data.clear()
        logger.info(f"Cache cleared for location: {location}")
    except Exception as e:
        logger.error(f"Error clearing cache for location {location}: {str(e)}")
    finally:
        conn.close()

def clear_all_cache():
    """Clear all cache data."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM location_cache")
        cursor.execute("DELETE FROM currency_rates")
        conn.commit()
        # Clear Streamlit cache as well
        st.cache_data.clear()
        logger.info("All cache cleared successfully.")
    except Exception as e:
        logger.error(f"Error clearing all cache: {str(e)}")
    finally:
        conn.close()

def cleanup_stale_cache():
    """Remove stale cache entries."""
    threshold = (datetime.now() - timedelta(hours=CACHE_TTL_HOURS)).strftime("%Y-%m-%d %H:%M:%S")
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    try:
        # Get stale locations before deleting them
        cursor.execute("SELECT location FROM location_cache WHERE timestamp < ?", (threshold,))
        stale_locations = cursor.fetchall()

        # Delete stale entries
        cursor.execute("DELETE FROM location_cache WHERE timestamp < ?", (threshold,))

        # Clear currency rates older than today
        today = datetime.now().date().strftime("%Y-%m-%d")
        cursor.execute("DELETE FROM currency_rates WHERE date(timestamp) < ?", (today,))

        conn.commit()

        # Clear Streamlit cache if any locations were stale
        if stale_locations:
            st.cache_data.clear()
            logger.info(f"Stale cache entries removed: {stale_locations}")
    except Exception as e:
        logger.error(f"Error during cache cleanup: {str(e)}")
    finally:
        conn.close()


logger = setup_logging()


def get_driver():
    """Create and return a configured WebDriver instance."""
    try:
        # First check installed versions
        try:
            # Get Chromium version
            chrome_version_output = subprocess.check_output(['chromium', '--version']).decode()
            st.write(f"Installed Chromium: {chrome_version_output.strip()}")
            
            # Get ChromeDriver version
            chromedriver_version_output = subprocess.check_output(['chromedriver', '--version']).decode()
            st.write(f"Installed ChromeDriver: {chromedriver_version_output.strip()}")
            
        except Exception as e:
            st.warning(f"Version check failed: {str(e)}")
        
        # Initialize Chrome options
        chrome_options = Options()
        
        # Basic required options
        chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        
        # Set binary location
        chrome_options.binary_location = "/usr/bin/chromium"
        
        # Additional options
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-web-security")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--remote-debugging-port=9222")
        
        # Generic user agent
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/stable Safari/537.36")
        
        # Initialize service with logging
        service = Service(
            executable_path='/usr/bin/chromedriver',
            log_path='/tmp/chromedriver.log',
            service_args=['--verbose']
        )
        st.write("Attempting to initialize ChromeDriver...")
        
        # Try to create driver
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        # Verify browser capabilities
        # st.write("Driver capabilities:")
        # st.write(f"Browser version: {driver.capabilities.get('browserVersion', 'unknown')}")
        # st.write(f"ChromeDriver version: {driver.capabilities.get('chrome', {}).get('chromedriverVersion', 'unknown')}")
        
        return driver
        
    except Exception as e:
        st.error(f"Failed to initialize ChromeDriver: {str(e)}")
        
        # Try to read ChromeDriver log
        try:
            with open('/tmp/chromedriver.log', 'r') as f:
                st.code(f.read(), language='text')
        except:
            st.warning("Could not read ChromeDriver log")
            
        st.code(traceback.format_exc())
        raise
@st.cache_data(ttl=CACHE_TTL_HOURS * 3600)
def scrape_listings(search_location: str) -> Tuple[List[Dict], List[int]]:
    """Scrape all listings for a given location with caching."""
    # driver = None
    try:
        driver = get_driver()
        all_listings = []
        listings_per_page = []

        # Get currency rates once
        currency_rates, _ = get_currency_rates()

        # Get first page
        search_url = f"https://www.airbnb.co.in/s/{urllib.parse.quote(search_location)}/homes"
        driver.get(search_url)

        while True:
            # Wait for listings to load
            time.sleep(PAGE_LOAD_DELAY)
            soup = BeautifulSoup(driver.page_source, 'html.parser')

            # Process current page
            listing_elements = soup.find_all('div', {'itemprop': 'itemListElement'})
            page_listings = []

            for element in listing_elements:
                try:
                    url_meta = element.find('meta', {'itemprop': 'url'})
                    if url_meta and url_meta.get('content'):
                        price_str = element.find('span', class_="_11jcbg2").text.strip() if element.find('span', class_="_11jcbg2") else "N/A"

                        # Convert price to multiple currencies
                        prices = convert_price(price_str, currency_rates) if price_str != "N/A" else {
                            'INR': 'N/A', 'SAR': 'N/A', 'AED': 'N/A', 'USD': 'N/A'
                        }
                        listing_info = {
                            'url': url_meta['content'].split('?')[0],
                            'price_inr': prices['INR'],
                            'price_sar': prices['SAR'],
                            'price_aed': prices['AED'],
                            'price_usd': prices['USD'],
                            'title': element.find('meta', {'itemprop': 'name'})['content'] if element.find('meta', {'itemprop': 'name'}) else "N/A",
                            'rating': element.find('span', text=lambda t: t and 'average rating' in t).text.strip() if element.find('span', text=lambda t: t and 'average rating' in t) else "N/A",
                            'location': search_location
                        }
                        page_listings.append(listing_info)
                except Exception as e:
                    logger.warning(f"Error processing listing element: {str(e)}")
                    continue

            listings_per_page.append(len(page_listings))
            all_listings.extend(page_listings)

            # Try to go to next page
            try:
                next_button = WebDriverWait(driver, WAIT_TIMEOUT).until(
                    EC.presence_of_element_located((By.XPATH, "//a[@aria-label='Next']"))
                )
                if not next_button.is_enabled():
                    break
                next_button.click()
                time.sleep(PAGE_LOAD_DELAY)
            except (TimeoutException, NoSuchElementException):
                break

        # Update location cache in database
        update_location_cache(search_location)
        return all_listings, listings_per_page

    except Exception as e:
        logger.error(f"Error during scraping: {str(e)}")
        raise
    finally:
        if driver:
            driver.quit()

def clear_currency_rates_cache():
    """Clear cached currency rates from the database."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM currency_rates WHERE base_currency = ?", (BASE_CURRENCY,))
        conn.commit()
        # Clear Streamlit cache related to currency rates if any
        st.cache_data.clear()
        logger.info("Currency rates cache cleared successfully.")
    except Exception as e:
        logger.error(f"Error clearing currency rates cache: {str(e)}")
    finally:
        conn.close()

def create_sidebar():
    """Create and manage the sidebar with cache information."""
    with st.sidebar:
        st.title("Cache Management")

        # Display current exchange rates
        st.subheader("Today's Exchange Rates")
        rates, rates_timestamp = get_currency_rates()
        if rates:
            st.write(f"**Exchange Rates as of:** {rates_timestamp}")
            st.write(f"1 {BASE_CURRENCY} = {rates['SAR']:.4f} SAR")
            st.write(f"1 {BASE_CURRENCY} = {rates['AED']:.4f} AED")
            st.write(f"1 {BASE_CURRENCY} = {rates['USD']:.4f} USD")
        else:
            st.write("Failed to fetch exchange rates.")

        # Display cached locations and timestamps
        st.subheader("Cached Locations")
        cached_locations = get_cached_locations()

        if cached_locations:
            for location, timestamp in cached_locations:
                st.write(f"📍 **{location}**")
                st.write(f"🕒 Cached at: {timestamp}")
                st.divider()
        else:
            st.write("No cached locations available")

        # Cache management buttons
        st.subheader("Cache Controls")
        if st.button("Clear All Cache"):
            clear_all_cache()
            st.success("All cache cleared successfully!")

        # Clear specific location cache
        if cached_locations:
            st.subheader("Clear Specific Location Cache")
            locations = [loc[0] for loc in cached_locations]
            selected_location = st.selectbox("Select location to clear:", locations)
            if st.button(f"Clear {selected_location} Cache"):
                clear_location_cache(selected_location)
                st.success(f"Cache cleared for {selected_location}!")

        # Currency Rates Cache Controls
        st.subheader("Currency Rates Cache Controls")
        if st.button("Clear Currency Rates Cache"):
            clear_currency_rates_cache()
            st.success("Currency rates cache cleared successfully!")

def main():
    st.set_page_config(page_title="Airbnb Scraper", layout="wide")
    st.title("Airbnb Listings Scraper")
    
    # Initialize database and clean up stale cache
    init_db()
    cleanup_stale_cache()
    
    # Create sidebar
    create_sidebar()

    # User Input
    # chrome_driver_path = st.text_input(
    #     "Enter ChromeDriver Path:",
    #     value=r"C:\Users\Chesta\Downloads\chromedriver-win64_130\chromedriver-win64\chromedriver.exe",
    #     help="Enter the path to your ChromeDriver executable."
    # )
    
    search_location = st.text_input(
        "Enter Search Location:",
        value="Riyadh",
        help="Enter a location to scrape Airbnb listings."
    )

    # Scrape Listings
    if st.button("Extract Listings"):
        # if not chrome_driver_path.strip() or not search_location.strip():
        #     st.error("Please provide both ChromeDriver path and search location.")
        #     return

        with st.spinner("Extracting listings..."):
            try:
                # Check if data is already cached in Streamlit
                listings, listings_per_page = scrape_listings(search_location)
                
                # Display Results   
                total_listings = len(listings)
                st.success(f"Scraping complete! Total listings found: {total_listings}")

                tab1, tab2 = st.tabs(["Listings Summary", "Raw Data"])

                with tab1:
                    st.write("### Listings Per Page:")
                    for i, count in enumerate(listings_per_page, start=1):
                        st.write(f"Page {i}: {count} listings")
                    st.write(f"### Total Listings: {total_listings}")

                with tab2:
                    st.write("### Raw Data")
                    df = pd.DataFrame(listings)
                    st.dataframe(df)

                    # CSV Download
                    csv = df.to_csv(index=False)
                    st.download_button(
                        label="Download Listings as CSV",
                        data=csv,
                        file_name=f"airbnb_listings_{search_location}.csv",
                        mime="text/csv"
                    )

            except Exception as e:
                st.error(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()
