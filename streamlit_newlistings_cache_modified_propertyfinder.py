import streamlit as st
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pandas as pd
import re
import math
from typing import Optional,Tuple
from selenium.common.exceptions import NoSuchElementException
import subprocess
from selenium.webdriver.chrome.options import Options
import shutil
import traceback
import urllib.parse
from urllib.parse import urlparse, parse_qsl, urlencode, urlunparse

def generate_cache_key(country: str, transaction_type: str, location: str, property_type: str) -> str:
    """
    Generate a consistent cache key from search parameters.
    All parameters are converted to lowercase and stripped of whitespace.

    Args:
        country: Country name
        transaction_type: Type of transaction (e.g., "Rent", "Buy", "New Projects")
        location: Location string
        property_type: Type of property

    Returns:
        str: Underscore-joined cache key
    """
    params = [
        str(country).lower().strip(),
        str(transaction_type).lower().strip(),
        str(location).lower().strip(),
        str(property_type).lower().strip()
    ]
    return "_".join(params)

def get_cached_results(country: str, transaction_type: str, location: str, property_type: str) -> Tuple[bool, Optional[dict]]:
    """
    Get cached results if they exist and are still valid.

    Args:
        country: Country name
        transaction_type: Type of transaction
        location: Location string
        property_type: Type of property

    Returns:
        Tuple[bool, Optional[dict]]: (cache_exists, cache_data)
    """
    if not all([country, transaction_type, location, property_type]):
        return False, None

    try:
        cache_key = generate_cache_key(country, transaction_type, location, property_type)
        cached_data = st.session_state.get(f'cache_{cache_key}')

        if (cached_data and
            isinstance(cached_data, dict) and
            'listings_data' in cached_data and
            cached_data['listings_data']):

            cache_age = pd.Timestamp.now() - cached_data['timestamp']
            if cache_age.total_seconds() <= 3600 *24:  # 1 hour TTL
                return True, cached_data

        return False, None

    except Exception as e:
        st.error(f"Error retrieving cache: {str(e)}")
        return False, None

def cache_search_results(country: str, transaction_type: str, location: str,
                        property_type: str, listings_data: list, total_pages: int) -> Optional[dict]:
    """
    Store search results in cache with metadata.

    Args:
        country: Country name
        transaction_type: Type of transaction
        location: Location string
        property_type: Type of property
        listings_data: List of property listings
        total_pages: Total number of pages available

    Returns:
        Optional[dict]: Cache entry if successful, None if failed
    """
    if not all([country, transaction_type, location, property_type]):
        return None

    try:
        cache_key = generate_cache_key(country, transaction_type, location, property_type)
        cache_entry = {
            'cache_key': cache_key,
            'listings_data': listings_data,
            'total_pages': total_pages,
            'timestamp': pd.Timestamp.now(),
            'search_params': {
                'country': country,
                'transaction_type': transaction_type,
                'location': location,
                'property_type': property_type
            }
        }
        st.session_state[f'cache_{cache_key}'] = cache_entry
        return cache_entry

    except Exception as e:
        st.error(f"Error caching results: {str(e)}")
        return None


# def setup_webdriver():
#     """Create and return a configured WebDriver instance."""
#     try:
#         # First check installed versions
#         try:
#             # Get Chromium version
#             chrome_version_output = subprocess.check_output(['chromium', '--version']).decode()
#             # st.write(f"Installed Chromium: {chrome_version_output.strip()}")
            
#             # Get ChromeDriver version
#             chromedriver_version_output = subprocess.check_output(['chromedriver', '--version']).decode()
#             # st.write(f"Installed ChromeDriver: {chromedriver_version_output.strip()}")
            
#         except Exception as e:
#             st.warning(f"Version check failed: {str(e)}")
        
#         # Initialize Chrome options
#         chrome_options = Options()
        
#         # Basic required options
#         chrome_options.add_argument("--headless=new")
#         chrome_options.add_argument("--no-sandbox")
#         chrome_options.add_argument("--disable-dev-shm-usage")
#         chrome_options.add_argument("--disable-gpu")
        
#         # Set binary location
#         chrome_options.binary_location = "/usr/bin/chromium"
        
#         # Additional options
#         chrome_options.add_argument("--disable-extensions")
#         chrome_options.add_argument("--disable-web-security")
#         chrome_options.add_argument("--window-size=1920,1080")
#         chrome_options.add_argument("--remote-debugging-port=9222")
        
#         # Generic user agent
#         chrome_options.add_argument("--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/stable Safari/537.36")
        
#         # Initialize service with logging
#         service = Service(
#             executable_path='/usr/bin/chromedriver',
#             log_path='/tmp/chromedriver.log',
#             service_args=['--verbose']
#         )
#         # st.write("Attempting to initialize ChromeDriver...")
        
#         # Try to create driver
#         driver = webdriver.Chrome(service=service, options=chrome_options)
        
#         # Verify browser capabilities
#         # st.write("Driver capabilities:")
#         # st.write(f"Browser version: {driver.capabilities.get('browserVersion', 'unknown')}")
#         # st.write(f"ChromeDriver version: {driver.capabilities.get('chrome', {}).get('chromedriverVersion', 'unknown')}")
        
#         return driver
        
#     except Exception as e:
#         st.error(f"Failed to initialize ChromeDriver: {str(e)}")
        
#         # Try to read ChromeDriver log
#         try:
#             with open('/tmp/chromedriver.log', 'r') as f:
#                 st.code(f.read(), language='text')
#         except:
#             st.warning("Could not read ChromeDriver log")
            
#         st.code(traceback.format_exc())
#         raise


