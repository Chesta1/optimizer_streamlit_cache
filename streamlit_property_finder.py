# # import streamlit as st
# # import pandas as pd
# # from selenium import webdriver
# # from selenium.webdriver.chrome.service import Service
# # from selenium.webdriver.common.by import By
# # from selenium.webdriver.support.ui import WebDriverWait
# # from selenium.webdriver.support import expected_conditions as EC
# # from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
# # import time
# # import logging

# # # Configure logging
# # logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# # def setup_webdriver():
# #     chrome_options = webdriver.ChromeOptions()
# #     chrome_options.add_argument("--no-sandbox")
# #     chrome_options.add_argument("--disable-dev-shm-usage")
# #     chrome_options.add_argument("--headless")  # Run in headless mode for Streamlit
    
# #     # Let user input their chromedriver path
# #     chromedriver_path = st.session_state.get('chromedriver_path', '')
# #     service = Service(chromedriver_path)
    
# #     try:
# #         driver = webdriver.Chrome(service=service, options=chrome_options)
# #         return driver
# #     except Exception as e:
# #         st.error(f"Failed to setup WebDriver: {str(e)}")
# #         return None

# # def scrape_page(driver, page_number):
# #     wait = WebDriverWait(driver, 20)
    
# #     # Extract basic property information
# #     property_cards = wait.until(EC.presence_of_all_elements_located(
# #         (By.XPATH, "//a[contains(@class, 'property-card-module_property-card__link')]")
# #     ))
    
# #     properties = []
# #     for card in property_cards:
# #         property_data = {}
# #         property_data['url'] = card.get_attribute('href')
# #         property_data['title'] = card.get_attribute('title')
        
# #         title_parts = property_data['title'].split(' for sale in ')
# #         if len(title_parts) == 2:
# #             property_info, location = title_parts
# #             property_data['location'] = location.strip()
            
# #             info_parts = property_info.split(' - ')
# #             property_data['type'] = info_parts[0]
# #             property_data['bedrooms'] = info_parts[1] if len(info_parts) > 1 else 'N/A'
# #             property_data['bathrooms'] = info_parts[2] if len(info_parts) > 2 else 'N/A'
# #         else:
# #             property_data['location'] = 'N/A'
# #             property_data['type'] = 'N/A'
# #             property_data['bedrooms'] = 'N/A'
# #             property_data['bathrooms'] = 'N/A'
        
# #         properties.append(property_data)
    
# #     # Extract prices
# #     price_elements = wait.until(EC.presence_of_all_elements_located(
# #         (By.XPATH, "//p[@data-testid='property-card-price']")
# #     ))
# #     for i, price_element in enumerate(price_elements):
# #         if i < len(properties):
# #             properties[i]['price'] = price_element.text
    
# #     # Extract listing times
# #     listing_time_elements = wait.until(EC.presence_of_all_elements_located(
# #         (By.XPATH, "//p[contains(@class, 'styles-module_footer__publish-info')]")
# #     ))
# #     for i, listing_time_element in enumerate(listing_time_elements):
# #         if i < len(properties):
# #             properties[i]['listing_time'] = listing_time_element.text
    
# #     # Extract areas
# #     area_elements = driver.find_elements(By.XPATH, "//p[@data-testid='property-card-spec-area']")
# #     for i, area_element in enumerate(area_elements):
# #         if i < len(properties):
# #             properties[i]['area'] = area_element.text
    
# #     return properties

# # def main():
# #     st.title("Property Finder Scraper")
    
# #     # Sidebar configuration
# #     st.sidebar.header("Configuration")
    
# #     # ChromeDriver path input
# #     chromedriver_path = st.sidebar.text_input(
# #         "ChromeDriver Path",
# #         value=st.session_state.get('chromedriver_path', ''),
# #         help="Enter the path to your ChromeDriver executable"
# #     )
# #     st.session_state['chromedriver_path'] = chromedriver_path
    
