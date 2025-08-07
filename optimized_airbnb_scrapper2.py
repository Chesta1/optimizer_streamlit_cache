# # Step 1: Enhanced Navigation with Anti-Detection Measures
# # This handles the popup issue when Selenium is detected

# import time
# import urllib.parse
# from datetime import datetime, timedelta
# from selenium import webdriver
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# import streamlit as st
# import subprocess
# import traceback

# def get_stealth_driver():
#     """Create a stealth WebDriver that's harder to detect."""
#     try:
#         print("🚀 Creating Stealth WebDriver...")
#         st.write("🚀 Creating Stealth WebDriver...")
        
#         # Initialize Chrome options with stealth settings
#         chrome_options = Options()
        
#         # Headless mode disabled for testing
#         chrome_options.headless = False
        
#         # Anti-detection options
#         chrome_options.add_argument("--disable-blink-features=AutomationControlled")
#         chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
#         chrome_options.add_experimental_option('useAutomationExtension', False)
        
#         # Basic options
#         chrome_options.add_argument("--disable-dev-shm-usage")
#         chrome_options.add_argument("--disable-gpu")
#         chrome_options.add_argument("--window-size=1920,1080")
#         chrome_options.add_argument("--disable-infobars")
#         chrome_options.add_argument("--disable-notifications")
        
#         # More realistic user agent
#         chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
#         # Your ChromeDriver path
#         chromedriver_path = r"C:\Users\Chesta\Downloads\chromedriver-win64 (1)\chromedriver-win64\chromedriver.exe"
        
#         # Initialize service
#         service = Service(executable_path=chromedriver_path)
        
#         # Create driver
#         driver = webdriver.Chrome(service=service, options=chrome_options)
        
#         # Execute script to hide webdriver property
#         driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
#         # Additional stealth scripts
#         driver.execute_script("""
#             Object.defineProperty(navigator, 'plugins', {
#                 get: () => [1, 2, 3, 4, 5]
#             });
#         """)
        
#         driver.execute_script("""
#             Object.defineProperty(navigator, 'languages', {
#                 get: () => ['en-US', 'en']
#             });
#         """)
        
#         print("✅ Stealth Driver created successfully")
#         st.write("✅ Stealth Driver created successfully")
        
#         return driver
        
#     except Exception as e:
#         print(f"❌ Failed to initialize ChromeDriver: {str(e)}")
#         st.error(f"❌ Failed to initialize ChromeDriver: {str(e)}")
#         raise

# def navigate_with_manual_approach(driver, search_location):
#     """Navigate to Airbnb using a more manual approach to avoid detection."""
#     try:
#         print(f"🌐 Starting manual navigation approach for: {search_location}")
#         st.write(f"🌐 Starting manual navigation approach for: {search_location}")
        
#         # Step 1: Go to Airbnb homepage first (looks more natural)
#         print("🏠 First, going to Airbnb homepage...")
#         st.write("🏠 First, going to Airbnb homepage...")
#         driver.get("https://www.airbnb.com")
#         time.sleep(3)
        
#         print(f"📄 Homepage loaded: {driver.title}")
#         st.write(f"📄 Homepage loaded: {driver.title}")
        
#         # Step 2: Now build the search URL
#         today = datetime.now()
#         check_in_date = today + timedelta(days=1)
#         check_out = check_in_date + timedelta(days=6)
        
#         checkin_str = check_in_date.strftime('%Y-%m-%d')
#         checkout_str = check_out.strftime('%Y-%m-%d')
        
#         print(f"📅 Dates: {checkin_str} to {checkout_str}")
#         st.write(f"📅 Dates: {checkin_str} to {checkout_str}")
        
#         # Step 3: Navigate to search results
#         search_url = f"https://www.airbnb.com/s/{urllib.parse.quote(search_location)}/homes?checkin={checkin_str}&checkout={checkout_str}"
        
#         print(f"🔗 Search URL: {search_url}")
#         st.write(f"🔗 Search URL: {search_url}")
        
#         print("🔍 Navigating to search results...")
#         st.write("🔍 Navigating to search results...")
        
#         driver.get(search_url)
#         time.sleep(5)
        
#         print(f"📄 Search page loaded: {driver.title}")
#         st.write(f"📄 Search page loaded: {driver.title}")
        
#         # Step 4: Check for popups and handle them
#         print("🔍 Checking for popups...")
#         st.write("🔍 Checking for popups...")
        
#         popup_found = check_and_handle_popups(driver)
        
#         if popup_found:
#             print("✅ Handled popups successfully")
#             st.write("✅ Handled popups successfully")
#         else:
#             print("ℹ️ No popups detected")
#             st.write("ℹ️ No popups detected")
        
#         # Step 5: Check if we successfully loaded listings
#         time.sleep(3)  # Wait for content to load
        
#         # Look for common Airbnb elements that indicate successful loading
#         indicators = [
#             "Over 1,000 homes",  # Text that often appears
#             "homes",
#             "listings"
#         ]
        
#         page_text = driver.page_source.lower()
#         success_indicators = [ind for ind in indicators if ind.lower() in page_text]
        
#         print(f"🎯 Found success indicators: {success_indicators}")
#         st.write(f"🎯 Found success indicators: {success_indicators}")
        
#         return True
        
#     except Exception as e:
#         print(f"❌ Navigation failed: {str(e)}")
#         st.error(f"❌ Navigation failed: {str(e)}")
#         return False

# def check_and_handle_popups(driver):
#     """Check for and handle common Airbnb popups."""
#     popup_found = False
    
#     try:
#         # Wait a bit for any popups to appear
#         time.sleep(2)
        
