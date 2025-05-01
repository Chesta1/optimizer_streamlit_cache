import streamlit as st
import requests
import subprocess
import traceback
import math
import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
import time
import pandas as pd


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

# ---------------- GET TOTAL PAGES ----------------
def get_total_pages(driver, final_url: str, items_per_page: int = 28):
    if not final_url.startswith(("http://", "https://")):
        final_url = "https://" + final_url.lstrip("/")
    try:
        driver.get(final_url)
        wait = WebDriverWait(driver, 10)
        property_count_element = wait.until(EC.presence_of_element_located((By.XPATH, "//span[@aria-label='Search results count']")))
        count_text = property_count_element.text
        property_count = int(re.sub(r'[^0-9]', '', count_text))
        total_pages = math.ceil(property_count / items_per_page)
        return total_pages, property_count
    except Exception as e:
        st.error(f"❌ Error getting total pages: {e}")
        return 0, 0

# ---------------- GET PAGINATION URLs ----------------
def get_page_urls(driver, final_url: str, total_pages: int, pages_to_scrape: int):
    try:
        wait = WebDriverWait(driver, 10)
        if total_pages == 0:
            return []
        page_urls = [(1, final_url)]
        found_pages = set([1])
        pagination_buttons = wait.until(EC.presence_of_all_elements_located((By.XPATH, "//a[@data-testid='pagination-page-button']")))
        for btn in pagination_buttons:
            page_text = btn.text.strip()
            if page_text.isdigit():
                page_num = int(page_text)
                if page_num <= pages_to_scrape and page_num not in found_pages:
                    href = btn.get_attribute("href")
                    if href:
                        page_urls.append((page_num, href))
                        found_pages.add(page_num)
        if pages_to_scrape > len(page_urls) and len(page_urls) > 1:
            base_url = page_urls[1][1]
            url_pattern = base_url.rsplit('=', 1)[0] + '='
            for page_num in range(2, pages_to_scrape + 1):
                if page_num not in found_pages:
                    page_url = f"{url_pattern}{page_num}"
                    page_urls.append((page_num, page_url))
        page_urls.sort(key=lambda x: x[0])
        return page_urls[:pages_to_scrape]
    except Exception as e:
        st.warning(f"⚠️ Error getting page URLs: {e}")
        return [(1, final_url)]
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


def extract_listings(driver, pages_list, search_params):
    """
    Scrape listings across all pages (no caching).
    """
    all_listings   = []
    current_serial = 1
    total_pages    = len(pages_list)

    progress_text = st.empty()
    progress_bar  = st.progress(0)

    for idx, (page_num, page_url) in enumerate(pages_list):
        progress_text.text(f"Scraping page {page_num} of {total_pages}…")
        time.sleep(5)  # give the page a moment to load

        # choose the correct scraper
        if search_params["transaction_type"].lower() == "new projects":
            new_list = new_projects_listings(
                driver,
                page_num,
                page_url,
                start_serial=current_serial
            )
        else:
            new_list = scrape_page_rent(
                driver,
                page_num,
                page_url,
                start_serial=current_serial
            )

        # assign serial numbers & accumulate
        for item in new_list:
            item["S.No."] = current_serial
            current_serial += 1
        all_listings.extend(new_list)

        # update progress bar
        progress_bar.progress((idx + 1) / total_pages)

    # clean up UI
    progress_text.empty()
    progress_bar.empty()

    return all_listings


# ---------------- GET COUNTRY BASE URL ----------------
def country_url(country):
    return {
        "UAE": "https://www.propertyfinder.ae",
        "Bahrain": "https://www.propertyfinder.bh",
        "Qatar": "https://www.propertyfinder.qa",
        "Egypt": "https://www.propertyfinder.eg",
        "Kingdom-of-Saudi Arabia": "https://www.propertyfinder.sa"
    }[country]