def setup_webdriver():
    """Create and return a configured WebDriver instance."""
    try:
        # First check installed versions
        try:
            # Get Chromium version
            chrome_version_output = subprocess.check_output(['chromium', '--version']).decode()
            # st.write(f"Installed Chromium: {chrome_version_output.strip()}")
            
            # Get ChromeDriver version
            chromedriver_version_output = subprocess.check_output(['chromedriver', '--version']).decode()
            # st.write(f"Installed ChromeDriver: {chromedriver_version_output.strip()}")
            
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
        # st.write("Attempting to initialize ChromeDriver...")
        
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

def country_url(country):
    country_propertyfinder_url = {
        "UAE": "https://www.propertyfinder.ae/",
        "Bahrain": "https://www.propertyfinder.bh/",
        "Qatar": "https://www.propertyfinder.qa/",
        "Egypt": "https://www.propertyfinder.eg/en",
        "Kingdom-of-Saudi Arabia": "https://www.propertyfinder.sa/en"
    }
    return country_propertyfinder_url[country]



def transaction_button_selector_xpath(transaction_type=None,country = None):
    BUTTON_SELECTORS = {
        'rent': {
            'xpath': "//button[@data-testid='segmented-control-Rent']",
            'css': "button[data-testid='segmented-control-Rent']"
        },
        'buy': {
            'xpath': "//button[@data-testid='segmented-control-Buy']",
            'css': "button[data-testid='segmented-control-Buy']"
        },
        # 'new_projects': {
        #     'xpath': "//button[@data-testid='segmented-control-New projects']",
        #     'css': "button[data-testid='segmented-control-New projects']"
        # },
        'commercial': {
            'xpath': "//button[@data-testid='segmented-control-Commercial']",
            'css': "button[data-testid='segmented-control-Commercial']"
        }
    }
    if country == "UAE":
        BUTTON_SELECTORS['new projects'] = {
            'xpath': "//button[@data-testid='segmented-control-New projects']",
            'css': "button[data-testid='segmented-control-New projects']"
        }
    if transaction_type is None:
        return None

    transaction_type = transaction_type.lower()

    if transaction_type not in BUTTON_SELECTORS:
        valid_types = list(BUTTON_SELECTORS.keys())
        raise ValueError(f"Invalid transaction type: '{transaction_type}'. "
                        f"Must be one of: {valid_types}")

    return BUTTON_SELECTORS[transaction_type]


def get_property_types(country, transaction_type):
    """
    Return appropriate property types based on country and transaction type.

    Args:
        country (str): Country code ('UAE', 'SA', 'Egypt', 'QA', 'BH')
        transaction_type (str): Type of transaction ('Buy', 'Rent', 'Commercial', 'New Projects')

    Returns:
        list: List of property types available for the given country and transaction type
    """
    property_types = {
        'UAE': {
            'rent': [
                'Apartment', 'Villa', 'Townhouse', 'Penthouse', 'Compound', 'Duplex',
                'Full Floor', 'Half Floor', 'Whole Building', 'Bulk Rent Unit',
                'Bungalow', 'Hotel & Hotel Apartment'
            ],
            'buy': [
                'Apartment', 'Villa', 'Townhouse', 'Penthouse', 'Compound', 'Duplex',
                'Full Floor', 'Half Floor', 'Whole Building', 'Land', 'Bulk Sale Unit',
                'Bungalow', 'Hotel & Hotel Apartment'
            ],
            'new projects': [
                'Apartment', 'Penthouse', 'Townhouse', 'Duplex', 'Villa'
            ],
            'commercial': [
                'Office Space', 'Retail', 'Warehouse', 'Shop', 'Villa', 'Show Room',
                'Full Floor', 'Half Floor', 'Whole Building', 'Land', 'Bulk Rent Unit',
                'Factory', 'Labor Camp', 'Staff Accommodation', 'Business Center',
                'Co-working space', 'Farm'
            ]
        },
        'Kingdom-of-Saudi Arabia': {
            'buy': [
                'Apartment', 'Farm', 'Villa', 'Rest House', 'Compound', 'Duplex',
                'Whole Building', 'Land', 'Hotel/Hotel Apartment', 'Full Floor'
            ],
            'rent': [
                'Apartment', 'Farm', 'Villa', 'Rest House', 'Compound', 'Duplex',
                'Whole Building', 'Land', 'Hotel/Hotel Apartment', 'Full Floor'
            ],
            'commercial': [
                'Office Space', 'Retail', 'Warehouse', 'Villa', 'Show Room',
                'Whole Building', 'Bulk Units', 'Factory', 'Hotel/Hotel Apartment',
                'Labor Camp', 'Staff Accommodation', 'Shop', 'Land'
            ]
        },
        'Egypt': {
            'buy': [
                'Apartment', 'Villa', 'Townhouse', 'Penthouse', 'Compound', 'Chalet',
                'Twin House', 'Duplex', 'Full Floor', 'Half Floor', 'Whole Building',
                'Land', 'Bulk Sale Unit', 'Bungalow', 'Hotel Apartment', 'iVilla',
                'Cabin', 'Palace', 'Roof'
            ],
            'rent': [
                'Apartment', 'Villa', 'Townhouse', 'Penthouse', 'Compound', 'Chalet',
                'Twin House', 'Duplex', 'Whole Building', 'Bulk Rent Unit',
                'Hotel Apartment', 'iVilla', 'Cabin', 'Palace', 'Roof', 'Half Floor'
            ],
            'commercial': [
                'Office Space', 'Retail', 'Warehouse', 'Shop', 'Villa', 'Show Room',
                'Full Floor', 'Whole Building', 'Land', 'Bulk Rent Unit', 'Factory',
                'Labor Camp', 'Staff Accommodation', 'Business Center',
                'Co-working Space', 'Farm', 'Medical Facility', 'iVilla', 'Clinic',
                'Cafeteria', 'Restaurant', 'Storage', 'Half Floor'
            ]
        },
        'Qatar': {
            'rent': [
                'Apartment', 'Villa', 'Townhouse', 'Penthouse', 'Compound', 'Duplex',
                'Whole Building', 'Bulk Rent Units', 'Hotel Apartments',
                'Staff Accommodation'
            ],
            'buy': [
                'Apartment', 'Villa', 'Townhouse', 'Penthouse', 'Compound', 'Duplex',
                'Full Floor', 'Half Floor', 'Whole Building', 'Land', 'Bulk Sale Units',
                'Bungalow', 'Hotel Apartments'
            ],
            'commercial': [
                'Office Space', 'Retail', 'Warehouse', 'Shop', 'Villa', 'Show Room',
                'Full Floor', 'Whole Building', 'Land', 'Bulk Rent Units',
                'Labor Camp', 'Staff Accommodation'
            ]
        },
        'Bahrain': {
            'buy': [
                'Apartment', 'Villa', 'Townhouse', 'Penthouse', 'Compound', 'Duplex',
                'Full Floor', 'Half Floor', 'Whole Building', 'Land', 'Bulk Sale Unit',
                'Bungalow', 'Hotel Apartment', 'Chalet'
            ],
            'rent': [
                'Apartment', 'Villa', 'Townhouse', 'Penthouse', 'Compound', 'Duplex',
                'Full Floor', 'Half Floor', 'Whole Building', 'Land', 'Bulk Rent Unit',
                'Bungalow', 'Short Term & Hotel Apartment', 'Hotel Apartment',
                'Staff Accommodation', 'Chalet'
            ],
            'commercial': [
                'Office Space', 'Retail', 'Warehouse', 'Shop', 'Villa', 'Show Room',
                'Full Floor', 'Whole Building', 'Land', 'Bulk Rent Unit', 'Labor Camp',
                'Staff Accommodation', 'Medical Facility', 'Labor Camp/ Per Room-Month'
            ]
        }
    }

    # Use the country and transaction_type directly from selectbox
    transaction_type = transaction_type.lower()
    return property_types.get(country, {}).get(transaction_type, [])