#         # Common popup selectors
#         popup_selectors = [
#             ("//button[contains(text(), 'Got it')]", "Got it button"),
#             ("//button[contains(text(), 'OK')]", "OK button"),
#             ("//button[contains(text(), 'Accept')]", "Accept button"),
#             ("//button[contains(text(), 'Continue')]", "Continue button"),
#             ("//button[@aria-label='Close']", "Close button"),
#             ("//div[@role='dialog']//button", "Dialog buttons"),
#         ]
        
#         for selector, description in popup_selectors:
#             try:
#                 elements = driver.find_elements(By.XPATH, selector)
#                 if elements:
#                     print(f"🔍 Found {len(elements)} {description}")
#                     st.write(f"🔍 Found {len(elements)} {description}")
                    
#                     for element in elements:
#                         if element.is_displayed() and element.is_enabled():
#                             print(f"🖱️ Clicking {description}")
#                             st.write(f"🖱️ Clicking {description}")
#                             element.click()
#                             popup_found = True
#                             time.sleep(1)
#                             break
#             except Exception as e:
#                 print(f"Error with {description}: {e}")
        
#         return popup_found
        
#     except Exception as e:
#         print(f"Error handling popups: {e}")
#         return False

# def main_step1_stealth():
#     """Main function for Step 1 - Stealth navigation test"""
#     st.set_page_config(page_title="Step 1: Stealth Airbnb Navigation", layout="wide")
#     st.title("Step 1: Stealth Airbnb Navigation Test")
#     st.write("This version uses anti-detection measures to avoid popups that appear when Selenium is detected.")
    
#     # User input for location
#     search_location = st.text_input(
#         "Enter Search Location:",
#         value="Riyadh",
#         help="Enter a location to search on Airbnb"
#     )
    
#     # Test navigation button
#     if st.button("🚀 Test Stealth Navigation"):
#         if not search_location.strip():
#             st.error("Please enter a search location.")
#             return
            
#         driver = None
#         try:
#             # Step 1: Create stealth driver
#             driver = get_stealth_driver()
            
#             # Step 2: Navigate with manual approach
#             success = navigate_with_manual_approach(driver, search_location)
            
#             if success:
#                 st.success("✅ Stealth navigation successful!")
#                 st.info("🔍 Check your Chrome browser window - it should show Airbnb listings without popups.")
#                 st.info("📱 The browser will stay open for inspection.")
                
#                 # Show current URL for comparison
#                 current_url = driver.current_url
#                 st.code(f"Current URL: {current_url}")
                
#                 st.warning("⚠️ Browser will stay open - close it manually when done.")
                
#             else:
#                 st.error("❌ Stealth navigation failed.")
#                 if driver:
#                     driver.quit()
                
#         except Exception as e:
#             st.error(f"💥 Error occurred: {str(e)}")
#             st.code(traceback.format_exc())
#             if driver:
#                 driver.quit()

# if __name__ == "__main__":
#     main_step1_stealth()

#-------------------------------------------------Second one attempt good one---------------------------------------------------------------

# import time
# import urllib.parse
# from datetime import datetime, timedelta
# from selenium import webdriver
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# import streamlit as st
# import subprocess
# import traceback

# def get_stealth_driver():
#     """Create a stealth WebDriver that's harder to detect."""
#     try:
#         print("🚀 Creating Stealth WebDriver...")
        
#         # Initialize Chrome options with stealth settings
#         chrome_options = Options()
        
#         # Headless mode disabled for testing
#         chrome_options.headless = False
        
#         # Anti-detection options
#         chrome_options.add_argument("--disable-blink-features=AutomationControlled")
#         chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
#         chrome_options.add_experimental_option('useAutomationExtension', False)
        
#         # Basic options
#         chrome_options.add_argument("--disable-dev-shm-usage")
#         chrome_options.add_argument("--disable-gpu")
#         chrome_options.add_argument("--window-size=1920,1080")
#         chrome_options.add_argument("--disable-infobars")
#         chrome_options.add_argument("--disable-notifications")
        
#         # More realistic user agent
#         chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
#         # Your ChromeDriver path
#         chromedriver_path = r"C:\Users\Chesta\Downloads\chromedriver-win64 (1)\chromedriver-win64\chromedriver.exe"
        
#         # Initialize service
#         service = Service(executable_path=chromedriver_path)
        
#         # Create driver
#         driver = webdriver.Chrome(service=service, options=chrome_options)
        
#         # Execute script to hide webdriver property
#         driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
#         # Additional stealth scripts
#         driver.execute_script("""
#             Object.defineProperty(navigator, 'plugins', {
#                 get: () => [1, 2, 3, 4, 5]
#             });
#         """)
        
#         driver.execute_script("""
#             Object.defineProperty(navigator, 'languages', {
#                 get: () => ['en-US', 'en']
#             });
#         """)
        
#         print("✅ Stealth Driver created successfully")
        
#         return driver
        
#     except Exception as e:
#         print(f"❌ Failed to initialize ChromeDriver: {str(e)}")
#         st.error(f"❌ Failed to initialize ChromeDriver: {str(e)}")
#         raise

# def navigate_with_manual_approach(driver, search_location):
#     """Navigate to Airbnb using a more manual approach to avoid detection."""
#     try:
#         print(f"🌐 Starting manual navigation approach for: {search_location}")
        
#         # Step 1: Go to Airbnb homepage first (looks more natural)
#         print("🏠 First, going to Airbnb homepage...")
#         driver.get("https://www.airbnb.com")
#         time.sleep(3)
        