# Modify your get_location_id function to reduce UI output
def get_location_id(query, base_url):
    headers = {
        "Accept": "*/*",
        "Accept-Language": "en-US,en;q=0.9",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36",
        "Referer": base_url,
        "Origin": base_url,
        "Pragma": "no-cache",
        "Cache-Control": "no-cache",
    }
    
    params = {
        "locale": "en",
        "filters.name": query,
        "pagination.limit": 20
    }
    
    try:
        # First try the API endpoint without /en
        api_url = f"{base_url}/api/pwa/locations"
        
        session = requests.Session()
        session.get(base_url)  # This initializes cookies/session
        
        resp = session.get(api_url, headers=headers, params=params)
        
        # If first attempt fails, try with different URL structure
        if resp.status_code != 200:
            st.info(f"Trying alternative API endpoint format...")
            
            # Try removing /en if it exists in the URL
            if "/en" in base_url:
                alt_base_url = base_url.replace("/en", "")
                api_url = f"{alt_base_url}/api/pwa/locations"
            else:
                # Try adding /en if it doesn't exist
                alt_base_url = f"{base_url}/en"
                api_url = f"{alt_base_url}/api/pwa/locations"
            
            resp = session.get(api_url, headers=headers, params=params)
        
        resp.raise_for_status()
        locations = resp.json()["data"]["attributes"]
        return locations
        
    except Exception as e:
        st.error(f"❌ Failed to fetch location ID: {str(e)}")
        st.error(traceback.format_exc())
        return []


# ---------------- FILTER OPTIONS ----------------
CATEGORY_OPTIONS = [
    {"label": "Rent", "value": "2"},
    {"label": "Buy", "value": "1"},
    {"label": "Commercial", "value": "4"},
    # {"label": "Commercial buy", "value": "3"},
    {"label": "New Projects", "value": "5"},
]
COMPLETION_STATUS_OPTIONS = [
    {"label": "Any", "value": ""},
    {"label": "Off-plan", "value": "off_plan"},
    {"label": "Ready", "value": "completed"},
]
FURNISHING_OPTIONS = [
    {"label": "All furnishings", "value": "0"},
    {"label": "Furnished", "value": "1"},
    {"label": "Unfurnished", "value": "2"},
    {"label": "Partly furnished", "value": "3"},
]
LISTED_WITHIN_OPTIONS = [
    {"label": "Any", "value": ""},
    {"label": "Less than 1 day", "value": "86400"},
    {"label": "Less than 7 days", "value": "604800"},
    {"label": "Less than 15 days", "value": "1296000"},
    {"label": "Less than 30 days", "value": "2592000"},
    {"label": "Less than 90 days", "value": "7776000"},
]

