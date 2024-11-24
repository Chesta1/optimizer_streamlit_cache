# import streamlit as st
# import pandas as pd
# from selenium import webdriver
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
# import time
# import logging

# # Configure logging
# logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# def setup_webdriver():
#     chrome_options = webdriver.ChromeOptions()
#     chrome_options.add_argument("--no-sandbox")
#     chrome_options.add_argument("--disable-dev-shm-usage")
#     chrome_options.add_argument("--headless")  # Run in headless mode for Streamlit
    
#     # Let user input their chromedriver path
#     chromedriver_path = st.session_state.get('chromedriver_path', '')
#     service = Service(chromedriver_path)
    
#     try:
#         driver = webdriver.Chrome(service=service, options=chrome_options)
#         return driver
#     except Exception as e:
#         st.error(f"Failed to setup WebDriver: {str(e)}")
#         return None

# def scrape_page(driver, page_number):
#     wait = WebDriverWait(driver, 20)
    
#     # Extract basic property information
#     property_cards = wait.until(EC.presence_of_all_elements_located(
#         (By.XPATH, "//a[contains(@class, 'property-card-module_property-card__link')]")
#     ))
    
#     properties = []
#     for card in property_cards:
#         property_data = {}
#         property_data['url'] = card.get_attribute('href')
#         property_data['title'] = card.get_attribute('title')
        
#         title_parts = property_data['title'].split(' for sale in ')
#         if len(title_parts) == 2:
#             property_info, location = title_parts
#             property_data['location'] = location.strip()
            
#             info_parts = property_info.split(' - ')
#             property_data['type'] = info_parts[0]
#             property_data['bedrooms'] = info_parts[1] if len(info_parts) > 1 else 'N/A'
#             property_data['bathrooms'] = info_parts[2] if len(info_parts) > 2 else 'N/A'
#         else:
#             property_data['location'] = 'N/A'
#             property_data['type'] = 'N/A'
#             property_data['bedrooms'] = 'N/A'
#             property_data['bathrooms'] = 'N/A'
        
#         properties.append(property_data)
    
#     # Extract prices
#     price_elements = wait.until(EC.presence_of_all_elements_located(
#         (By.XPATH, "//p[@data-testid='property-card-price']")
#     ))
#     for i, price_element in enumerate(price_elements):
#         if i < len(properties):
#             properties[i]['price'] = price_element.text
    
#     # Extract listing times
#     listing_time_elements = wait.until(EC.presence_of_all_elements_located(
#         (By.XPATH, "//p[contains(@class, 'styles-module_footer__publish-info')]")
#     ))
#     for i, listing_time_element in enumerate(listing_time_elements):
#         if i < len(properties):
#             properties[i]['listing_time'] = listing_time_element.text
    
#     # Extract areas
#     area_elements = driver.find_elements(By.XPATH, "//p[@data-testid='property-card-spec-area']")
#     for i, area_element in enumerate(area_elements):
#         if i < len(properties):
#             properties[i]['area'] = area_element.text
    
#     return properties

# def main():
#     st.title("Property Finder Scraper")
    
#     # Sidebar configuration
#     st.sidebar.header("Configuration")
    
#     # ChromeDriver path input
#     chromedriver_path = st.sidebar.text_input(
#         "ChromeDriver Path",
#         value=st.session_state.get('chromedriver_path', ''),
#         help="Enter the path to your ChromeDriver executable"
#     )
#     st.session_state['chromedriver_path'] = chromedriver_path
    
#     # Number of pages to scrape
#     num_pages = st.sidebar.slider("Number of pages to scrape", 1, 10, 3)
    
#     # Base URL input
#     base_url = st.sidebar.text_input(
#         "Base URL",
#         value="https://www.propertyfinder.sa/en/search?l=8216&c=1&fu=0&ob=nd",
#         help="Enter the base URL for property search"
#     )
    