#         print(f"📄 Homepage loaded: {driver.title}")
        
#         # Step 2: Now build the search URL
#         today = datetime.now()
#         check_in_date = today + timedelta(days=1)
#         check_out = check_in_date + timedelta(days=6)
        
#         checkin_str = check_in_date.strftime('%Y-%m-%d')
#         checkout_str = check_out.strftime('%Y-%m-%d')
        
#         print(f"📅 Dates: {checkin_str} to {checkout_str}")
        
#         # Step 3: Navigate to search results
#         search_url = f"https://www.airbnb.com/s/{urllib.parse.quote(search_location)}/homes?checkin={checkin_str}&checkout={checkout_str}"
        
#         print(f"🔗 Search URL: {search_url}")
        
#         print("🔍 Navigating to search results...")
        
#         driver.get(search_url)
#         time.sleep(5)
        
#         print(f"📄 Search page loaded: {driver.title}")
        
#         # Step 4: Check for popups and handle them
#         print("🔍 Checking for popups...")
        
#         popup_found = check_and_handle_popups(driver)
        
#         if popup_found:
#             print("✅ Handled popups successfully")
#         else:
#             print("ℹ️ No popups detected")
        
#         # Step 5: Check if we successfully loaded listings
#         time.sleep(3)  # Wait for content to load
        
#         # Look for common Airbnb elements that indicate successful loading
#         indicators = [
#             "Over 1,000 homes",  # Text that often appears
#             "homes",
#             "listings"
#         ]
        
#         page_text = driver.page_source.lower()
#         success_indicators = [ind for ind in indicators if ind.lower() in page_text]
        
#         print(f"🎯 Found success indicators: {success_indicators}")
        
#         return True
        
#     except Exception as e:
#         print(f"❌ Navigation failed: {str(e)}")
#         st.error(f"❌ Navigation failed: {str(e)}")
#         return False

# def check_and_handle_popups(driver):
#     """Check for and handle common Airbnb popups."""
#     popup_found = False
    
#     try:
#         # Wait a bit for any popups to appear
#         time.sleep(2)
        
#         # Common popup selectors
#         popup_selectors = [
#             ("//button[contains(text(), 'Got it')]", "Got it button"),
#             ("//button[contains(text(), 'OK')]", "OK button"),
#             ("//button[contains(text(), 'Accept')]", "Accept button"),
#             ("//button[contains(text(), 'Continue')]", "Continue button"),
#             ("//button[@aria-label='Close']", "Close button"),
#             ("//div[@role='dialog']//button", "Dialog buttons"),
#         ]
        
#         for selector, description in popup_selectors:
#             try:
#                 elements = driver.find_elements(By.XPATH, selector)
#                 if elements:
#                     print(f"🔍 Found {len(elements)} {description}")
                    
#                     for element in elements:
#                         if element.is_displayed() and element.is_enabled():
#                             print(f"🖱️ Clicking {description}")
#                             element.click()
#                             popup_found = True
#                             time.sleep(1)
#                             break
#             except Exception as e:
#                 print(f"Error with {description}: {e}")
        
#         return popup_found
        
#     except Exception as e:
#         print(f"Error handling popups: {e}")
#         return False

# def main_step1_stealth():
#     """Main function for Step 1 - Stealth navigation test"""
#     st.set_page_config(page_title="Step 1: Stealth Airbnb Navigation", layout="wide")
#     st.title("Step 1: Stealth Airbnb Navigation Test")
#     st.write("This version uses anti-detection measures to avoid popups that appear when Selenium is detected.")
    
#     # User input for location
#     search_location = st.text_input(
#         "Enter Search Location:",
#         value="Riyadh",
#         help="Enter a location to search on Airbnb"
#     )
    
#     # Test navigation button
#     if st.button("🚀 Test Stealth Navigation"):
#         if not search_location.strip():
#             st.error("Please enter a search location.")
#             return
            
#         driver = None
#         try:
#             # Step 1: Create stealth driver
#             driver = get_stealth_driver()
            
#             # Step 2: Navigate with manual approach
#             success = navigate_with_manual_approach(driver, search_location)
            
#             if success:
#                 st.success("✅ Stealth navigation successful!")
#                 st.info("🔍 Check your Chrome browser window - it should show Airbnb listings without popups.")
#                 st.info("📱 The browser will stay open for inspection.")
                
#                 # Show current URL for comparison
#                 current_url = driver.current_url
#                 st.code(f"Current URL: {current_url}")
                
#                 st.warning("⚠️ Browser will stay open - close it manually when done.")
                
#             else:
#                 st.error("❌ Stealth navigation failed.")
#                 if driver:
#                     driver.quit()
                
#         except Exception as e:
#             st.error(f"💥 Error occurred: {str(e)}")
#             st.code(traceback.format_exc())
#             if driver:
#                 driver.quit()

# if __name__ == "__main__":
#     main_step1_stealth()



#---------------------------------------Third Step----------------------------------------------------------

# Step 2: Enhanced Pagination with Stealth Navigation and Scrolling
# Combines stealth navigation with robust page navigation to the very last page

# import time
# import urllib.parse
# from datetime import datetime, timedelta
# from selenium import webdriver
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
# from selenium.webdriver.common.keys import Keys
# from bs4 import BeautifulSoup
# import streamlit as st
# import subprocess
# import traceback

# # Constants from your original code
# WAIT_TIMEOUT = 10
# PAGE_LOAD_DELAY = 3

# def get_stealth_driver():
#     """Create a stealth WebDriver that's harder to detect."""
#     try:
#         print("🚀 Creating Stealth WebDriver...")
        