PROPERTY_TYPES = {
    'UAE': {
        'Rent': [
            {'value': '',  'label': '',                          'slug': []},
            {'value': '1', 'label': 'Apartment',                 'slug': ['apartment']},
            {'value': '35','label': 'Villa',                     'slug': ['villa']},
            {'value': '22','label': 'Townhouse',                 'slug': ['townhouse']},
            {'value': '20','label': 'Penthouse',                 'slug': ['penthouse']},
            {'value': '42','label': 'Compound',                  'slug': ['compound']},
            {'value': '24','label': 'Duplex',                    'slug': ['duplex']},
            {'value': '18','label': 'Full Floor',                'slug': ['full-floor']},
            {'value': '29','label': 'Half Floor',                'slug': ['half-floor']},
            {'value': '10','label': 'Whole Building',            'slug': ['whole-building']},
            {'value': '34','label': 'Bulk Rent Unit',            'slug': ['bulk-rent-unit']},
            {'value': '31','label': 'Bungalow',                  'slug': ['bungalow']},
            {'value': '45','label': 'Hotel & Hotel Apartment',   'slug': ['hotel-hotel-apartment']},
        ],
        'Buy': [
            {'value': '',  'label': '',                          'slug': []},
            {'value': '1', 'label': 'Apartment',                 'slug': ['apartment']},
            {'value': '35','label': 'Villa',                     'slug': ['villa']},
            {'value': '22','label': 'Townhouse',                 'slug': ['townhouse']},
            {'value': '20','label': 'Penthouse',                 'slug': ['penthouse']},
            {'value': '42','label': 'Compound',                  'slug': ['compound']},
            {'value': '24','label': 'Duplex',                    'slug': ['duplex']},
            {'value': '18','label': 'Full Floor',                'slug': ['full-floor']},
            {'value': '29','label': 'Half Floor',                'slug': ['half-floor']},
            {'value': '10','label': 'Whole Building',            'slug': ['whole-building']},
            {'value': '5', 'label': 'Land',                      'slug': ['land']},
            {'value': '30','label': 'Bulk Sale Unit',            'slug': ['bulk-sale-unit']},
            {'value': '31','label': 'Bungalow',                  'slug': ['bungalow']},
            {'value': '45','label': 'Hotel & Hotel Apartment',   'slug': ['hotel-hotel-apartment']},
        ],
        'New Projects': [
            {'value': '',  'label': '',                          'slug': []},
            {'value': '1', 'label': 'Apartment',                 'slug': ['apartment']},
            {'value': '20','label': 'Penthouse',                 'slug': ['penthouse']},
            {'value': '22','label': 'Townhouse',                 'slug': ['townhouse']},
            {'value': '24','label': 'Duplex',                    'slug': ['duplex']},
            {'value': '35','label': 'Villa',                     'slug': ['villa']},
        ],
        'Commercial': [
            {'value': '',  'label': '',                          'slug': []},
            {'value': '4', 'label': 'Office Space',              'slug': ['office-space']},
            {'value': '27','label': 'Retail',                    'slug': ['retail']},
            {'value': '13','label': 'Warehouse',                 'slug': ['warehouse']},
            {'value': '21','label': 'Shop',                      'slug': ['shop']},
            {'value': '35','label': 'Villa',                     'slug': ['villa']},
            {'value': '12','label': 'Show Room',                 'slug': ['show-room']},
            {'value': '18','label': 'Full Floor',                'slug': ['full-floor']},
            {'value': '29','label': 'Half Floor',                'slug': ['half-floor']},
            {'value': '10','label': 'Whole Building',            'slug': ['whole-building']},
            {'value': '5', 'label': 'Land',                      'slug': ['land']},
            {'value': '34','label': 'Bulk Rent Unit',            'slug': ['bulk-rent-unit']},
            {'value': '44','label': 'Factory',                   'slug': ['factory']},
            {'value': '11','label': 'Labor Camp',                'slug': ['labor-camp']},
            {'value': '43','label': 'Staff Accommodation',       'slug': ['staff-accommodation']},
            {'value': '48','label': 'Business Centre',           'slug': ['business-centre']},
            {'value': '49','label': 'Co-working space',          'slug': ['co-working-space']},
            {'value': '50','label': 'Farm',                      'slug': ['farm']},
        ],
    },
    'Bahrain': {
        'Rent': [
            {'value': '',  'label': '',                      'slug': []},
            {'value': '1', 'label': 'Apartment',             'slug': ['apartment']},
            {'value': '39','label': 'Short Term & Hotel Apartment','slug':['short-term-hotel-apartment']},
            {'value': '35','label': 'Villa',                 'slug': ['villa']},
            {'value': '22','label': 'Townhouse',             'slug': ['townhouse']},
            {'value': '28','label': 'Hotel Apartment',       'slug': ['hotel-apartment']},
            {'value': '20','label': 'Penthouse',             'slug': ['penthouse']},
            {'value': '42','label': 'Compound',              'slug': ['compound']},
            {'value': '24','label': 'Duplex',                'slug': ['duplex']},
            {'value': '10','label': 'Whole Building',        'slug': ['whole-building']},
            {'value': '34','label': 'Bulk Rent Unit',        'slug': ['bulk-rent-unit']},
            {'value': '31','label': 'Bungalow',              'slug': ['bungalow']},
            {'value': '43','label': 'Staff Accommodation',   'slug': ['staff-accommodation']},
            {'value': '44','label': 'Chalet',                'slug': ['chalet']},
        ],
        'Buy': [
            {'value': '',  'label': '',                      'slug': []},
            {'value': '1', 'label': 'Apartment',             'slug': ['apartment']},
            {'value': '35','label': 'Villa',                 'slug': ['villa']},
            {'value': '22','label': 'Townhouse',             'slug': ['townhouse']},
            {'value': '20','label': 'Penthouse',             'slug': ['penthouse']},
            {'value': '28','label': 'Hotel Apartment',       'slug': ['hotel-apartment']},
            {'value': '42','label': 'Compound',              'slug': ['compound']},
            {'value': '24','label': 'Duplex',                'slug': ['duplex']},
            {'value': '18','label': 'Full Floor',            'slug': ['full-floor']},
            {'value': '29','label': 'Half Floor',            'slug': ['half-floor']},
            {'value': '10','label': 'Whole Building',        'slug': ['whole-building']},
            {'value': '5', 'label': 'Land',                  'slug': ['land']},
            {'value': '30','label': 'Bulk Sale Unit',        'slug': ['bulk-sale-unit']},
            {'value': '31','label': 'Bungalow',              'slug': ['bungalow']},
            {'value': '44','label': 'Chalet',                'slug': ['chalet']},
        ],
        'Commercial': [
            {'value': '',  'label': '',                      'slug': []},
            {'value': '4', 'label': 'Office Space',          'slug': ['office-space']},
            {'value': '27','label': 'Retail',                'slug': ['retail']},
            {'value': '13','label': 'Warehouse',             'slug': ['warehouse']},
            {'value': '21','label': 'Shop',                  'slug': ['shop']},
            {'value': '35','label': 'Villa',                 'slug': ['villa']},
            {'value': '12','label': 'Show Room',             'slug': ['show-room']},
            {'value': '18','label': 'Full Floor',            'slug': ['full-floor']},
            {'value': '10','label': 'Whole Building',        'slug': ['whole-building']},
            {'value': '5', 'label': 'Land',                  'slug': ['land']},
            {'value': '34','label': 'Bulk Sale Unit',        'slug': ['bulk-sale-unit']},
        ],
    },
    'Qatar': {
        'Rent': [
            {'value': '',  'label': '',                   'slug': []},
            {'value': '1', 'label': 'Apartment',          'slug': ['apartment']},
            {'value': '35','label': 'Villa',              'slug': ['villa']},
            {'value': '22','label': 'Townhouse',          'slug': ['townhouse']},
            {'value': '20','label': 'Penthouse',          'slug': ['penthouse']},
            {'value': '42','label': 'Compound',           'slug': ['compound']},
            {'value': '24','label': 'Duplex',             'slug': ['duplex']},
            {'value': '10','label': 'Whole Building',     'slug': ['whole-building']},
            {'value': '34','label': 'Bulk Rent Units',    'slug': ['bulk-rent-units']},
            {'value': '28','label': 'Hotel Apartments',   'slug': ['hotel-apartments']},
            {'value': '43','label': 'Staff Accommodation','slug': ['staff-accommodation']},
        ],
        'Buy': [
            {'value': '',  'label': '',                   'slug': []},
            {'value': '1', 'label': 'Apartment',          'slug': ['apartment']},
            {'value': '35','label': 'Villa',              'slug': ['villa']},
            {'value': '22','label': 'Townhouse',          'slug': ['townhouse']},
            {'value': '20','label': 'Penthouse',          'slug': ['penthouse']},
            {'value': '42','label': 'Compound',           'slug': ['compound']},
            {'value': '24','label': 'Duplex',             'slug': ['duplex']},
            {'value': '18','label': 'Full Floor',         'slug': ['full-floor']},
            {'value': '29','label': 'Half Floor',         'slug': ['half-floor']},
            {'value': '10','label': 'Whole Building',     'slug': ['whole-building']},
            {'value': '5', 'label': 'Land',               'slug': ['land']},
            {'value': '30','label': 'Bulk Sale Units',    'slug': ['bulk-sale-units']},
            {'value': '31','label': 'Bungalow',           'slug': ['bungalow']},
            {'value': '28','label': 'Hotel Apartments',   'slug': ['hotel-apartments']},
        ],
        'Commercial': [
            {'value': '',  'label': '',                   'slug': []},
            {'value': '4', 'label': 'Office Space',       'slug': ['office-space']},
            {'value': '27','label': 'Retail',             'slug': ['retail']},
            {'value': '13','label': 'Warehouse',          'slug': ['warehouse']},
            {'value': '21','label': 'Shop',               'slug': ['shop']},
            {'value': '35','label': 'Villa',              'slug': ['villa']},
            {'value': '12','label': 'Show Room',          'slug': ['show-room']},
            {'value': '18','label': 'Full Floor',         'slug': ['full-floor']},
            {'value': '10','label': 'Whole Building',     'slug': ['whole-building']},
            {'value': '5', 'label': 'Land',               'slug': ['land']},
            {'value': '34','label': 'Bulk Rent Units',    'slug': ['bulk-rent-units']},
            {'value': '11','label': 'Labor Camp',         'slug': ['labor-camp']},
            {'value': '43','label': 'Staff Accommodation','slug': ['staff-accommodation']},
        ],
    },
    'Egypt': {
        'Buy': [
            {'value': '',  'label': '',               'slug': []},
            {'value': '1', 'label': 'Apartment',      'slug': ['apartment']},
            {'value': '35','label': 'Villa',          'slug': ['villa']},
            {'value': '22','label': 'Townhouse',      'slug': ['townhouse']},
            {'value': '20','label': 'Penthouse',      'slug': ['penthouse']},
            {'value': '42','label': 'Compound',       'slug': ['compound']},
            {'value': '44','label': 'Chalet',         'slug': ['chalet']},
            {'value': '46','label': 'Twin House',     'slug': ['twin-house']},
            {'value': '24','label': 'Duplex',         'slug': ['duplex']},
            {'value': '18','label': 'Full Floor',     'slug': ['full-floor']},
            {'value': '29','label': 'Half Floor',     'slug': ['half-floor']},
            {'value': '10','label': 'Whole Building', 'slug': ['whole-building']},
            {'value': '5', 'label': 'Land',           'slug': ['land']},
            {'value': '30','label': 'Bulk Sale Unit', 'slug': ['bulk-sale-unit']},
            {'value': '31','label': 'Bungalow',       'slug': ['bungalow']},
            {'value': '28','label': 'Hotel Apartment','slug': ['hotel-apartment']},
            {'value': '50','label': 'iVilla',         'slug': ['ivilla']},
            {'value': '51','label': 'Cabin',          'slug': ['cabin']},
            {'value': '52','label': 'Palace',         'slug': ['palace']},
            {'value': '53','label': 'Roof',           'slug': ['roof']},
        ],
        'Rent': [
            {'value': '',  'label': '',               'slug': []},
            {'value': '1', 'label': 'Apartment',      'slug': ['apartment']},
            {'value': '35','label': 'Villa',          'slug': ['villa']},
            {'value': '22','label': 'Townhouse',      'slug': ['townhouse']},
            {'value': '20','label': 'Penthouse',      'slug': ['penthouse']},
            {'value': '42','label': 'Compound',       'slug': ['compound']},
            {'value': '44','label': 'Chalet',         'slug': ['chalet']},
            {'value': '46','label': 'Twin House',     'slug': ['twin-house']},
            {'value': '24','label': 'Duplex',         'slug': ['duplex']},
            {'value': '10','label': 'Whole Building', 'slug': ['whole-building']},
            {'value': '34','label': 'Bulk Rent Unit', 'slug': ['bulk-rent-unit']},
            {'value': '31','label': 'Bungalow',       'slug': ['bungalow']},
            {'value': '28','label': 'Hotel Apartment','slug': ['hotel-apartment']},
            {'value': '50','label': 'iVilla',         'slug': ['ivilla']},
            {'value': '51','label': 'Cabin',          'slug': ['cabin']},
            {'value': '52','label': 'Palace',         'slug': ['palace']},
            {'value': '53','label': 'Roof',           'slug': ['roof']},
            {'value': '29','label': 'Half Floor',     'slug': ['half-floor']},
        ],
        'Commercial': [
            {'value': '',  'label': '',                  'slug': []},
            {'value': '4', 'label': 'Office Space',      'slug': ['office-space']},
            {'value': '27','label': 'Retail',            'slug': ['retail']},
            {'value': '13','label': 'Warehouse',         'slug': ['warehouse']},
            {'value': '21','label': 'Shop',              'slug': ['shop']},
            {'value': '35','label': 'Villa',             'slug': ['villa']},
            {'value': '12','label': 'Show Room',         'slug': ['show-room']},
            {'value': '18','label': 'Full Floor',        'slug': ['full-floor']},
            {'value': '10','label': 'Whole Building',    'slug': ['whole-building']},
            {'value': '5', 'label': 'Land',              'slug': ['land']},
            {'value': '34','label': 'Bulk Rent Unit',    'slug': ['bulk-rent-unit']},
            {'value': '11','label': 'Labor Camp',        'slug': ['labor-camp']},
            {'value': '43','label': 'Staff Accommodation','slug': ['staff-accommodation']},
            {'value': '47','label': 'Medical Facility',  'slug': ['medical-facility']},
            {'value': '50','label': 'iVilla',            'slug': ['ivilla']},
            {'value': '45','label': 'Factory',           'slug': ['factory']},
            {'value': '54','label': 'Clinic',            'slug': ['clinic']},
            {'value': '55','label': 'Cafeteria',         'slug': ['cafeteria']},
            {'value': '56','label': 'Co-Working Space',  'slug': ['co-working-space']},
            {'value': '57','label': 'Farm',              'slug': ['farm']},
            {'value': '48','label': 'Restaurant',        'slug': ['restaurant']},
            {'value': '49','label': 'Storage',           'slug': ['storage']},
            {'value': '29','label': 'Half Floor',        'slug': ['half-floor']},
        ],
    },
    'Kingdom-of-Saudi Arabia': {
        'Buy': [
            {'value': '',  'label': '',                      'slug': []},
            {'value': '1', 'label': 'Apartment',             'slug': ['apartment']},
            {'value': '35','label': 'Villa',                 'slug': ['villa']},
            {'value': '22','label': 'Farm',                  'slug': ['farm']},
            {'value': '20','label': 'Rest House',            'slug': ['rest-house']},
            {'value': '42','label': 'Compound',              'slug': ['compound']},
            {'value': '24','label': 'Duplex',                'slug': ['duplex']},
            {'value': '10','label': 'Whole Building',        'slug': ['whole-building']},
            {'value': '5', 'label': 'Land',                  'slug': ['land']},
            {'value': '45','label': 'Hotel/Hotel Apartment', 'slug': ['hotel/hotel-apartment']},
            {'value': '51','label': 'Full Floor',            'slug': ['full-floor']},
        ],
        'Rent': [
            {'value': '',  'label': '',                      'slug': []},
            {'value': '1', 'label': 'Apartment',             'slug': ['apartment']},
            {'value': '35','label': 'Villa',                 'slug': ['villa']},
            {'value': '22','label': 'Farm',                  'slug': ['farm']},
            {'value': '20','label': 'Rest House',            'slug': ['rest-house']},
            {'value': '42','label': 'Compound',              'slug': ['compound']},
            {'value': '24','label': 'Duplex',                'slug': ['duplex']},
            {'value': '10','label': 'Whole Building',        'slug': ['whole-building']},
            {'value': '45','label': 'Hotel/Hotel Apartment', 'slug': ['hotel/hotel-apartment']},
            {'value': '5', 'label': 'Land',                  'slug': ['land']},
            {'value': '51','label': 'Full Floor',            'slug': ['full-floor']},
        ],
        'Commercial': [
            {'value': '',  'label': '',                      'slug': []},
            {'value': '4', 'label': 'Office Space',          'slug': ['office-space']},
            {'value': '27','label': 'Retail',                'slug': ['retail']},
            {'value': '13','label': 'Warehouse',             'slug': ['warehouse']},
            {'value': '35','label': 'Villa',                 'slug': ['villa']},
            {'value': '12','label': 'Show Room',             'slug': ['show-room']},
            {'value': '10','label': 'Whole Building',        'slug': ['whole-building']},
            {'value': '34','label': 'Bulk Units',            'slug': ['bulk-units']},
            {'value': '44','label': 'Factory',               'slug': ['factory']},
            {'value': '45','label': 'Hotel/Hotel Apartment', 'slug': ['hotel/hotel-apartment']},
            {'value': '11','label': 'Labor Camp',            'slug': ['labor-camp']},
            {'value': '43','label': 'Staff Accommodation',   'slug': ['staff-accommodation']},
            {'value': '21','label': 'Shop',                  'slug': ['shop']},
            {'value': '5', 'label': 'Land',                  'slug': ['land']},
        ],
    },
}