def get_total_pages(driver, final_url: str, items_per_page: int = 26):
    """
    Get the total number of available pages based on property count.

    Returns:
        tuple: (total_pages, property_count)
    """
    print("\n=== Starting Page Analysis ===")
    print(f"Analyzing URL: {final_url}")

    try:
        driver.get(final_url)
        wait = WebDriverWait(driver, 10)

        # Get property count
        property_count_element = wait.until(
            EC.presence_of_element_located((
                By.XPATH,
                "//span[@aria-label='Search results count']"
            ))
        )
        count_text = property_count_element.text
        property_count = int(re.sub(r'[^0-9]', '', count_text))
        # print(f"Found {property_count} properties in search results")

        # Calculate total pages
        total_pages = math.ceil(property_count / items_per_page)
        st.write(f"\nTotal pages available: {total_pages}")

        return total_pages, property_count

    except Exception as e:
        print(f"\nError getting total pages: {str(e)}")
        return 0, 0

def get_page_urls(driver, final_url: str, total_pages: int, pages_to_scrape: int):
    """
    Generate URLs for the specified number of pages to scrape.

    Args:
        driver: Selenium WebDriver instance
        final_url: Base URL for scraping
        total_pages: Total number of available pages
        pages_to_scrape: Number of pages user wants to scrape

    Returns:
        list: List of tuples containing (page_number, page_url)
    """
    try:
        wait = WebDriverWait(driver, 20)

        if total_pages == 0:
            # print("No results found.")
            return []

        print(f"Pages to scrape: {pages_to_scrape}")

        # Initialize with first page
        page_urls = [(1, final_url)]
        found_pages = set([1])

        # Get pagination URLs
        print("\nLooking for pagination buttons...")
        pagination_buttons = wait.until(
            EC.presence_of_all_elements_located((
                By.XPATH,
                "//a[@data-testid='pagination-page-button']"
            ))
        )

        print("Processing pagination URLs...")
        for btn in pagination_buttons:
            page_text = btn.text.strip()
            if page_text.isdigit():
                page_num = int(page_text)
                if page_num <= pages_to_scrape and page_num not in found_pages:
                    href = btn.get_attribute("href")
                    if href:
                        page_urls.append((page_num, href))
                        found_pages.add(page_num)
                        # print(f"Found URL for page {page_num}")

        # If we need more pages than what's immediately visible
        if pages_to_scrape > len(page_urls):
            if len(page_urls) > 1:
                base_url = page_urls[1][1]  # Use second URL as template
                url_pattern = base_url.rsplit('=', 1)[0] + '='

                # Add missing page URLs
                for page_num in range(2, pages_to_scrape + 1):
                    if page_num not in found_pages:
                        page_url = f"{url_pattern}{page_num}"
                        page_urls.append((page_num, page_url))
                        print(f"Generated URL for page {page_num}")

        # Sort by page number
        page_urls.sort(key=lambda x: x[0])

        # Trim to requested number of pages
        page_urls = page_urls[:pages_to_scrape]
        print(f"\nTotal pagination URLs found: {len(page_urls)}")

        return page_urls

    except Exception as e:
        print(f"\nError during page processing: {str(e)}")
        return [(1, final_url)]  # Return at least first page on error