#         # Initialize Chrome options with stealth settings
#         chrome_options = Options()
#         chrome_options.headless = False
        
#         # Anti-detection options
#         chrome_options.add_argument("--disable-blink-features=AutomationControlled")
#         chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
#         chrome_options.add_experimental_option('useAutomationExtension', False)
        
#         # Basic options
#         chrome_options.add_argument("--disable-dev-shm-usage")
#         chrome_options.add_argument("--disable-gpu")
#         chrome_options.add_argument("--window-size=1920,1080")
#         chrome_options.add_argument("--disable-infobars")
#         chrome_options.add_argument("--disable-notifications")
        
#         # More realistic user agent
#         chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
#         # Your ChromeDriver path
#         chromedriver_path = r"C:\Users\Chesta\Downloads\chromedriver-win64 (1)\chromedriver-win64\chromedriver.exe"
        
#         # Initialize service
#         service = Service(executable_path=chromedriver_path)
        
#         # Create driver
#         driver = webdriver.Chrome(service=service, options=chrome_options)
        
#         # Execute script to hide webdriver property
#         driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
#         # Additional stealth scripts
#         driver.execute_script("""
#             Object.defineProperty(navigator, 'plugins', {
#                 get: () => [1, 2, 3, 4, 5]
#             });
#         """)
        
#         driver.execute_script("""
#             Object.defineProperty(navigator, 'languages', {
#                 get: () => ['en-US', 'en']
#             });
#         """)
        
#         print("✅ Stealth Driver created successfully")
#         return driver
        
#     except Exception as e:
#         print(f"❌ Failed to initialize ChromeDriver: {str(e)}")
#         st.error(f"❌ Failed to initialize ChromeDriver: {str(e)}")
#         raise

# def handle_initial_popups(driver):
#     """Handle popups that appear on initial page load."""
#     print("🔍 Handling initial popups...")
    
#     try:
#         time.sleep(2)  # Wait for popups to appear
        
#         popup_selectors = [
#             ("//button[contains(text(), 'Got it')]", "Got it button"),
#             ("//button[contains(text(), 'OK')]", "OK button"),
#             ("//button[contains(text(), 'Accept')]", "Accept button"),
#             ("//button[contains(text(), 'Continue')]", "Continue button"),
#             ("//button[@aria-label='Close']", "Close button"),
#             ("//div[@role='dialog']//button", "Dialog buttons"),
#         ]
        
#         popup_handled = False
#         for selector, description in popup_selectors:
#             try:
#                 elements = driver.find_elements(By.XPATH, selector)
#                 if elements:
#                     print(f"🔍 Found {len(elements)} {description}")
                    
#                     for element in elements:
#                         if element.is_displayed() and element.is_enabled():
#                             print(f"🖱️ Clicking {description}")
#                             element.click()
#                             popup_handled = True
#                             time.sleep(1)
#                             break
#                     if popup_handled:
#                         break
#             except Exception as e:
#                 print(f"Error with {description}: {e}")
        
#         if popup_handled:
#             print("✅ Initial popups handled")
#         else:
#             print("ℹ️ No initial popups detected")
            
#     except Exception as e:
#         print(f"Error handling initial popups: {e}")

# def scroll_to_bottom_gradually(driver):
#     """Gradually scroll to bottom of page to load all content."""
#     print("📜 Scrolling to load all content...")
    
#     try:
#         # Get initial page height
#         last_height = driver.execute_script("return document.body.scrollHeight")
        
#         scroll_attempts = 0
#         max_scroll_attempts = 5
        
#         while scroll_attempts < max_scroll_attempts:
#             # Scroll down gradually
#             driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
#             time.sleep(2)
            
#             # Calculate new scroll height
#             new_height = driver.execute_script("return document.body.scrollHeight")
            
#             if new_height == last_height:
#                 # No more content loaded, break
#                 break
            
#             last_height = new_height
#             scroll_attempts += 1
#             print(f"📜 Scroll attempt {scroll_attempts}: Page height now {new_height}")
        
#         # Scroll back to top
#         driver.execute_script("window.scrollTo(0, 0);")
#         time.sleep(1)
#         print("📜 Scrolling complete, back to top")
        
#     except Exception as e:
#         print(f"Error during scrolling: {e}")

# def find_next_button_enhanced(driver):
#     """Enhanced next button finding with multiple strategies."""
#     print("🔍 Looking for Next button with multiple strategies...")
    
#     # Multiple selectors to try (from your original code + enhancements)
#     next_button_selectors = [
#         # Original from your code
#         ("//a[@aria-label='Next']", "Next aria-label"),
        
#         # Additional selectors
#         ("//a[contains(@aria-label, 'Next')]", "Next aria-label (contains)"),
#         ("//button[contains(@aria-label, 'Next')]", "Next button aria-label"),
#         ("//a[contains(text(), 'Next')]", "Next text"),
#         ("//button[contains(text(), 'Next')]", "Next button text"),
#         ("//a[@data-testid='pagination-next']", "Next pagination testid"),
#         ("//button[@data-testid='pagination-next']", "Next button pagination testid"),
#         ("//*[contains(@class, 'next') and contains(@class, 'button')]", "Next class button"),
#         ("//nav//a[last()]", "Last nav link (often Next)"),
#         ("//div[contains(@class, 'pagination')]//a[last()]", "Last pagination link"),
#     ]
    
#     for selector, description in next_button_selectors:
#         try:
#             print(f"🔍 Trying: {description}")
#             elements = driver.find_elements(By.XPATH, selector)
            
#             if elements:
#                 print(f"   Found {len(elements)} elements")
                