# Constants for filter options
FILTER_OPTIONS = {
    
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
        },
        "multiple": True  # Flag to indicate multiple selection
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




COUNTRY_OPTIONS = ["UAE", "Bahrain", "Qatar", "Egypt", "Kingdom-of-Saudi Arabia"]


st.set_page_config(page_title="Property Finder Search Tool", layout="centered")
st.title("📍 Property Finder Listing Scraper")

with st.form("property_finder_form"):
    country = st.selectbox("Select country:", COUNTRY_OPTIONS, key="country")
    base_url = country_url(country)

    location_query = st.text_input("Enter location (e.g., Palm Jumeirah)", key="location_query")

    category = st.selectbox(
        "Category",
        CATEGORY_OPTIONS,
        format_func=lambda x: x["label"],
        key="category"
    )

    prop_list = PROPERTY_TYPES[country][category["label"]]
    prop = st.selectbox(
        "Property Type",
        prop_list,
        format_func=lambda x: x["label"],
        key="prop"
    )

    furnishing = st.selectbox(
        "Furnishing",
        FURNISHING_OPTIONS,
        format_func=lambda x: x['label'],
        key="furnishing"
    )

    completion = st.selectbox(
        "Completion Status",
        COMPLETION_STATUS_OPTIONS,
        format_func=lambda x: x['label'],
        key="completion"
    )

    listed_within = st.selectbox(
        "Listed Within",
        LISTED_WITHIN_OPTIONS,
        format_func=lambda x: x["label"],
        key="listed_within"
    )

    sort_by = st.selectbox(
        "Sort By",
        options=list(FILTER_OPTIONS["sort"]["options"].keys()),
        key="sort"
    )

    submitted = st.form_submit_button("🔍 Submit Search")