def scrape_page_rent(driver, page_number,page_listings,start_serial=1):
    """
    Scrape a single 'rent' results page by targeting <li role='listitem'>
    and pulling data from child elements via data-testid or class.
    """
    #print(f"\n--- Scraping Page (Rent) {page_number} ---")
    wait = WebDriverWait(driver, 8)

    driver.get(page_listings)
    # All list items with role="listitem"

    time.sleep(5)
    li_items = wait.until(
        EC.presence_of_all_elements_located(
            (By.XPATH, "//li[@role='listitem']")
        )
    )
    #print(f"Found {len(li_items)} property cards on rent page {page_number}.")

    properties = []
    current_serial = start_serial
    for li in li_items:
        property_data = {}
        # absolute_position = start_serial + idx + 1
        property_data["S.No."]= current_serial
        # 1) Type
        try:
            property_type_element = li.find_element(By.XPATH, ".//p[@data-testid='property-card-type']")
            property_data["type"] = property_type_element.text
        except NoSuchElementException:
            property_data["type"] = "N/A"

        # 2) Price
        try:
            property_price_elem = li.find_element(By.XPATH, ".//p[@data-testid='property-card-price']")
            property_data["price"] = property_price_elem.text
        except NoSuchElementException:
            property_data["price"] = "N/A"

        # 3) The <h2> text (City View | Furnished | Flexible Terms)
        try:
            property_style_info = li.find_element(By.XPATH, ".//h2[contains(@class, 'styles-module_content__title__')]")
            property_data["info"] = property_style_info.text
        except NoSuchElementException:
            property_data["info"] = "N/A"

        # 4) Bedrooms
        try:
            bedrooms_elem = li.find_element(By.XPATH, ".//p[@data-testid='property-card-spec-bedroom']")
            property_data["bedrooms"] = bedrooms_elem.text
        except NoSuchElementException:
            property_data["bedrooms"] = "N/A"

        # 5) Bathrooms
        try:
            bathrooms_elem = li.find_element(By.XPATH, ".//p[@data-testid='property-card-spec-bathroom']")
            property_data["bathrooms"] = bathrooms_elem.text
        except NoSuchElementException:
            property_data["bathrooms"] = "N/A"

        # 6) Area
        try:
            area_elem = li.find_element(By.XPATH, ".//p[@data-testid='property-card-spec-area']")
            property_data["area"] = area_elem.text
        except NoSuchElementException:
            property_data["area"] = "N/A"

        # 7) Listing time
        try:
            listing_time_elem = li.find_element(
                By.XPATH,
                ".//p[contains(@class, 'styles-module_footer__publish-info')]"
            )
            property_data["listing_time"] = listing_time_elem.text
        except NoSuchElementException:
            property_data["listing_time"] = "N/A"
        try:
            property_data_location = li.find_element(By.XPATH, ".//p[contains(@class, 'styles-module_content__location__')]")
            property_data['location'] = property_data_location.text
        except:
            property_data['location'] = "N/A"


        # 8) URL & Title
        try:
            link_elem = li.find_element(By.XPATH, ".//a[@data-testid='property-card-link']")
            property_data["url"] = link_elem.get_attribute("href")
            property_data["title"] = link_elem.get_attribute("title")
        except NoSuchElementException:
            property_data["url"] = "N/A"
            property_data["title"] = "N/A"
        # 9) Broker Data
        try:
            broker_img = li.find_element(By.XPATH, './/div[@data-testid="property-card-broker-logo"]//img[@data-testid="gallery-picture"]')
            logo_alt = broker_img.get_attribute("alt")
            if "logo image" in logo_alt:
                logo_alt = logo_alt.replace("logo image", "").strip()
            property_data["broker"] = logo_alt
        except NoSuchElementException:
            property_data["broker"] = "N/A"


        properties.append(property_data)
        current_serial += 1
    return properties