# #     # Number of pages to scrape
# #     num_pages = st.sidebar.slider("Number of pages to scrape", 1, 10, 3)
    
# #     # Base URL input
# #     base_url = st.sidebar.text_input(
# #         "Base URL",
# #         value="https://www.propertyfinder.sa/en/search?l=8216&c=1&fu=0&ob=nd",
# #         help="Enter the base URL for property search"
# #     )
    
# #     # Start scraping button
# #     if st.sidebar.button("Start Scraping"):
# #         if not chromedriver_path:
# #             st.error("Please enter ChromeDriver path first!")
# #             return
        
# #         driver = None
# #         all_properties = []
# #         progress_bar = st.progress(0)
# #         status_text = st.empty()
        
# #         try:
# #             driver = setup_webdriver()
# #             if not driver:
# #                 return
            
# #             for page_number in range(1, num_pages + 1):
# #                 status_text.text(f"Scraping page {page_number} of {num_pages}...")
# #                 url = f"{base_url}&page={page_number}" if page_number > 1 else base_url
                
# #                 try:
# #                     driver.get(url)
# #                     properties = scrape_page(driver, page_number)
# #                     all_properties.extend(properties)
                    
# #                     # Update progress
# #                     progress = page_number / num_pages
# #                     progress_bar.progress(progress)
                    
# #                     time.sleep(5)  # Respectful delay between pages
                    
# #                 except Exception as e:
# #                     st.error(f"Error scraping page {page_number}: {str(e)}")
# #                     break
            
# #             # Convert to DataFrame and display results
# #             if all_properties:
# #                 df = pd.DataFrame(all_properties)
# #                 st.success(f"Successfully scraped {len(all_properties)} properties!")
                
# #                 # Display data
# #                 st.header("Scraped Property Data")
# #                 st.dataframe(df)
                
# #                 # Download button
# #                 csv = df.to_csv(index=False)
# #                 st.download_button(
# #                     label="Download data as CSV",
# #                     data=csv,
# #                     file_name="property_data.csv",
# #                     mime="text/csv"
# #                 )
                
# #                 # Basic analytics
# #                 st.header("Basic Analytics")
# #                 col1, col2 = st.columns(2)
                
# #                 with col1:
# #                     st.subheader("Properties by Type")
# #                     type_counts = df['type'].value_counts()
# #                     st.bar_chart(type_counts)
                
# #                 with col2:
# #                     st.subheader("Properties by Location")
# #                     location_counts = df['location'].value_counts().head(10)
# #                     st.bar_chart(location_counts)
                
# #         except Exception as e:
# #             st.error(f"An error occurred: {str(e)}")
# #         finally:
# #             if driver:
# #                 driver.quit()
# #                 status_text.text("Scraping completed!")

# # if __name__ == "__main__":
# #     main()



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
# import subprocess
# import traceback
# from selenium.webdriver.chrome.options import Options

# # Configure logging
# logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# # def setup_webdriver():
# #     chrome_options = webdriver.ChromeOptions()
# #     chrome_options.add_argument("--no-sandbox")
# #     chrome_options.add_argument("--disable-dev-shm-usage")
    
# #     # Hardcoded ChromeDriver path
# #     chromedriver_path = r"C:\Users\Chesta\Downloads\chromedriver-win64_130\chromedriver-win64\chromedriver.exe"
# #     service = Service(chromedriver_path)
# #     driver = webdriver.Chrome(service=service, options=chrome_options)
# #     return driver

# def setup_webdriver():
#     """Create and return a configured WebDriver instance."""
#     try:
#         # First check installed versions
#         try:
#             # Get Chromium version
#             chrome_version_output = subprocess.check_output(['chromium', '--version']).decode()
#             st.write(f"Installed Chromium: {chrome_version_output.strip()}")
            
#             # Get ChromeDriver version
#             chromedriver_version_output = subprocess.check_output(['chromedriver', '--version']).decode()
#             st.write(f"Installed ChromeDriver: {chromedriver_version_output.strip()}")
            
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
#         st.write("Attempting to initialize ChromeDriver...")
        
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