#                 for i, element in enumerate(elements):
#                     try:
#                         is_displayed = element.is_displayed()
#                         is_enabled = element.is_enabled()
#                         element_text = element.text.strip()
                        
#                         print(f"   Element {i+1}: displayed={is_displayed}, enabled={is_enabled}, text='{element_text}'")
                        
#                         if is_displayed and is_enabled:
#                             print(f"✅ Found usable Next button: {description}")
#                             return element
                            
#                     except Exception as e:
#                         print(f"   Element {i+1}: Error checking - {e}")
#                         continue
#             else:
#                 print("   No elements found")
                
#         except Exception as e:
#             print(f"   Error with {description}: {e}")
    
#     print("❌ No usable Next button found")
#     return None

# def click_next_button_safely(driver, next_button):
#     """Safely click the next button with scrolling and multiple attempts."""
#     print("🖱️ Attempting to click Next button safely...")
    
#     try:
#         # Strategy 1: Scroll button into view and click
#         print("🖱️ Strategy 1: Scroll into view and click")
#         driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", next_button)
#         time.sleep(1)
        
#         # Wait for any animations to complete
#         time.sleep(1)
        
#         try:
#             next_button.click()
#             print("✅ Successfully clicked Next button (Strategy 1)")
#             return True
#         except Exception as e:
#             print(f"Strategy 1 failed: {e}")
        
#         # Strategy 2: JavaScript click
#         print("🖱️ Strategy 2: JavaScript click")
#         try:
#             driver.execute_script("arguments[0].click();", next_button)
#             print("✅ Successfully clicked Next button (Strategy 2)")
#             return True
#         except Exception as e:
#             print(f"Strategy 2 failed: {e}")
        
#         # Strategy 3: Move to element and click
#         print("🖱️ Strategy 3: ActionChains move and click")
#         try:
#             from selenium.webdriver.common.action_chains import ActionChains
#             actions = ActionChains(driver)
#             actions.move_to_element(next_button).click().perform()
#             print("✅ Successfully clicked Next button (Strategy 3)")
#             return True
#         except Exception as e:
#             print(f"Strategy 3 failed: {e}")
        
#         # Strategy 4: Send ENTER key
#         print("🖱️ Strategy 4: Send ENTER key")
#         try:
#             next_button.send_keys(Keys.RETURN)
#             print("✅ Successfully activated Next button (Strategy 4)")
#             return True
#         except Exception as e:
#             print(f"Strategy 4 failed: {e}")
        
#         print("❌ All click strategies failed")
#         return False
        
#     except Exception as e:
#         print(f"❌ Error in click_next_button_safely: {e}")
#         return False

# def navigate_all_pages(driver, search_location):
#     """Navigate through all pages of Airbnb listings."""
#     try:
#         print(f"🚀 Starting complete page navigation for: {search_location}")
        
#         # Step 1: Initial navigation (from Step 1)
#         print("🏠 Going to Airbnb homepage first...")
#         driver.get("https://www.airbnb.com")
#         time.sleep(3)
        
#         # Step 2: Build search URL
#         today = datetime.now()
#         check_in_date = today + timedelta(days=1)
#         check_out = check_in_date + timedelta(days=6)
        
#         checkin_str = check_in_date.strftime('%Y-%m-%d')
#         checkout_str = check_out.strftime('%Y-%m-%d')
        
#         search_url = f"https://www.airbnb.com/s/{urllib.parse.quote(search_location)}/homes?checkin={checkin_str}&checkout={checkout_str}"
#         print(f"🔗 Search URL: {search_url}")
        
#         # Step 3: Navigate to search results
#         print("🔍 Navigating to search results...")
#         driver.get(search_url)
#         time.sleep(5)
        
#         # Step 4: Handle initial popups
#         handle_initial_popups(driver)
        
#         # Step 5: Page navigation loop (from your original code + enhancements)
#         page_number = 1
#         total_pages_processed = 0
#         max_pages = 50  # Safety limit
        
#         while page_number <= max_pages:
#             print(f"\n📄 Processing page {page_number}...")
            
#             # Scroll to load all content on current page
#             scroll_to_bottom_gradually(driver)
            
#             # Wait for page to stabilize
#             time.sleep(PAGE_LOAD_DELAY)
            
#             # Get page source for analysis (we'll extract listings in Step 3)
#             soup = BeautifulSoup(driver.page_source, 'html.parser')
            
#             # Quick check: count listings on this page
#             listing_elements = soup.find_all('div', {'itemprop': 'itemListElement'})
#             print(f"📊 Found {len(listing_elements)} listing elements on page {page_number}")
            
#             if len(listing_elements) == 0:
#                 print("⚠️ No listings found on this page - might be end of results")
#                 break
            
#             total_pages_processed += 1
            
#             # Look for Next button (from your original code + enhancements)
#             print(f"🔍 Looking for Next button on page {page_number}...")
            
#             next_button = find_next_button_enhanced(driver)
            
#             if not next_button:
#                 print("🛑 No Next button found - reached end of results")
#                 break
            
#             # Check if Next button is disabled (from your original code)
#             try:
#                 if not next_button.is_enabled():
#                     print("🛑 Next button is disabled - reached end of results")
#                     break
#             except:
#                 pass
            
#             # Attempt to click Next button
#             print(f"🖱️ Clicking Next button to go to page {page_number + 1}...")
            
#             click_success = click_next_button_safely(driver, next_button)
            
#             if not click_success:
#                 print("❌ Failed to click Next button - stopping pagination")
#                 break
            