#     # Start scraping button
#     if st.sidebar.button("Start Scraping"):
#         if not chromedriver_path:
#             st.error("Please enter ChromeDriver path first!")
#             return
        
#         driver = None
#         all_properties = []
#         progress_bar = st.progress(0)
#         status_text = st.empty()
        
#         try:
#             driver = setup_webdriver()
#             if not driver:
#                 return
            
#             for page_number in range(1, num_pages + 1):
#                 status_text.text(f"Scraping page {page_number} of {num_pages}...")
#                 url = f"{base_url}&page={page_number}" if page_number > 1 else base_url
                
#                 try:
#                     driver.get(url)
#                     properties = scrape_page(driver, page_number)
#                     all_properties.extend(properties)
                    
#                     # Update progress
#                     progress = page_number / num_pages
#                     progress_bar.progress(progress)
                    
#                     time.sleep(5)  # Respectful delay between pages
                    
#                 except Exception as e:
#                     st.error(f"Error scraping page {page_number}: {str(e)}")
#                     break
            
#             # Convert to DataFrame and display results
#             if all_properties:
#                 df = pd.DataFrame(all_properties)
#                 st.success(f"Successfully scraped {len(all_properties)} properties!")
                
#                 # Display data
#                 st.header("Scraped Property Data")
#                 st.dataframe(df)
                
#                 # Download button
#                 csv = df.to_csv(index=False)
#                 st.download_button(
#                     label="Download data as CSV",
#                     data=csv,
#                     file_name="property_data.csv",
#                     mime="text/csv"
#                 )
                
#                 # Basic analytics
#                 st.header("Basic Analytics")
#                 col1, col2 = st.columns(2)
                
#                 with col1:
#                     st.subheader("Properties by Type")
#                     type_counts = df['type'].value_counts()
#                     st.bar_chart(type_counts)
                
#                 with col2:
#                     st.subheader("Properties by Location")
#                     location_counts = df['location'].value_counts().head(10)
#                     st.bar_chart(location_counts)
                
#         except Exception as e:
#             st.error(f"An error occurred: {str(e)}")
#         finally:
#             if driver:
#                 driver.quit()
#                 status_text.text("Scraping completed!")

# if __name__ == "__main__":
#     main()



import streamlit as st
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
import time
import logging
import subprocess
import traceback
from selenium.webdriver.chrome.options import Options

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# def setup_webdriver():
#     chrome_options = webdriver.ChromeOptions()
#     chrome_options.add_argument("--no-sandbox")
#     chrome_options.add_argument("--disable-dev-shm-usage")
    
#     # Hardcoded ChromeDriver path
#     chromedriver_path = r"C:\Users\Chesta\Downloads\chromedriver-win64_130\chromedriver-win64\chromedriver.exe"
#     service = Service(chromedriver_path)
#     driver = webdriver.Chrome(service=service, options=chrome_options)
#     return driver

def setup_webdriver():
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