# def scrape_page(driver, page_number):
#     print(f"\n--- Scraping Page {page_number} ---")
#     wait = WebDriverWait(driver, 20)
    
#     # Extract basic property information
#     property_cards = wait.until(EC.presence_of_all_elements_located((By.XPATH, "//a[contains(@class, 'property-card-module_property-card__link')]")))
#     print(f"Found {len(property_cards)} property cards on this page.")
    
#     properties = []
#     for index, card in enumerate(property_cards, 1):
#         property_data = {}
#         property_data['url'] = card.get_attribute('href')
#         print(property_data['url'])
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
#     price_elements = wait.until(EC.presence_of_all_elements_located((By.XPATH, "//p[@data-testid='property-card-price']")))
#     for i, price_element in enumerate(price_elements):
#         if i < len(properties):
#             properties[i]['price'] = price_element.text
    
#     # Extract listing times
#     listing_time_elements = wait.until(EC.presence_of_all_elements_located((By.XPATH, "//p[contains(@class, 'styles-module_footer__publish-info')]")))
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
#     st.sidebar.header("Scraping Configuration")
    
#     # Number of pages to scrape in sidebar
#     num_pages = st.sidebar.slider("Number of pages to scrape", 1, 10, 3)
    
#     # Base URL input in sidebar
#     base_url = st.sidebar.text_input(
#         "Base URL",
#         value="https://www.propertyfinder.sa/en/search?l=8216&c=1&fu=0&ob=nd"
#     )
    
#     # Start scraping button
#     if st.sidebar.button("Start Scraping"):
#         driver = None
#         all_properties = []
#         progress_bar = st.progress(0)
#         status_text = st.empty()
        
#         try:
#             driver = setup_webdriver()
#             logging.info("WebDriver set up successfully.")
            
#             for page_number in range(1, num_pages + 1):
#                 status_text.text(f"Scraping page {page_number} of {num_pages}...")
#                 url = f"{base_url}&page={page_number}" if page_number > 1 else base_url
                
#                 try:
#                     driver.get(url)
#                     logging.info(f"Opened URL: {url}")
                    
#                     # Wait for page load
#                     WebDriverWait(driver, 20).until(
#                         EC.presence_of_element_located((By.XPATH, "//a[contains(@class, 'property-card-module_property-card__link')]"))
#                     )
                    
#                     properties = scrape_page(driver, page_number)
#                     all_properties.extend(properties)
                    
#                     # Update progress
#                     progress = page_number / num_pages
#                     progress_bar.progress(progress)
                    
#                     logging.info(f"Scraped {len(properties)} properties from page {page_number}")
#                     time.sleep(5)  # Wait before next page
                    
#                 except Exception as e:
#                     st.error(f"Error on page {page_number}: {str(e)}")
#                     if st.button("Continue to next page?"):
#                         continue
#                     else:
#                         break
            
#             # Display results
#             if all_properties:
#                 # Convert to DataFrame
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
                
#                 # Analytics
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
#                 logging.info("Browser closed.")

# if __name__ == "__main__":
#     main()


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
# import subprocess
# import traceback
# from selenium.webdriver.chrome.options import Options

# # Set page config
# st.set_page_config(
#     page_title="Property Finder Scraper",
#     page_icon="🏠",
#     layout="wide"
# )

# # Configure logging
# logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# def setup_webdriver():
#     """Create and return a configured WebDriver instance."""
#     try:
#         # First check installed versions
#         try:
#             # Get Chromium version
#             chrome_version_output = subprocess.check_output(['chromium', '--version']).decode()
#             st.write(f"Installed Chromium: {chrome_version_output.strip()}")
            
#             # Get ChromeDriver version
#             chromedriver_version_output = subprocess.check_output(['chromedriver', '--version']).decode()
#             st.write(f"Installed ChromeDriver: {chromedriver_version_output.strip()}")
            
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
#         st.write("Attempting to initialize ChromeDriver...")
        
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