def new_projects_listings(driver, page_number,page_listings,start_serial=1):
    wait = WebDriverWait(driver, 10)

    driver.get(page_listings)
    time.sleep(10)

    li_items = wait.until(
    EC.presence_of_all_elements_located(
        (By.XPATH, "//article[@data-testid='project-featured-card']")
    )
    )

    properties = []
    current_serial = start_serial
    for li in li_items:
        # print("\n🔹 Processing Project HTML:\n", li.get_attribute("outerHTML"))
        property_data = {}
        # absolute_position = start_serial + idx + 1
        property_data["S.No."]= current_serial
        try:
            # Get off-plan status
            off_plan = li.find_element(By.XPATH, ".//div[@data-testid='tag-off_plan']").text
            # print(off_plan)
            property_data["off_plan_status"] = off_plan
        except NoSuchElementException:
            property_data["off_plan_status"] = "N/A"

        try:
            # Get delivery date
            delivery_date = li.find_element(By.XPATH, ".//div[@data-testid='tag-delivery_date']").text
            # print(delivery_date)
            property_data["delivery_date"] = delivery_date
        except NoSuchElementException:
            property_data["delivery_date"] = "N/A"

        try:
            # Get developer logo
            developer_logo = li.find_element(By.XPATH, ".//img[@data-testid='project-featured-card-developer-logo']")
            logo_url = developer_logo.get_attribute('src')
            # Create HTML img tag for the logo
            if logo_url:
                property_data["developer_logo"] = f'<img src="{logo_url}" width="40" height="40" alt="developer logo">'
                #f'<img src="{logo_url}" width="40" height="40">'
        except NoSuchElementException:
            property_data["developer_logo"] = "N/A"

        # Get title (h3)
        try:
            title = li.find_element(By.XPATH, ".//h3[@class='styles-module_card__title__fCeSh']").text
            # print(title)
            property_data["title"] = title
        except NoSuchElementException:
            property_data["title"] = "N/A"

        # Get location
        try:
            location = li.find_element(By.XPATH, ".//span[@data-testid='project-featured-card-location']").text
            property_data["location"] = location
        except NoSuchElementException:
            property_data["location"] = "N/A"

        # Get bedrooms
        try:
            bedrooms = li.find_element(By.XPATH, ".//div[@data-testid='project-featured-card-bedrooms']").text
            property_data["bedrooms"] = bedrooms
        except NoSuchElementException:
            property_data["bedrooms"] = "N/A"

        # New fields for price and payment plan
        try:
            price_element = li.find_element(By.XPATH, ".//div[@data-testid='project-featured-card-price']")
            price = price_element.text.replace('\n', ' ').replace(':', ' ')  # Clean up the text
            property_data["launch_price"] = price
        except NoSuchElementException:
            property_data["launch_price"] = "N/A"

        try:
            payment_plan = li.find_element(By.XPATH, ".//div[@data-testid='project-featured-card-payment-plans']").text
            property_data["payment_plan"] = payment_plan
        except NoSuchElementException:
            property_data["payment_plan"] = "N/A"

                # Add construction progress
        try:
            progress_div = li.find_element(By.XPATH,
                ".//div[contains(@class, 'styles-module_progress-bar__label')]")
            progress_span = progress_div.find_element(By.XPATH, ".//span")
            construction_progress = f"Construction progress: {progress_span.text}%"
            property_data["construction_progress"] = construction_progress
        except NoSuchElementException:
            property_data["construction_progress"] = "N/A"

        properties.append(property_data)
        current_serial += 1
    return properties

# @st.cache_data
# def cache_listings(listings):
#     return listings




# Modified extract_listings_test function
def extract_listings_test(driver, pages_list, search_params):
    """
    Enhanced listing extraction with simplified caching
    """
    # Check for cached results first
    has_cache, cache_data = get_cached_results(
        search_params['country'],
        search_params['transaction_type'],
        search_params['location'],
        search_params['property_type']
    )

    if has_cache:
        # Display cache information
        st.info(f"Found cached data from {cache_data['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}")

        # Create DataFrame from cached listings
        df = pd.DataFrame(cache_data['listings_data'])

        # Display the cached data
        # st.dataframe(df, hide_index=True, use_container_width=True)
        display_with_logos(df)

        # Option to refresh data
        if st.button("Refresh Data"):
            st.info("Fetching fresh data...")
            return scrape_fresh_data(driver, pages_list, search_params)

        return cache_data['listings_data']

    # If no cache, scrape fresh data
    return scrape_fresh_data(driver, pages_list, search_params)


def scrape_fresh_data(driver, pages_list, search_params):
    """
    Scrape fresh data and cache it
    """
    all_listings = []
    current_serial = 1

    # Progress indicators
    progress_text = st.empty()
    progress_bar = st.progress(0)
    # dataframe_placeholder = st.empty()

    total_pages = len(pages_list)

    # Scrape data
    for idx, (page_num, page_url) in enumerate(pages_list):
        try:
            progress_text.text(f"Scraping page {page_num} of {total_pages}")

            # Scrape new data
            time.sleep(10)
            if search_params['transaction_type'].lower() == "new projects":
                # print("Using new_projects_listings scraper")
                new_listings = new_projects_listings(driver, page_num, page_url, start_serial=current_serial)
            else:
                # print("Using standard scrape_page_rent scraper")
                new_listings = scrape_page_rent(driver, page_num, page_url, start_serial=current_serial)


            # Update serial numbers and add to results
            for item in new_listings:
                item['S.No.'] = current_serial
                current_serial += 1
            all_listings.extend(new_listings)

            # Update progress
            progress = (idx + 1) / total_pages
            progress_bar.progress(progress)

        #     # Update display
        #     df = pd.DataFrame(all_listings)
        #     # dataframe_placeholder.dataframe(df, hide_index=True, use_container_width=True)
        #     # ✅ Ensure 'developer_logo' column only stores raw image URLs
        #    # ✅ Ensure 'developer_logo' column contains proper HTML image tags
        #     display_with_logos(df)


        except Exception as e:
            st.error(f"Error processing page {page_num}: {str(e)}")
            continue

    # Clear progress indicators
    progress_text.empty()
    progress_bar.empty()

    # Cache the complete results
    cache_search_results(
        search_params['country'],
        search_params['transaction_type'],
        search_params['location'],
        search_params['property_type'],
        all_listings,
        total_pages
    )

    return all_listings

def render_html_table(df):
    """
    Convert DataFrame to an HTML-styled table where images are rendered.
    """
    df_html = df.to_html(escape=False, index=False)
    return df_html


def display_with_logos(df):
    """
    Display DataFrame in Streamlit with properly formatted image logos.
    """
    if 'developer_logo' in df.columns:
        df['developer_logo'] = df['developer_logo'].apply(lambda x: x if x != "N/A" else "N/A")

    # Convert DataFrame to HTML and render in Streamlit
    st.markdown(render_html_table(df), unsafe_allow_html=True)

def get_transaction_types(country):
    """
    Return available transaction types based on country
    """
    base_types = ["Rent", "Buy", "Commercial"]
    if country == "UAE":
        return base_types + ["New Projects"]
    return base_types