# Add these session state keys near the top of your script where you initialize other state variables
# Initialize session state variables at the top of your script
# Add these session state keys near the top of your script where you initialize other state variables
# Initialize session state variables at the top of your script
if submitted and st.session_state["location_query"]:
    st.session_state["location_query_submitted"] = True
    st.session_state["last_query"] = st.session_state["location_query"]

    if (
        not st.session_state.get("locations_found") or
        st.session_state["last_query"] != st.session_state["location_query"]
    ):
        locs = get_location_id(st.session_state["location_query"], base_url)
        st.session_state["locations_found"] = locs
        st.session_state["confirmed_location"] = False
    else:
        locs = st.session_state["locations_found"]

    if locs:
        exact = [l for l in locs if l['name'].lower() == st.session_state["location_query"].strip().lower()]
        if exact:
            st.session_state["selected_loc"] = exact[0]
            st.session_state["confirmed_location"] = True

if (
    st.session_state.get("location_query_submitted") and
    st.session_state.get("locations_found")
):
    locs = st.session_state["locations_found"]
    if not st.session_state.get("confirmed_location"):
        st.warning("⚠️ No exact match. Please select:")
        opts = [f"{l['name']} (ID:{l['id']})" for l in locs]
        choice = st.selectbox("Select location", opts, key="loc_select")
        if st.button("Confirm Location", key="confirm_loc"):
            m = re.search(r'ID:(\d+)', choice)
            if m:
                sel = next((l for l in locs if str(l['id'])==m.group(1)), None)
                if sel:
                    st.session_state["selected_loc"] = sel
                    st.session_state["confirmed_location"] = True
            else:
                st.error("Couldn't parse ID.")

    if st.session_state.get("confirmed_location"):
        loc = st.session_state["selected_loc"]
        st.write(f"Selected: {loc['name']} (ID:{loc['id']})")

        c = st.session_state["category"]["value"]
        t = st.session_state["prop"]["value"]
        bed_selections = st.session_state.get("bedrooms", [])
        bath_selections = st.session_state.get("bathrooms", [])
        fu = st.session_state["furnishing"]["value"]
        cs = st.session_state["completion"]["value"]
        lw = st.session_state["listed_within"]["value"]
        ob = FILTER_OPTIONS["sort"]["options"][st.session_state["sort"]]

        url = f"{base_url}/en/search?l={loc['id']}&c={c}"
        if t:
            url += f"&t={t}"
        if bed_selections and "Any" not in bed_selections:
            for br in bed_selections:
                val = FILTER_OPTIONS["bedrooms"]["options"][br]
                if val:
                    url += f"&bdr[]={val}"
        if bath_selections and "Any" not in bath_selections:
            for ba in bath_selections:
                val = FILTER_OPTIONS["bathrooms"]["options"][ba]
                if val:
                    url += f"&btr[]={val}"
        if fu != '0':
            url += f"&fu={fu}"
        if cs:
            url += f"&cs={cs}"
        if lw:
            url += f"&lw={lw}"
        if ob:
            url += f"&ob={ob}"

        st.write("🔗 Final URL:", url)
        st.session_state["search_url"] = url
        
        # Save state for later use
        st.session_state["search_url"] = url
        st.session_state["location_name"] = loc['name']

        # Fetch pagination info
        if 'pagination_fetched' not in st.session_state or not st.session_state['pagination_fetched']:
            with st.spinner("Fetching listings and pagination..."):
                driver = setup_webdriver()
                total_pages, property_count = get_total_pages(driver, url)
                driver.quit()
                st.session_state["total_pages"] = total_pages
                st.session_state["property_count"] = property_count
                st.session_state['pagination_fetched'] = True

            st.success(f"📊 {property_count} properties found across {total_pages} pages.")
            st.markdown(f"🔗 [Open Search Page for {loc['name']}]({url})", unsafe_allow_html=True)