# def scrape_page(driver, page_number):
#     print(f"\n--- Scraping Page {page_number} ---")
#     wait = WebDriverWait(driver, 20)
    
#     # Extract basic property information
#     property_cards = wait.until(EC.presence_of_all_elements_located((By.XPATH, "//a[contains(@class, 'property-card-module_property-card__link')]")))
#     print(f"Found {len(property_cards)} property cards on this page.")
    
#     properties = []
#     for index, card in enumerate(property_cards, 1):
#         property_data = {}
#         property_data['url'] = card.get_attribute('href')
#         print(property_data['url'] )
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
#     price_elements = wait.until(EC.presence_of_all_elements_located((By.XPATH, "//p[@data-testid='property-card-price']")))
#     for i, price_element in enumerate(price_elements):
#         if i < len(properties):
#             properties[i]['price'] = price_element.text
    
#     # Extract listing times
#     listing_time_elements = wait.until(EC.presence_of_all_elements_located((By.XPATH, "//p[contains(@class, 'styles-module_footer__publish-info')]")))
#     for i, listing_time_element in enumerate(listing_time_elements):
#         if i < len(properties):
#             properties[i]['listing_time'] = listing_time_element.text
    
#     # Extract areas
#     area_elements = driver.find_elements(By.XPATH, "//p[@data-testid='property-card-spec-area']")
#     for i, area_element in enumerate(area_elements):
#         if i < len(properties):
#             properties[i]['area'] = area_element.text
    
#     # Print extracted information
#     for index, property_data in enumerate(properties, 1):
#         print(f"\nProperty {index}:")
#         for key, value in property_data.items():
#             print(f"{key.capitalize()}: {value}")
    
#     return properties

# def main():
#     st.title("🏠 Property Finder Scraper")
#     st.write("Search and scrape property listings from PropertyFinder.ae")
    
#     # User inputs
#     col1, col2, col3 = st.columns(3)
    
#     with col1:
#         property_type = st.selectbox(
#             "Select Property Type",
#             options=["buy"],
#             index=0
#         )
    
#     with col2:
#         location = st.text_input("Enter Location", "Dubai")
    
#     with col3:
#         pages_to_scrape = st.number_input(
#             "Number of Pages to Scrape",
#             min_value=1,
#             max_value=10,
#             value=3
#         )
    
#     # Start scraping button
#     if st.button("Start Scraping", type="primary"):
#         try:
#             with st.spinner("Setting up web driver..."):
#                 driver = setup_webdriver()
            
#             st.info("Starting the scraping process...")
            
#             # Navigate to base URL
#             base_url = "https://www.propertyfinder.ae/"
#             driver.get(base_url)
            
#             # Setup wait
#             wait = WebDriverWait(driver, 10)
            
#             # Input location
#             search_input = wait.until(
#                 EC.presence_of_element_located((By.XPATH, "//input[@data-testid='multi-selection-autocomplete-template-input']"))
#             )
#             search_input.clear()
#             search_input.send_keys(location)
            
#             # Select property type
#             if property_type == "rent":
#                 wait.until(
#                     EC.element_to_be_clickable((By.XPATH, "//button[@data-testid='segmented-control-Rent']"))
#                 ).click()
#             else:
#                 wait.until(
#                     EC.element_to_be_clickable((By.XPATH, "//button[@data-testid='segmented-control-Buy']"))
#                 ).click()
            
#             # Click search
#             wait.until(
#                 EC.element_to_be_clickable((By.XPATH, "//button[@data-testid='home-page-filters-search']"))
#             ).click()
            
#             # Initialize progress bar
#             progress_bar = st.progress(0)
            
#             # Initialize list to store all properties
#             all_properties = []
            
#             # Scrape first page
#             st.write("Scraping page 1...")
#             properties = scrape_page(driver, 1)
#             all_properties.extend(properties)
#             progress_bar.progress(1/pages_to_scrape)
            