# def get_furnished_filter_value(furnished_option):
#     """Return the appropriate furnished filter value based on selection."""
#     furnished_map = {
#         "All furnishings":"0",
#         "Furnished":"1",
#         "Unfurnished":"2",
#         "Partly furnished":"3"
#     }

#     return furnished_map.get(furnished_option,"0")



# def apply_url_filters(base_url, filters):
#     """
#     Apply filters directly to the URL instead of using UI interactions.
    
#     Args:
#         base_url (str): The base search URL obtained after initial search
#         filters (dict): Dictionary of filter parameters to apply
        
#     Returns:
#         str: Modified URL with filter parameters
#     """
#     # Parse the existing URL
#     url_parts = list(urllib.parse.urlparse(base_url))
#     # # Before: ['https', 'www.propertyfinder.ae', '/en/search', '', 'c=1&t=1&l=36', '']

#     # Extract query parameters as dictionary
#     query = dict(urllib.parse.parse_qsl(url_parts[4]))
#     # {'c': '1', 't': '1', 'l': '36'}
    
#     # Add filter parameters
#     query.update(filters)
#      # {'c': '1', 't': '1', 'l': '36', 'fu': '2'}


#     # Convert back to query string
#     url_parts[4] = urllib.parse.urlencode(query)
#     # url_parts[4] = 'c=1&t=1&l=36&fu=2'

#     # Reassemble the URL
#     return urllib.parse.urlunparse(url_parts)
#      # 'https://www.propertyfinder.ae/en/search?c=1&t=1&l=36&fu=2'



def apply_property_filters(base_url, filters):
    """
    Apply property filters to a PropertyFinder URL, handling both regular and array parameters.
    
    Args:
        base_url (str): The base URL from initial search
        filters (dict): Dictionary of filters to apply
        
    Returns:
        str: Modified URL with filters applied
    """
    # Parse the URL
    parsed_url = urlparse(base_url)
    
    # Get existing parameters as dict
    query_params = dict(parse_qsl(parsed_url.query))
    
    # Update/add filter parameters
    for key, value in filters.items():
        if value is not None and value != "":
            query_params[key] = value
    
    # Rebuild the URL
    url_parts = list(parsed_url)
    url_parts[4] = urlencode(query_params)
    
    return urlunparse(url_parts)

# Constants for filter options
FILTER_OPTIONS = {
    # Furnishing options
    "furnishing": {
        "parameter": "fu",
        "options": {
            "All furnishings": "0",
            "Furnished": "1", 
            "Unfurnished": "2",
            "Partly furnished": "3"
        }
    },
    
    # Bedroom options
    "bedrooms": {
        "parameter": "bdr[]",
        "options": {
            "Any": "",
            "Studio": "0",
            "1 Bedroom": "1",
            "2 Bedrooms": "2",
            "3 Bedrooms": "3", 
            "4 Bedrooms": "4",
            "5 Bedrooms": "5",
            "6 Bedrooms": "6",
            "7 Bedrooms": "7",
            "7+ Bedrooms": "8"
        }
    },
    
    # Bathroom options
    "bathrooms": {
        "parameter": "btr[]", 
        "options": {
            "Any": "",
            "1 Bathroom": "1",
            "2 Bathrooms": "2",
            "3 Bathrooms": "3",
            "4 Bathrooms": "4",
            "5 Bathrooms": "5",
            "6 Bathrooms": "6",
            "7 Bathrooms": "7",
            "7+ Bathrooms": "8"
        }
    },
    
    # Sort options
    "sort": {
        "parameter": "ob",
        "options": {
            "Featured": "mr",
            "Newest": "nd",
            "Price (low)": "pa",
            "Price (high)": "pd",
            "Beds (least)": "ba",
            "Beds (most)": "bd"
        }
    }
}



# Add this to your main function after initial search completes
def display_property_filters():
    """
    Display property filter UI in Streamlit and return selected filters.
    
    Returns:
        dict: Selected filter parameters ready for URL application
    """
    st.subheader("Property Filters")
    
    # Create two columns for layout
    col1, col2 = st.columns(2)
    
    selected_filters = {}
    
    # First column: Furnishing & Bedrooms
    with col1:
        # Furnishing status
        furnishing = st.selectbox(
            "Furnishing Status",
            list(FILTER_OPTIONS["furnishing"]["options"].keys()),
            index=0
        )
        
        # Only add if not "Any"
        furnishing_value = FILTER_OPTIONS["furnishing"]["options"][furnishing]
        if furnishing_value:
            selected_filters[FILTER_OPTIONS["furnishing"]["parameter"]] = furnishing_value
        
        # Bedrooms
        bedrooms = st.selectbox(
            "Bedrooms",
            list(FILTER_OPTIONS["bedrooms"]["options"].keys()),
            index=0
        )
        
        # Only add if not "Any"
        bedroom_value = FILTER_OPTIONS["bedrooms"]["options"][bedrooms]
        if bedroom_value:
            selected_filters[FILTER_OPTIONS["bedrooms"]["parameter"]] = bedroom_value
    
    # Second column: Bathrooms & Sort
    with col2:
        # Bathrooms
        bathrooms = st.selectbox(
            "Bathrooms",
            list(FILTER_OPTIONS["bathrooms"]["options"].keys()),
            index=0
        )
        
        # Only add if not "Any"
        bathroom_value = FILTER_OPTIONS["bathrooms"]["options"][bathrooms]
        if bathroom_value:
            selected_filters[FILTER_OPTIONS["bathrooms"]["parameter"]] = bathroom_value
        
        # Sort
        sort_option = st.selectbox(
            "Sort By",
            list(FILTER_OPTIONS["sort"]["options"].keys()),
            index=0
        )
        
        # Add sort parameter
        sort_value = FILTER_OPTIONS["sort"]["options"][sort_option]
        if sort_value:
            selected_filters[FILTER_OPTIONS["sort"]["parameter"]] = sort_value
    
    return selected_filters




     