def scrape_page(driver, page_number):
    print(f"\n--- Scraping Page {page_number} ---")
    wait = WebDriverWait(driver, 20)
    
    # Extract basic property information
    property_cards = wait.until(EC.presence_of_all_elements_located((By.XPATH, "//a[contains(@class, 'property-card-module_property-card__link')]")))
    print(f"Found {len(property_cards)} property cards on this page.")
    
    properties = []
    for index, card in enumerate(property_cards, 1):
        property_data = {}
        property_data['url'] = card.get_attribute('href')
        print(property_data['url'])
        property_data['title'] = card.get_attribute('title')
        
        title_parts = property_data['title'].split(' for sale in ')
        if len(title_parts) == 2:
            property_info, location = title_parts
            property_data['location'] = location.strip()
            
            info_parts = property_info.split(' - ')
            property_data['type'] = info_parts[0]
            property_data['bedrooms'] = info_parts[1] if len(info_parts) > 1 else 'N/A'
            property_data['bathrooms'] = info_parts[2] if len(info_parts) > 2 else 'N/A'
        else:
            property_data['location'] = 'N/A'
            property_data['type'] = 'N/A'
            property_data['bedrooms'] = 'N/A'
            property_data['bathrooms'] = 'N/A'
        
        properties.append(property_data)
    
    # Extract prices
    price_elements = wait.until(EC.presence_of_all_elements_located((By.XPATH, "//p[@data-testid='property-card-price']")))
    for i, price_element in enumerate(price_elements):
        if i < len(properties):
            properties[i]['price'] = price_element.text
    
    # Extract listing times
    listing_time_elements = wait.until(EC.presence_of_all_elements_located((By.XPATH, "//p[contains(@class, 'styles-module_footer__publish-info')]")))
    for i, listing_time_element in enumerate(listing_time_elements):
        if i < len(properties):
            properties[i]['listing_time'] = listing_time_element.text
    
    # Extract areas
    area_elements = driver.find_elements(By.XPATH, "//p[@data-testid='property-card-spec-area']")
    for i, area_element in enumerate(area_elements):
        if i < len(properties):
            properties[i]['area'] = area_element.text
    
    return properties

def main():
    st.title("Property Finder Scraper")
    
    # Sidebar configuration
    st.sidebar.header("Scraping Configuration")
    
    # Number of pages to scrape in sidebar
    num_pages = st.sidebar.slider("Number of pages to scrape", 1, 10, 3)
    
    # Base URL input in sidebar
    base_url = st.sidebar.text_input(
        "Base URL",
        value="https://www.propertyfinder.sa/en/search?l=8216&c=1&fu=0&ob=nd"
    )
    
    # Start scraping button
    if st.sidebar.button("Start Scraping"):
        driver = None
        all_properties = []
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        try:
            driver = setup_webdriver()
            logging.info("WebDriver set up successfully.")
            
            for page_number in range(1, num_pages + 1):
                status_text.text(f"Scraping page {page_number} of {num_pages}...")
                url = f"{base_url}&page={page_number}" if page_number > 1 else base_url
                
                try:
                    driver.get(url)
                    logging.info(f"Opened URL: {url}")
                    
                    # Wait for page load
                    WebDriverWait(driver, 20).until(
                        EC.presence_of_element_located((By.XPATH, "//a[contains(@class, 'property-card-module_property-card__link')]"))
                    )
                    
                    properties = scrape_page(driver, page_number)
                    all_properties.extend(properties)
                    
                    # Update progress
                    progress = page_number / num_pages
                    progress_bar.progress(progress)
                    
                    logging.info(f"Scraped {len(properties)} properties from page {page_number}")
                    time.sleep(5)  # Wait before next page
                    
                except Exception as e:
                    st.error(f"Error on page {page_number}: {str(e)}")
                    if st.button("Continue to next page?"):
                        continue
                    else:
                        break
            
            # Display results
            if all_properties:
                # Convert to DataFrame
                df = pd.DataFrame(all_properties)
                st.success(f"Successfully scraped {len(all_properties)} properties!")
                
                # Display data
                st.header("Scraped Property Data")
                st.dataframe(df)
                
                # Download button
                csv = df.to_csv(index=False)
                st.download_button(
                    label="Download data as CSV",
                    data=csv,
                    file_name="property_data.csv",
                    mime="text/csv"
                )
                
                # Analytics
                st.header("Basic Analytics")
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("Properties by Type")
                    type_counts = df['type'].value_counts()
                    st.bar_chart(type_counts)
                
                with col2:
                    st.subheader("Properties by Location")
                    location_counts = df['location'].value_counts().head(10)
                    st.bar_chart(location_counts)
                
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
        finally:
            if driver:
                driver.quit()
                status_text.text("Scraping completed!")
                logging.info("Browser closed.")

if __name__ == "__main__":
    main()