#             # Find and scrape additional pages
#             if pages_to_scrape > 1:
#                 pagination_buttons = driver.find_elements(By.XPATH, "//a[@data-testid='pagination-page-button']")
#                 page_links = []
                
#                 for btn in pagination_buttons:
#                     page_text = btn.text.strip()
#                     if page_text.isdigit():
#                         page_num = int(page_text)
#                         if page_num <= pages_to_scrape:
#                             href = btn.get_attribute("href")
#                             page_links.append((page_num, href))
                
#                 page_links.sort(key=lambda x: x[0])
                
#                 for page_num, href in page_links:
#                     if page_num > pages_to_scrape:
#                         break
                    
#                     st.write(f"Scraping page {page_num}...")
#                     driver.get(href)
#                     properties = scrape_page(driver, page_num)
#                     all_properties.extend(properties)
#                     progress_bar.progress(page_num/pages_to_scrape)
            
#             # Create DataFrame
#             df = pd.DataFrame(all_properties)
            
#             # Display results
#             st.success(f"Successfully scraped {len(all_properties)} properties!")
            
#             # Download button
#             st.download_button(
#                 label="Download Data as CSV",
#                 data=df.to_csv(index=False).encode('utf-8'),
#                 file_name=f"property_finder_{property_type}_{location}.csv",
#                 mime='text/csv'
#             )
            
#             # Display DataFrame
#             st.write("### Scraped Properties")
#             st.dataframe(df)
            
#         except Exception as e:
#             st.error(f"An error occurred: {str(e)}")
        
#         finally:
#             driver.quit()

# if __name__ == "__main__":
#     main()

import streamlit as st
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException,
    NoSuchElementException,
    WebDriverException
)
import time
import logging
import traceback
from selenium.webdriver.chrome.options import Options
import sqlite3
from datetime import datetime, timedelta
from typing import List, Dict, Tuple
import subprocess


CACHE_TTL_HOURS = 24
DB_FILE = "locations_cache.db"

# Set page config for Streamlit
st.set_page_config(
    page_title="Property Finder Scraper",
    page_icon="🏠",
    layout="wide"
)

# # Configure logging
# logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def setup_logging():
    """Setup logging configuration."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    return logging.getLogger(__name__)

logger = setup_logging()


def init_db():
    """Initialize SQLite database for storing location and property type cache metadata."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    try:
        # Check if the table exists
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='location_cache'
        """)
        table_exists = cursor.fetchone() is not None
        
        if not table_exists:
            # Create new table with all required columns
            cursor.execute("""
                CREATE TABLE location_cache(
                    location TEXT,
                    property_type TEXT,
                    timestamp TEXT,
                    PRIMARY KEY (location, property_type)
                )
            """)
        else:
            # Check if property_type column exists
            cursor.execute("PRAGMA table_info(location_cache)")
            columns = [col[1] for col in cursor.fetchall()]
            
            if 'property_type' not in columns:
                # Backup existing data
                cursor.execute("CREATE TABLE temp_backup AS SELECT * FROM location_cache")
                
                # Drop existing table
                cursor.execute("DROP TABLE location_cache")
                
                # Create new table with property_type column
                cursor.execute("""
                    CREATE TABLE location_cache(
                        location TEXT,
                        property_type TEXT,
                        timestamp TEXT,
                        PRIMARY KEY (location, property_type)
                    )
                """)
                
                # Restore data with default property_type
                cursor.execute("""
                    INSERT INTO location_cache (location, property_type, timestamp)
                    SELECT location, 'unknown', timestamp FROM temp_backup
                """)
                
                # Drop backup table
                cursor.execute("DROP TABLE temp_backup")
                
                # Clear all cache since the structure changed
                st.cache_data.clear()
                logger.info("Database schema updated to include property_type")
        
        conn.commit()
        logger.info("Database initialization completed successfully")
        
    except Exception as e:
        logger.error(f"Error during database initialization: {str(e)}")
        raise
    finally:
        conn.close()


def is_location_property_cached(location: str, property_type: str) -> bool:
    """Check if location and property type combination is cached and within TTL."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    try:
        cursor.execute(
            "SELECT timestamp FROM location_cache WHERE location = ? AND property_type = ?", 
            (location, property_type)
        )
        row = cursor.fetchone()
        if row:
            cached_time = datetime.strptime(row[0], "%Y-%m-%d %H:%M:%S")
            return datetime.now() - cached_time < timedelta(hours=CACHE_TTL_HOURS)
        return False
    finally:
        conn.close()