# ─── SECOND FORM: PAGINATION ───────────────────────────────────────────────────
if "search_url" in st.session_state and st.session_state.get("total_pages", 0) > 0:
    with st.form("page_scrape_form"):
        st.subheader("📄 How many pages to scrape?")
        st.info(f"Up to **{st.session_state['total_pages']}** pages available.")
        pages_to_scrape = st.number_input(
            "Pages to scrape:",
            min_value=1,
            max_value=st.session_state["total_pages"],
            value=min(3, st.session_state["total_pages"]),
            key="pages_to_scrape_input"
        )
        scrape_trigger = st.form_submit_button("🔁 Generate Page URLs")
        if scrape_trigger:
            st.session_state["scrape_triggered"] = True
            st.session_state["pages_to_scrape"] = pages_to_scrape

# ─── DISPLAY GENERATED PAGE URLS ───────────────────────────────────────────────
if st.session_state.get("scrape_triggered"):
    base = st.session_state["search_url"]
    n = st.session_state["pages_to_scrape"]
    # build AND store your pages_list
    pages_list = [(i, f"{base}&page={i}") for i in range(1, n+1)]
    st.session_state["pages_list"] = pages_list

    st.subheader("🔗 Pagination URLs")
    for i, u in pages_list:
        st.markdown(f"➡️ Page {i}: [Listing Link]({u})", unsafe_allow_html=True)

    st.download_button(
        "📥 Download Page URLs",
        data="\n".join(u for _, u in pages_list),
        file_name="pagination_urls.txt",
        mime="text/plain"
    )