#             # Wait for next page to load (from your original code)
#             print(f"⏳ Waiting for page {page_number + 1} to load...")
#             time.sleep(PAGE_LOAD_DELAY)
            
#             # Verify we moved to next page
#             try:
#                 # Wait for page to change
#                 WebDriverWait(driver, WAIT_TIMEOUT).until(
#                     lambda d: "page=" in d.current_url.lower() or len(d.find_elements(By.XPATH, "//div[@itemprop='itemListElement']")) > 0
#                 )
#                 print(f"✅ Successfully navigated to page {page_number + 1}")
#                 page_number += 1
                
#             except TimeoutException:
#                 print("⏰ Timeout waiting for next page - stopping pagination")
#                 break
#             except Exception as e:
#                 print(f"❌ Error verifying page change: {e}")
#                 break
        
#         print(f"\n🎉 Page navigation complete!")
#         print(f"📊 Total pages processed: {total_pages_processed}")
#         print(f"📄 Final page number: {page_number}")
        
#         return total_pages_processed
        
#     except Exception as e:
#         print(f"💥 Error during page navigation: {str(e)}")
#         return 0

# def main_step2_pagination():
#     """Main function for Step 2 - Complete page navigation test"""
#     st.set_page_config(page_title="Step 2: Complete Page Navigation", layout="wide")
#     st.title("Step 2: Complete Page Navigation with Stealth")
#     st.write("This will navigate through ALL pages of Airbnb listings using stealth mode and enhanced scrolling.")
    
#     # User input for location
#     search_location = st.text_input(
#         "Enter Search Location:",
#         value="Riyadh",
#         help="Enter a location to search on Airbnb"
#     )
    
#     # Test complete navigation
#     if st.button("🚀 Navigate All Pages"):
#         if not search_location.strip():
#             st.error("Please enter a search location.")
#             return
            
#         driver = None
#         try:
#             # Create stealth driver
#             driver = get_stealth_driver()
            
#             # Navigate through all pages
#             pages_processed = navigate_all_pages(driver, search_location)
            
#             if pages_processed > 0:
#                 st.success(f"✅ Complete navigation successful!")
#                 st.info(f"📊 Processed {pages_processed} pages of listings")
#                 st.info("🔍 Check your Chrome browser window to see the final page.")
#                 st.warning("⚠️ Browser will stay open - close it manually when done.")
                
#             else:
#                 st.error("❌ Page navigation failed.")
#                 if driver:
#                     driver.quit()
                
#         except Exception as e:
#             st.error(f"💥 Error occurred: {str(e)}")
#             st.code(traceback.format_exc())
#             if driver:
#                 driver.quit()

# if __name__ == "__main__":
#     main_step2_pagination()


#-----------------------------------------------4th Step inclusion-------------------------------------------------

# Step 3: Complete Data Extraction - Combines pagination with listing data extraction
# Creates DataFrame with: Title, Rating, Number of Reviews, URL, and Price

import time
import urllib.parse
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from bs4 import BeautifulSoup
import streamlit as st
import pandas as pd
import subprocess
import traceback
import re

# Constants from your original code
WAIT_TIMEOUT = 15
PAGE_LOAD_DELAY = 5

def get_stealth_driver():
    """Create a stealth WebDriver for Streamlit Cloud deployment."""
    try:
        print("🚀 Creating Stealth WebDriver for Streamlit Cloud...")
        
        chrome_options = Options()
        
        # For Streamlit Cloud - must be headless
        chrome_options.headless = True  # Changed to True for cloud deployment
        
        # Anti-detection options
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # Linux/Cloud specific options
        chrome_options.add_argument("--no-sandbox")  # Required for cloud
        chrome_options.add_argument("--disable-dev-shm-usage")  # Required for cloud
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--disable-infobars")
        chrome_options.add_argument("--disable-notifications")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-web-security")
        chrome_options.add_argument("--remote-debugging-port=9222")
        
        # Set binary location for Streamlit Cloud (Linux)
        chrome_options.binary_location = "/usr/bin/chromium"
        
        # User agent for Linux
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        # Service for Streamlit Cloud (Linux paths)
        service = Service(
            executable_path='/usr/bin/chromedriver',
            log_path='/tmp/chromedriver.log',
            service_args=['--verbose']
        )
        
        # Create driver
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        # Stealth scripts
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        driver.execute_script("Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]});")
        driver.execute_script("Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']});")
        
        print("✅ Stealth Driver created successfully for Streamlit Cloud")
        return driver
        
    except Exception as e:
        print(f"❌ Failed to initialize ChromeDriver: {str(e)}")
        st.error(f"❌ Failed to initialize ChromeDriver: {str(e)}")
        raise

def handle_initial_popups(driver):
    """Handle popups that appear on initial page load."""
    print("🔍 Handling initial popups...")
    
    try:
        time.sleep(2)
        popup_selectors = [
            ("//button[contains(text(), 'Got it')]", "Got it button"),
            ("//button[contains(text(), 'OK')]", "OK button"),
            ("//button[contains(text(), 'Accept')]", "Accept button"),
            ("//button[@aria-label='Close']", "Close button"),
        ]
        
        for selector, description in popup_selectors:
            try:
                elements = driver.find_elements(By.XPATH, selector)
                if elements:
                    for element in elements:
                        if element.is_displayed() and element.is_enabled():
                            # print(f"🖱️ Clicking {description}")
                            element.click()
                            time.sleep(1)
                            break
            except Exception as e:
                st.write(f"Error with {description}: {e}")
                
    except Exception as e:
        st.write(f"Error handling initial popups: {e}")

# Simple function to remove unwanted text from price