def update_location_cache(location: str, property_type: str):
    """Update cache timestamp for a location and property type combination."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    try:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("""
            INSERT OR REPLACE INTO location_cache (location, property_type, timestamp)
            VALUES (?, ?, ?)
        """, (location, property_type, timestamp))
        conn.commit()
    finally:
        conn.close()

def get_cached_locations() -> List[Tuple[str, str, str]]:
    """Get all cached locations with their property types and timestamps."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    try:
        return cursor.execute(
            "SELECT location, property_type, timestamp FROM location_cache"
        ).fetchall()
    finally:
        conn.close()

def clear_location_cache(location: str, property_type: str = None):
    """Clear cache for specific location and optionally property type."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    try:
        if property_type:
            cursor.execute(
                "DELETE FROM location_cache WHERE location = ? AND property_type = ?",
                (location, property_type)
            )
        else:
            cursor.execute("DELETE FROM location_cache WHERE location = ?", (location,))
        conn.commit()
        st.cache_data.clear()
        logger.info(f"Cache cleared for location: {location}" + 
                   (f" and property type: {property_type}" if property_type else ""))
    except Exception as e:
        logger.error(f"Error clearing cache: {str(e)}")
    finally:
        conn.close()


def clear_all_cache():
    """Clear all cache data."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM location_cache")
   
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
        cursor.execute(
            "SELECT location, property_type FROM location_cache WHERE timestamp < ?",
            (threshold,)
        )
        stale_entries = cursor.fetchall()

        cursor.execute("DELETE FROM location_cache WHERE timestamp < ?", (threshold,))
        conn.commit()

        if stale_entries:
            st.cache_data.clear()
            logger.info(f"Stale cache entries removed: {stale_entries}")
    except Exception as e:
        logger.error(f"Error during cache cleanup: {str(e)}")
    finally:
        conn.close()


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

def scrape_page_buy(driver, page_number):
    """
    Scrape a single 'buy' results page.
    This logic relies on the 'title' containing the phrase ' for sale in '.
    """
    # print(f"\n--- Scraping Page (Buy) {page_number} ---")
    wait = WebDriverWait(driver, 20)
    
    # Wait for property-card links to appear
    property_cards = wait.until(
        EC.presence_of_all_elements_located(
            (By.XPATH, "//a[contains(@class, 'property-card-module_property-card__link')]")
        )
    )
    # print(f"Found {len(property_cards)} property cards on buy page {page_number}.")

    properties = []
    for card in property_cards:
        property_data = {}
        
        # Link URL & Title
        property_data['url'] = card.get_attribute('href')
        property_data['title'] = card.get_attribute('title')
        
        # Example: "Apartment - 2 Bedrooms - 3 Bathrooms for sale in XYZ"
        title_text = property_data['title'] or ""
        title_parts = title_text.split(' for sale in ')
        if len(title_parts) == 2:
            property_info, location = title_parts
            property_data['location'] = location.strip()
            
            info_parts = property_info.split(' - ')
            property_data['type'] = info_parts[0] if len(info_parts) > 0 else 'N/A'
            property_data['bedrooms'] = info_parts[1] if len(info_parts) > 1 else 'N/A'
            property_data['bathrooms'] = info_parts[2] if len(info_parts) > 2 else 'N/A'
        else:
            property_data['location'] = 'N/A'
            property_data['type'] = 'N/A'
            property_data['bedrooms'] = 'N/A'
            property_data['bathrooms'] = 'N/A'
        
        properties.append(property_data)
    
    # Price
    price_elements = wait.until(
        EC.presence_of_all_elements_located((By.XPATH, "//p[@data-testid='property-card-price']"))
    )
    for i, price_element in enumerate(price_elements):
        if i < len(properties):
            properties[i]['price'] = price_element.text
    
    # Listing time
    listing_time_elements = wait.until(
        EC.presence_of_all_elements_located(
            (By.XPATH, "//p[contains(@class, 'styles-module_footer__publish-info')]")
        )
    )
    for i, listing_time_element in enumerate(listing_time_elements):
        if i < len(properties):
            properties[i]['listing_time'] = listing_time_element.text
    
    # Area
    area_elements = driver.find_elements(By.XPATH, "//p[@data-testid='property-card-spec-area']")
    for i, area_element in enumerate(area_elements):
        if i < len(properties):
            properties[i]['area'] = area_element.text
    
    # Debug print
    # for idx, prop in enumerate(properties, 1):
    #     print(f"\n[Buy] Property #{idx} on page {page_number}:")
    #     for k, v in prop.items():
    #         print(f"  {k}: {v}")

    return properties


