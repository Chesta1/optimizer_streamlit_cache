
import logging
import urllib.parse
import time
from typing import List, Dict, Tuple
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.options import Options
import pandas as pd
import streamlit as st
from datetime import datetime
import subprocess
import traceback


# Setup logging
def setup_logging():
    """Setup logging configuration."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger(__name__)
    return logger


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
        st.write("Driver capabilities:")
        st.write(f"Browser version: {driver.capabilities.get('browserVersion', 'unknown')}")
        st.write(f"ChromeDriver version: {driver.capabilities.get('chrome', {}).get('chromedriverVersion', 'unknown')}")
        
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

# Get total pages and URLs
def get_total_pages_and_urls(search_location: str, driver) -> Tuple[int, List[str]]:
    try:
        search_url = f"https://www.airbnb.co.in/s/{urllib.parse.quote(search_location)}/homes"
        driver.get(search_url)

        page_urls = [driver.current_url]
        total_pages = 1

        while True:
            try:
                next_link = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, "//a[@aria-label='Next']"))
                )
                next_link.click()
                WebDriverWait(driver, 5).until(
                    EC.url_changes(page_urls[-1])
                )
                page_urls.append(driver.current_url)
                total_pages += 1
            except (TimeoutException, NoSuchElementException):
                break
        return total_pages, page_urls

    except Exception as e:
        logger.error(f"Error getting pages and URLs: {str(e)}")
        return 0, []


# Extract listings from a page
def get_listing_links_for_page(page_url: str, driver) -> List[Dict]:
    try:
        driver.get(page_url)
        time.sleep(5)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        listings_info = []

        listing_elements = soup.find_all('div', {'itemprop': 'itemListElement'})
        for element in listing_elements:
            try:
                url_meta = element.find('meta', {'itemprop': 'url'})
                price_span = element.find('span', class_="_11jcbg2")
                title_element = element.find('meta', {'itemprop': 'name'})
                rating_span = element.find('span', text=lambda t: t and 'average rating' in t)

                if url_meta and url_meta.get('content'):
                    listing_info = {
                        'url': url_meta['content'].split('?')[0],
                        'price': price_span.text.strip() if price_span else "Price not available",
                        'title': title_element['content'] if title_element else "Title not available",
                        'rating': rating_span.text.strip() if rating_span else "Rating not available"
                    }
                    listings_info.append(listing_info)
            except Exception as e:
                logger.warning(f"Error processing listing: {str(e)}")
                continue
        return listings_info

    except Exception as e:
        logger.error(f"Error getting listing links: {str(e)}")
        return []

@st.cache_data(ttl=86400)
def get_cached_pages_and_urls(search_location: str, _driver) -> Tuple[int, List[str]]:
    """Cache total pages and URLs for a location."""
    # Store cache timestamp in session state
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if 'cache_info' not in st.session_state:
        st.session_state.cache_info = {}
    st.session_state.cache_info[f"pages_{search_location}"] = timestamp
    return get_total_pages_and_urls(search_location, _driver)




@st.cache_data(ttl=86400)
def get_cached_listing_links(page_url: str, _driver) -> List[Dict]:
    """Cache listing links for a specific page."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if 'cache_info' not in st.session_state:
        st.session_state.cache_info = {}
    st.session_state.cache_info[f"listings_{page_url}"] = timestamp
    return get_listing_links_for_page(page_url, _driver)


@st.cache_data(ttl=86400)
def scrape_all_listings( search_location: str) -> Tuple[List[Dict], List[int]]:
    """Cache the entire scraping workflow."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if 'cache_info' not in st.session_state:
        st.session_state.cache_info = {}
    st.session_state.cache_info[f"full_scrape_{search_location}"] = timestamp
    
    driver = get_driver() 
    total_pages, page_urls = get_cached_pages_and_urls(search_location, driver)
    
    all_listings = []
    listings_per_page = []
    for page_url in page_urls:
        page_listings = get_cached_listing_links(page_url, driver)
        listings_per_page.append(len(page_listings))
        all_listings.extend(page_listings)

    driver.quit()
    return all_listings, listings_per_page



def create_sidebar():
    """Create and manage the sidebar with cache information."""
    with st.sidebar:
        st.title("Cache Management")
        
        # Display cached locations and timestamps
        st.subheader("Cached Data")
        if 'cache_info' in st.session_state:
            for key, timestamp in st.session_state.cache_info.items():
                if key.startswith("full_scrape_"):
                    location = key.replace("full_scrape_", "")
                    st.write(f"📍 {location}")
                    st.write(f"🕒 Cached at: {timestamp}")
                    st.divider()
        else:
            st.write("No cached data available")
        
        # Cache management buttons
        st.subheader("Cache Controls")
        if st.button("Clear All Cache"):
            # Clear all st.cache_data caches
            st.cache_data.clear()
            # Clear session state cache info
            if 'cache_info' in st.session_state:
                st.session_state.cache_info = {}
            st.success("Cache cleared successfully!")
            
        # Individual location cache clearing
        if 'cache_info' in st.session_state and any(k.startswith("full_scrape_") for k in st.session_state.cache_info.keys()):
            st.subheader("Clear Specific Location Cache")
            locations = [k.replace("full_scrape_", "") for k in st.session_state.cache_info.keys() if k.startswith("full_scrape_")]
            selected_location = st.selectbox("Select location to clear:", locations)
            
            if st.button(f"Clear {selected_location} Cache"):
                # Clear specific location cache
                keys_to_remove = [k for k in st.session_state.cache_info.keys() if selected_location in k]
                for key in keys_to_remove:
                    st.session_state.cache_info.pop(key, None)
                # Also clear the cache_data for this location
                st.cache_data.clear()
                st.success(f"Cache cleared for {selected_location}!")

# Streamlit application
def main():
    st.set_page_config(page_title="Airbnb Scraper", layout="wide")
    st.title("Airbnb Listings Scraper")

    create_sidebar()

    # User Input

    search_location = st.text_input(
        "Enter Search Location:",
        value="Riyadh",
        help="Enter a location to scrape Airbnb listings."
    )

    # Scrape Listings
    if st.button("Extract Listings"):
        if search_location.strip():
            with st.spinner("Extracting listings..."):
                try:
                    # Scrape all listings (cached)
                    all_listings, listings_per_page = scrape_all_listings(search_location)

                    # Display Results
                    total_listings = len(all_listings)
                    st.success(f"Scraping complete! Total listings found: {total_listings}")

                    # Tabs for results
                    tab1, tab2= st.tabs(["Listings Summary", "Raw Data"])

                    with tab1:
                        st.write("### Listings Per Page:")
                        for i, count in enumerate(listings_per_page, start=1):
                            st.write(f"Page {i}: {count} listings")
                        st.write(f"### Total Listings: {total_listings}")

                    with tab2:
                        st.write("### Raw Data")
                        df = pd.DataFrame(all_listings)
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