def main():
    st.title("Property Finder Scraper")
    # Add cache control in sidebar
    with st.sidebar:
        st.header("Cache Settings")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Clear Cache"):
                st.cache_data.clear()
                # Clear session state cache entries
                for key in list(st.session_state.keys()):
                    if key.startswith('cache_'):
                        del st.session_state[key]
                st.success("Cache cleared successfully!")
        with col2:
            if st.button("Cache Status"):
                st.write("Cache Information")
                st.divider()

            # Check for cache entries in session state
            cache_entries = [key for key in st.session_state.keys() if key.startswith('cache_')]

            if not cache_entries:
                st.info("No cached data available")
            else:
                for cache_key in cache_entries:
                    cache_data = st.session_state[cache_key]
                    if isinstance(cache_data, dict) and 'search_params' in cache_data:
                        params = cache_data['search_params']
                        st.write(f"### Cache Entry: {cache_key}")
                        st.write(f"""
                        - **Search Parameters**:
                        - Country: {params['country']}
                        - Transaction Type: {params['transaction_type']}
                        - Location: {params['location']}
                        - Property Type: {params['property_type']}
                        - **Data Details**:
                        - Total Listings: {len(cache_data['listings_data'])}
                        - Total Pages: {cache_data['total_pages']}
                        - Last Updated: {cache_data['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}
                        """)
                        st.divider()
                        
    # SECTION 1: BASIC SEARCH PARAMETERS
    st.subheader("Search Parameters")
    country = st.selectbox("Select Country", ["UAE", "Bahrain", "Qatar", "Egypt", "Kingdom-of-Saudi Arabia"])

    # Get available transaction types based on country
    available_transaction_types = get_transaction_types(country)
    transaction_type = st.selectbox("Select Transaction Type", available_transaction_types)

    location = st.text_input("Enter City, community or building")
    # Get property types directly using user's selections
    property_types = get_property_types(country, transaction_type)

    if not property_types:
        st.warning(f"No property types available for {transaction_type} in {country}")
        return

    property_type = st.selectbox("Select Property Type", property_types)
    
    # SECTION 2: ADVANCED FILTERS (MOVED BEFORE SEARCH BUTTON)
    # Use the existing display_property_filters function
    selected_filters = display_property_filters()
        
    # Store search parameters
    search_params = {
        'country': country,
        'transaction_type': transaction_type,
        'location': location,
        'property_type': property_type
    }

    # Initialize cache status
    has_cache = False
    cache_data = None

    # Check for existing cached data if all search parameters are provided
    if all(search_params.values()):  # Check if all parameters have values
        has_cache, cache_data = get_cached_results(
            search_params['country'],
            search_params['transaction_type'],
            search_params['location'],
            search_params['property_type']
        )
        if has_cache and not st.session_state.get('refresh_data', False):
            st.success(f"""
                Found existing data for this search combination:
                - Last updated: {cache_data['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}
                - Total pages: {cache_data['total_pages']}
                """)

            # Show cached data
            df = pd.DataFrame(cache_data['listings_data'])
            st.dataframe(df, hide_index=True, use_container_width=True)

            # Download option for cached data
            csv = df.to_csv(index=False)
            st.download_button(
                label="Download Cached Data as CSV",
                data=csv,
                file_name=f"property_listings_{country}_{location}.csv",
                mime="text/csv",
            )

            # Option to refresh data
            if st.button("Fetch Fresh Data"):
                st.session_state.refresh_data = True
            else:
                return    # Exit if user doesn't want to refresh
        # Reset refresh_data flag
        if st.session_state.get('refresh_data'):
            del st.session_state['refresh_data']
            
    # Create a session state to store the driver and other values
    if 'driver' not in st.session_state:
        st.session_state.driver = None
    if 'total_pages' not in st.session_state:
        st.session_state.total_pages = 0
    if 'final_url' not in st.session_state:
        st.session_state.final_url = None
    if 'base_url' not in st.session_state:
        st.session_state.base_url = None
    if 'search_url' not in st.session_state:
        st.session_state.search_url = None
        
    # URL Debugging Panel
    if 'base_url' in st.session_state and st.session_state.base_url:
        with st.expander("Debug URLs", expanded=False):
            st.write("**Base URL:** ", st.session_state.base_url)
            if 'search_url' in st.session_state and st.session_state.search_url:
                st.write("**Search URL:** ", st.session_state.search_url)
            if 'final_url' in st.session_state and st.session_state.final_url:
                st.write("**Final URL (with filters):** ", st.session_state.final_url)
        
    # Search button - only show if no cache or refresh requested
    if not has_cache or getattr(st.session_state, 'refresh_data', False):
        # Initial search button
        if st.button("Search Properties"):
            try:
                # Initialize the driver if not already initialized
                if st.session_state.driver is None:
                    st.session_state.driver = setup_webdriver()

                driver = st.session_state.driver

                # Get URL based on country selection
                base_url = country_url(country)
                st.session_state.base_url = base_url
                st.write(f"Base URL: {base_url}")

                # Navigate to the URL
                driver.get(base_url)
                driver.maximize_window()
                st.write("Successfully navigated to the URL")
                # Wait for the page to load
                time.sleep(10)

                # Click the transaction type button
                transaction_selectors = transaction_button_selector_xpath(transaction_type, country=country)
                if transaction_selectors:
                    select_transaction_type = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH, transaction_selectors['xpath']))
                    )
                    driver.execute_script("arguments[0].click();", select_transaction_type)
                    time.sleep(5)

                # Location search
                search_input = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "input[placeholder='City, community or building']"))
                )
                search_input.clear()
                search_input.send_keys(location)
                search_input.click()

                # Wait for dropdown to appear
                dropdown = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "div[data-testid='multi-selection-autocomplete-template-suggestions']"))
                )
                time.sleep(10)

                # Find and click the specific location suggestion
                suggestion = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-testid='multi-selection-autocomplete-template-suggestion-button']"))
                )
                time.sleep(10)
                suggestion.click()
                time.sleep(3)

                # Property type selection
                select_property_type = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[@data-testid='filters-form-dropdown-property-type']"))
                )
                select_property_type.click()
                time.sleep(2)

                if property_type:
                    try:
                        # Wait for dropdown content to be visible
                        dropdown_content = WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.XPATH, "//div[@data-testid='dropdown-content']"))
                        )
                        # Find the specific property type option
                        property_option = dropdown_content.find_element(
                            By.XPATH, f".//button[@class='styles-module_dropdown-content__item__thioe' and text()='{property_type}']"
                        )
                        driver.execute_script("arguments[0].scrollIntoView(true);", property_option)
                        time.sleep(3)  # Wait for scroll to complete

                        # Click using JavaScript
                        driver.execute_script("arguments[0].click();", property_option)
                        time.sleep(3)
                    except Exception as e:
                        st.write(f"Property type selection failed: {e}")

                # Click on the search button
                time.sleep(5)
                wait = WebDriverWait(driver, 8)
                search_button = wait.until(
                    EC.element_to_be_clickable(
                        (By.XPATH, "//button[@data-testid='home-page-filters-search']")
                    )
                )

                # Scroll the button into view
                driver.execute_script("arguments[0].scrollIntoView(true);", search_button)
                time.sleep(5)  # Give some time for the scroll to complete
                search_button.click()

                # Wait for URL change
                time.sleep(3)

                # Store the basic search URL
                st.session_state.search_url = driver.current_url
                st.write(f"Basic search URL: {st.session_state.search_url}")

                # Apply filters directly without requiring a second button click
                if selected_filters:
                    filtered_url = apply_property_filters(st.session_state.search_url, selected_filters)
                    st.write(f"Applying filters automatically to URL...")
                    
                    # Navigate to the filtered URL
                    driver.get(filtered_url)
                    time.sleep(3)  # Wait for page to load with filters
                    
                    # Store the final URL (with filters applied)
                    st.session_state.final_url = filtered_url
                    st.write(f"Final URL with filters: {st.session_state.final_url}")
                else:
                    # If no filters were applied, the search URL is the final URL
                    st.session_state.final_url = st.session_state.search_url
                    st.write("No filters applied. Using search URL as final.")

                # Get total pages available
                total_pages, property_count = get_total_pages(driver, st.session_state.final_url)
                st.session_state.total_pages = total_pages

                if total_pages == 0:
                    st.write("No results found. Please try different search criteria.")
                    if st.session_state.driver:
                        st.session_state.driver.quit()
                        st.session_state.driver = None
                    return

            except Exception as e:
                st.write(f"An error occurred during search: {e}")
                st.code(traceback.format_exc())  # Added for better debugging
                if st.session_state.driver:
                    st.session_state.driver.quit()
                    st.session_state.driver = None
                return

        # Only show number input if we have total pages
        if st.session_state.total_pages > 0:
            number_of_pages_to_scrape = st.number_input(
                "Number of pages to scrape",
                min_value=1,
                max_value=st.session_state.total_pages,
                value=min(1, st.session_state.total_pages)
            )

            if st.button("Start Scraping"):
                try:
                    if st.session_state.driver is None:
                        st.error("Please perform the search first")
                        return

                    # Get the URLs for the pages to scrape
                    page_urls = get_page_urls(
                        st.session_state.driver,
                        st.session_state.final_url,
                        st.session_state.total_pages,
                        number_of_pages_to_scrape
                    )

                    if not page_urls:
                        st.write("No results found. Please try different search criteria.")
                        return

                    # Scrape listings
                    all_listings = extract_listings_test(st.session_state.driver, page_urls, search_params)

                    if not all_listings:
                        st.write("No listings found. Please check your search criteria.")
                        return

                    # Convert to DataFrame and reset the index
                    df = pd.DataFrame(all_listings).reset_index(drop=True)

                    # Create two columns for a "toolbar" effect
                    col1, col2 = st.columns([3, 1])

                    with col1:
                        st.markdown("## Results Table")  # or "###"
                        
                    with col2:
                        # Prepare CSV data
                        csv = df.to_csv(index=False)
                        st.download_button(
                            label="Download data as CSV",
                            data=csv,
                            file_name="property_listings.csv",
                            mime="text/csv",
                        )

                    # Now render the table below your "toolbar"
                    display_with_logos(df)

                except Exception as e:
                    st.write(f"An error occurred during scraping: {e}")
                    st.code(traceback.format_exc())  # Added for better debugging
                finally:
                    # Only quit the driver after scraping is complete
                    if st.session_state.driver:
                        st.session_state.driver.quit()
                        st.session_state.driver = None
                        st.session_state.total_pages = 0
                        st.session_state.final_url = None
                        st.session_state.base_url = None
                        st.session_state.search_url = None

if __name__ == "__main__":
    main()