def scrape_page_rent(driver, page_number):
    """
    Scrape a single 'rent' results page by targeting <li role='listitem'> 
    and pulling data from child elements via data-testid or class.
    """
    #print(f"\n--- Scraping Page (Rent) {page_number} ---")
    wait = WebDriverWait(driver, 20)

    # All list items with role="listitem"
    li_items = wait.until(
        EC.presence_of_all_elements_located(
            (By.XPATH, "//li[@role='listitem']")
        )
    )
    #print(f"Found {len(li_items)} property cards on rent page {page_number}.")

    properties = []

    for li in li_items:
        property_data = {}

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

    # Debug print
    # for idx, prop in enumerate(properties, 1):
    #     print(f"\n[Rent] Property #{idx} on page {page_number}:")
    #     for k, v in prop.items():
    #         print(f"  {k}: {v}")

    return properties
@st.cache_data(ttl=60*60*24)  # 24 hour TTL
def get_cached_property_data(location: str, property_type: str, pages: int) -> pd.DataFrame:
    """
    Get property data either from cache or by scraping.
    Uses Streamlit's cache_data decorator with 24-hour TTL.
    """
    if not is_location_property_cached(location, property_type):
        # If not in cache, scrape the data
        properties = scrape_properties(location, property_type, pages)
        df = pd.DataFrame(properties)
        if not df.empty:
            update_location_cache(location, property_type)
        return df
    else:
        # Load from cache (Streamlit will handle this automatically)
        logger.info(f"Using cached data for location: {location} and property type: {property_type}")
        return pd.DataFrame()  # Cache hit, Streamlit will return cached value
    