def clean_price_simple(raw_price_text):
    """
    Simple logic: Remove everything from beginning until after "Show price breakdown"
    """
    
    if not raw_price_text or raw_price_text == "N/A":
        return "N/A"
    
    # print(f"🔍 Original text: {raw_price_text}")
    
    try:
        # Check if "Show price breakdown" exists in the text
        if "Show price breakdown" in raw_price_text:
            # Find the position after "Show price breakdown"
            breakdown_pos = raw_price_text.find("Show price breakdown")
            after_breakdown_pos = breakdown_pos + len("Show price breakdown")
            
            # Get everything after "Show price breakdown"
            cleaned_text = raw_price_text[after_breakdown_pos:].strip()
            
            # print(f"✅ Cleaned text: {cleaned_text}")
            return cleaned_text
        
        else:
            # If no "Show price breakdown", return original text
            # print(f"ℹ️ No 'Show price breakdown' found, returning original")
            return raw_price_text.strip()
            
    except Exception as e:
        # print(f"❌ Error cleaning text: {e}")
        return raw_price_text


def extract_listing_data(element):
    """Extract data from a single listing element - from your original code logic."""
    try:
        # Extract URL (from your original code)
        url_meta = element.find('meta', {'itemprop': 'url'})
        listing_url = url_meta['content'].split('?')[0] if url_meta and url_meta.get('content') else "N/A"
        
        # Extract price per day (from your original code)
        # price_element = price_element = element.find('span', class_="a8jt5op atm_3f_idpfg4 atm_7h_hxbz6r atm_7i_ysn8ba atm_e2_t94yts atm_ks_zryt35 atm_l8_idpfg4 atm_vv_1q9ccgz atm_vy_t94yts a1fdgz01 atm_mk_stnw88 atm_tk_idpfg4 dir dir-ltr")
        # print(price_element)
        # price_per_day = price_element.text.strip() if price_element else "N/A"
        # print(price_per_day)
        
        price_element = price_element = element.find('div', class_="_w3xh25")
        # print(price_element)
        price_per_day = price_element.text.strip() if price_element else "N/A"
        # print(price_per_day)
        clean_price = clean_price_simple(price_per_day)
        # print(clean_price)

        # Extract total price (from your original code)
        total_price_element = element.find('div', class_="a8jt5op atm_3f_idpfg4 atm_7h_hxbz6r atm_7i_ysn8ba atm_e2_t94yts atm_ks_zryt35 atm_l8_idpfg4 atm_vv_1q9ccgz atm_vy_t94yts a1fdgz01 atm_mk_stnw88 atm_tk_idpfg4 dir dir-ltr")
        if total_price_element:
            total_price_span = total_price_element.find('span', {'aria-hidden': 'true'})
            total_price = total_price_span.text.strip() if total_price_span else "N/A"
        else:
            total_price = "N/A"
        
        # Extract listing title (from your original code)
        listing_card = element.find('div', attrs={'data-testid': 'listing-card-title'})
        listing_title = listing_card.text.strip() if listing_card else "N/A"
        
        # Extract description (from your original code)
        name_meta = element.find('meta', {'itemprop': 'name'})
        description = name_meta['content'] if name_meta else "N/A"
        
        # Extract rating (from your original code - fixed deprecated warning)
        rating_element = element.find('span', string=lambda t: t and 'average rating' in t)
        rating = rating_element.text.strip() if rating_element else "N/A"
        
        # Additional extraction: Number of reviews
        review_element = element.find('span', string=re.compile(r'\(\d+\)'))
        num_reviews = review_element.text.strip() if review_element else "N/A"
        
        listing_data = {
            'Title': description,                           # Main listing title
            'Property Type & Location': listing_title,      # From your original code
            'Rating': rating,                               # From your original code
            'Number of Reviews': num_reviews,               # Extracted from rating text
            'Listing-URL': listing_url,                     # From your original code
            'Price Per Day (USD)': clean_price,          # From your original code
            # '7-Day Stay Cost (USD)': total_price,          # From your original code
        }
        
        return listing_data
        
    except Exception as e:
        print(f"Error extracting listing data: {e}")
        return None