# ─── SCRAPE LISTINGS (NO CACHE) ────────────────────────────────────────────────
if st.session_state.get("pages_list"):
    if st.button("🕵️‍♀️ Scrape Listings"):
        driver = setup_webdriver()
        all_listings = []
        current_serial = 1
        
        # Setup progress indicators
        total_pages = len(st.session_state["pages_list"])
        progress_text = st.empty()
        progress_bar = st.progress(0)
        
        # Loop through pages with progress tracking
        for idx, (page_num, page_url) in enumerate(st.session_state["pages_list"]):
            # Update progress indicators
            progress_text.text(f"🕸️ Scraping page {page_num} of {total_pages}...")
            progress_bar.progress((idx) / total_pages)  # Start of page processing
            
            # branch on the category *value*, not the label
            if st.session_state["transaction_type_value"] == "5":
                scraped = new_projects_listings(
                    driver, page_num, page_url, start_serial=current_serial
                )
            else:
                scraped = scrape_page_rent(
                    driver, page_num, page_url, start_serial=current_serial
                )
            
            for item in scraped:
                item["S.No."] = current_serial
                current_serial += 1
            all_listings.extend(scraped)
            
            # Update progress after completing each page
            progress_bar.progress((idx + 1) / total_pages)
        
        # Clean up progress indicators
        progress_text.empty()
        progress_bar.empty()
        
        driver.quit()
        
        if all_listings:
            # Store the listings in session state for reuse
            st.session_state["scraped_listings"] = all_listings
            
            # Create DataFrame
            listings_df = pd.DataFrame(all_listings)
            
            st.success(
                f"✅ Scraped {len(all_listings)} listings across "
                f"{len(st.session_state['pages_list'])} pages."
            )
            
            # Display the data
            st.dataframe(
                listings_df,
                hide_index=True,
                use_container_width=True
            )
            
            # Download buttons
            col1, col2 = st.columns(2)
            
            # Get current datetime for filename
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            location_name = st.session_state.get("location_name", "properties").replace(" ", "_")
            
            with col1:
                # CSV download button
                csv = listings_df.to_csv(index=False)
                st.download_button(
                    label="📥 Download as CSV",
                    data=csv,
                    file_name=f"{location_name}_listings_{timestamp}.csv",
                    mime="text/csv",
                )
            
            with col2:
                # Excel download button
                buffer = BytesIO()
                with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                    listings_df.to_excel(writer, index=False, sheet_name='Listings')
                    # Auto-adjust columns' width
                    worksheet = writer.sheets['Listings']
                    for i, col in enumerate(listings_df.columns):
                        # Find the maximum length in the column
                        column_len = max(listings_df[col].astype(str).map(len).max(), len(col)) + 2
                        worksheet.set_column(i, i, column_len)
                
                excel_data = buffer.getvalue()
                st.download_button(
                    label="📥 Download as Excel",
                    data=excel_data,
                    file_name=f"{location_name}_listings_{timestamp}.xlsx",
                    mime="application/vnd.ms-excel",
                )
        else:
            st.warning("⚠️ No listings found. Check your filters or selectors.")