def scrape_properties(location: str, property_type: str, pages: int) -> List[Dict]:
    """
    Main scraping function that handles both rent and buy properties.
    Returns list of property dictionaries.
    """
    driver = setup_webdriver()
    try:
        all_properties = []
        
        # Navigate and setup initial page
        base_url = "https://www.propertyfinder.ae/"
        driver.get(base_url)
        wait = WebDriverWait(driver, 10)
        
        # Input location and property type
        search_input = wait.until(
            EC.presence_of_element_located(
                (By.XPATH, "//input[@data-testid='multi-selection-autocomplete-template-input']")
            )
        )
        search_input.clear()
        search_input.send_keys(location)
        
        # Select property type
        if property_type == "rent":
            wait.until(
                EC.element_to_be_clickable((By.XPATH, "//button[@data-testid='segmented-control-Rent']"))
            ).click()
        else:
            wait.until(
                EC.element_to_be_clickable((By.XPATH, "//button[@data-testid='segmented-control-Buy']"))
            ).click()
            
        # Click search
        wait.until(
            EC.element_to_be_clickable((By.XPATH, "//button[@data-testid='home-page-filters-search']"))
        ).click()
        
        # Scrape first page
        if property_type == "rent":
            properties = scrape_page_rent(driver, 1)
        else:
            properties = scrape_page_buy(driver, 1)
        all_properties.extend(properties)
        
        # Handle pagination if more than one page
        if pages > 1:
            pagination_buttons = driver.find_elements(
                By.XPATH,
                "//a[@data-testid='pagination-page-button']"
            )
            page_links = []
            
            for btn in pagination_buttons:
                page_text = btn.text.strip()
                if page_text.isdigit():
                    page_num = int(page_text)
                    if page_num <= pages:
                        href = btn.get_attribute("href")
                        page_links.append((page_num, href))
            
            page_links.sort(key=lambda x: x[0])
            
            for page_num, href in page_links:
                if page_num > pages:
                    break
                
                driver.get(href)
                if property_type == "rent":
                    properties = scrape_page_rent(driver, page_num)
                else:
                    properties = scrape_page_buy(driver, page_num)
                all_properties.extend(properties)
                
        return all_properties
        
    finally:
        driver.quit()

def main():
    st.title("🏠 Property Finder Scraper")
    st.write("Search and scrape property listings from PropertyFinder.ae")
    
    # Initialize database
    init_db()
    
    # Clean up stale cache entries
    cleanup_stale_cache()
    
    # Show cached locations with property types
    st.sidebar.header("Cache Status")
    cached_entries = get_cached_locations()
    if cached_entries:
        st.sidebar.write("Currently cached data:")
        for location, prop_type, timestamp in cached_entries:
            cached_time = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
            time_left = cached_time + timedelta(hours=CACHE_TTL_HOURS) - datetime.now()
            hours_left = time_left.total_seconds() / 3600
            
            if hours_left > 0:  # Only show if not expired
                status_text = f"📍 {location} ({prop_type}) - {hours_left:.1f} hours left"
                col1, col2 = st.sidebar.columns([3, 1])
                col1.write(status_text)
                if col2.button("Clear", key=f"clear_{location}_{prop_type}"):
                    clear_location_cache(location, prop_type)
                    st.experimental_rerun()
    
    # Clear all cache button
    if st.sidebar.button("Clear All Cache"):
        clear_all_cache()
        st.experimental_rerun()
    
    # Main interface
    col1, col2, col3 = st.columns(3)
    
    with col1:
        selected_property_type = st.selectbox(
            "Select Property Type",
            options=["rent", "buy"],
            index=0
        )
    
    with col2:
        location = st.text_input("Enter Location", "Dubai")
    
    with col3:
        pages_to_scrape = st.number_input(
            "Number of Pages to Scrape",
            min_value=1,
            max_value=10,
            value=3
        )
    
    if st.button("Start Scraping", type="primary"):
        try:
            with st.spinner("Fetching property data..."):
                # Check if the data exists in cache
                df = get_cached_property_data(location, selected_property_type, pages_to_scrape)
                
                if not df.empty:
                    st.success(f"Successfully retrieved {len(df)} properties!")
                    
                    # Download button
                    st.download_button(
                        label="Download Data as CSV",
                        data=df.to_csv(index=False).encode('utf-8'),
                        file_name=f"property_finder_{selected_property_type}_{location}.csv",
                        mime='text/csv'
                    )
                    
                    # Display DataFrame
                    st.write("### Property Data")
                    st.dataframe(df)
                else:
                    st.warning("No data found for the specified location and property type. Starting fresh scrape...")
                    # Start fresh scrape
                    df = get_cached_property_data(location, selected_property_type, pages_to_scrape)
                    if not df.empty:
                        st.success(f"Successfully scraped {len(df)} properties!")
                        st.dataframe(df)
                    else:
                        st.error("No properties found for the given criteria.")
                    
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
            st.error(traceback.format_exc())

if __name__ == "__main__":
    main()