def scrape_all_listings_complete(search_location):
    """Complete scraping function - combines stealth navigation + pagination + data extraction."""
    driver = None
    try:
        # print(f"🚀 Starting complete scraping for: {search_location}")
        
        # Step 1: Create stealth driver
        driver = get_stealth_driver()
        
        # Step 2: Initial navigation
        # print("🏠 Going to Airbnb homepage first...")
        driver.get("https://www.airbnb.com")
        time.sleep(3)
        
        # Build search URL
        today = datetime.now()
        check_in_date = today + timedelta(days=1)
        check_out = check_in_date + timedelta(days=6)
        
        checkin_str = check_in_date.strftime('%Y-%m-%d')
        checkout_str = check_out.strftime('%Y-%m-%d')
        
        search_url = f"https://www.airbnb.com/s/{urllib.parse.quote(search_location)}/homes?checkin={checkin_str}&checkout={checkout_str}"
        # print(f"🔗 Search URL: {search_url}")
        
        # Navigate to search results
        # print("🔍 Navigating to search results...")
        driver.get(search_url)
        time.sleep(5)
        
        # Handle initial popups
        handle_initial_popups(driver)
        
        # Step 3: Extract data from all pages
        all_listings = []
        listings_per_page = []
        page_number = 1
        max_pages = 50
        
        while page_number <= max_pages:
            # print(f"\n📄 Extracting data from page {page_number}...")
            
            # Wait for content to load
            time.sleep(PAGE_LOAD_DELAY)
            
            # Get page source
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            
            # Find listing elements (from your original code)
            listing_elements = soup.find_all('div', {'itemprop': 'itemListElement'})
            # print(f"📊 Found {len(listing_elements)} listing elements on page {page_number}")
            
            if len(listing_elements) == 0:
                # print("⚠️ No listings found - end of results")
                break
            
            # Extract data from each listing
            page_listings = []
            for i, element in enumerate(listing_elements):
                # print(f"  Processing listing {i+1}/{len(listing_elements)}")
                
                listing_data = extract_listing_data(element)
                if listing_data:
                    page_listings.append(listing_data)
                    # print(f"  ✅ Extracted: {listing_data['Title'][:50]}...")
            
            listings_per_page.append(len(page_listings))
            all_listings.extend(page_listings)
            
            # print(f"✅ Page {page_number} complete: {len(page_listings)} listings extracted")
            # print(f"📊 Total listings so far: {len(all_listings)}")
            
            # Look for Next button
            next_button_selectors = [
                ("//a[@aria-label='Next']", "Next aria-label"),  # Your original selector
                ("//a[contains(@aria-label, 'Next')]", "Next aria-label (contains)"),
                ("//button[contains(@aria-label, 'Next')]", "Next button"),
                ("//a[contains(text(), 'Next')]", "Next text"),
            ]
            
            next_button = None
            for selector, description in next_button_selectors:
                try:
                    elements = driver.find_elements(By.XPATH, selector)
                    if elements:
                        for element in elements:
                            if element.is_displayed() and element.is_enabled():
                                next_button = element
                                # print(f"✅ Found Next button: {description}")
                                break
                        if next_button:
                            break
                except Exception as e:
                    st.error(f"The error is {e}.")
                    continue
            
            if not next_button:
                # print("🛑 No Next button found - reached end of results")
                break
            
            # Check if Next button is disabled (from your original code)
            if not next_button.is_enabled():
                # print("🛑 Next button is disabled - reached end of results")
                break
            
            # Click Next button with enhanced strategies
            # print(f"🖱️ Clicking Next button to go to page {page_number + 1}...")
            
            try:
                # Scroll button into view
                driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", next_button)
                time.sleep(1)
                
                # Try to click
                next_button.click()
                # print(f"✅ Successfully clicked Next button")
                
                # Wait for next page to load (from your original code)
                time.sleep(PAGE_LOAD_DELAY)
                page_number += 1
                
            except Exception as e:
                # print(f"❌ Failed to click Next button: {e}")
                # print("🛑 Stopping pagination")
                break
        
        # print(f"\n🎉 Scraping complete!")
        # print(f"📊 Total pages processed: {page_number - 1}")
        # print(f"📊 Total listings extracted: {len(all_listings)}")
        
        return all_listings, listings_per_page
        
    except Exception as e:
        print(f"💥 Error during complete scraping: {str(e)}")
        return [], []
    finally:
        if driver:
            print("🧹 Closing browser...")
            driver.quit()

def main_step3_complete():
    """Main function for Step 3 - Complete scraping with DataFrame creation"""
    st.set_page_config(page_title="Step 3: Complete Airbnb Scraping", layout="wide")
    # st.title("Step 3: Complete Airbnb Scraping with Data Extraction")
    # st.write("This will scrape ALL pages and create a DataFrame with Title, Rating, Reviews, URL, and Price.")
    
    # User input for location
    search_location = st.text_input(
        "Enter Search Location:",
        value="Riyadh",
        help="Enter a location to search on Airbnb"
    )
    
    # Complete scraping
    if st.button("🚀 Complete Scraping"):
        if not search_location.strip():
            st.error("Please enter a search location.")
            return
            
        with st.spinner("Extracting all listings..."):
            try:
                # Run complete scraping
                listings, listings_per_page = scrape_all_listings_complete(search_location)
                
                if listings:
                    total_listings = len(listings)
                    st.success(f"🎉 Scraping complete! Total listings found: {total_listings}")
                    
                    # Create tabs for results (from your original code)
                    tab1, tab2 = st.tabs(["Listings Summary", "Raw Data"])
                    
                    with tab1:
                        st.write("### Listings Per Page:")
                        for i, count in enumerate(listings_per_page, start=1):
                            st.write(f"Page {i}: {count} listings")
                        st.write(f"### Total Listings: {total_listings}")
                        
                        # Show sample data
                        if listings:
                            st.write("### Sample Listing:")
                            sample = listings[0]
                            for key, value in sample.items():
                                st.write(f"**{key}:** {value}")
                    
                    with tab2:
                        st.write("### Complete DataFrame")
                        # Create DataFrame (from your original code)
                        df = pd.DataFrame(listings)
                        df.index.name = "S.No."
                        st.dataframe(df)
                        
                        # CSV Download (from your original code)
                        csv = df.to_csv(index=False, encoding='utf-8-sig')
                        st.download_button(
                            label="Download Listings as CSV",
                            data=csv,
                            file_name=f"airbnb_listings_{search_location}.csv",
                            mime="text/csv"
                        )
                        
                        # Show DataFrame info
                        st.write(f"**Shape:** {df.shape[0]} rows × {df.shape[1]} columns")
                        st.write("**Columns:**")
                        for col in df.columns:
                            non_na_count = df[col].count()
                            st.write(f"- {col}: {non_na_count}/{len(df)} values")
                
                else:
                    st.error("❌ No listings found. Check the console for debugging info.")
                    
            except Exception as e:
                st.error(f"💥 Error occurred: {str(e)}")
                st.code(traceback.format_exc())

if __name__ == "__main__":
    main_step3_complete()