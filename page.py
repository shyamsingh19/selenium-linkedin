import logging
import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException, WebDriverException
from main import add_data_to_sheet

# Logging Configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Paths and ChromeDriver Setup
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CHROMEDRIVER_PATH = os.path.join(SCRIPT_DIR, "chromedriver.exe")
USER_DATA_DIR = "C:\\Users\\shyam\\AppData\\Local\\Google\\Chrome\\User Data"

chrome_options = Options()
chrome_options.add_argument(f"--user-data-dir={USER_DATA_DIR}")
chrome_options.add_argument("--profile-directory=Profile 3")
chrome_options.add_argument("--log-level=3")  # Reduce verbosity
chrome_options.add_argument("--disable-webrtc")  # Suppress WebRTC logs
chrome_options.add_argument("--disable-blink-features=AutomationControlled")
chrome_options.add_argument("--disable-extensions")

service = Service(executable_path=CHROMEDRIVER_PATH)

try:
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.maximize_window()

    # Open LinkedIn Search Page
    link = "https://www.linkedin.com/search/results/people/?geoUrn=%5B%22115918471%22%2C%22102106636%22%2C%2290009626%22%2C%22106187582%22%2C%22104869687%22%2C%22106442238%22%5D&keywords=SDE&network=%5B%22S%22%2C%22O%22%5D&origin=FACETED_SEARCH&sid=(0B)"
    logging.info(f"Opening the page: {link}")
    driver.get(link)

    def extract_links():
        """Extracts profile links from the current page."""
        # xpath_selector = "//div[contains(@class, 'entity-result__content')]//a[@href and contains(@href, '/in/')]"
        xpath_selector = "//div[contains(@class, 'faUjwyjcfeuMLUteNCRttWCgFNPyDBuduA')]//a[@href and contains(@href, '/in/')]"
        try:
            elements = WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.XPATH, xpath_selector))
            )
            links = [element.get_attribute("href") for element in elements if element.get_attribute("href")]
            return links
        except TimeoutException:
            logging.error("Timeout while waiting for links to load.")
            return []

    def click_next():
        """Clicks the 'Next' button to navigate pages."""
        try:
            # Check if the "..." button exists, indicating more pages
            next_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//li[contains(@class, 'artdeco-pagination__indicator--number') and contains(., '…')]"))
            )
            driver.execute_script("arguments[0].scrollIntoView(true);", next_button)
            next_button.click()
            time.sleep(1)  # Give the page some time to load
            logging.info("Clicked '...' button for more pages.")
            return True
        except (NoSuchElementException, TimeoutException):
            # If "..." not found, look for the actual next button
            try:
                next_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[@aria-label='Next']"))
                )
                driver.execute_script("arguments[0].scrollIntoView(true);", next_button)
                next_button.click()
                time.sleep(1)  # Give the page some time to load
                logging.info("Clicked 'Next' button.")
                return True
            except (NoSuchElementException, TimeoutException):
                logging.error("Next button not found or not clickable. End of pagination.")
                return False


    current_page = 1
    while current_page <= 100:
        logging.info(f"Processing page {current_page}")

        # Extract profile links
        links_to_open = extract_links()
        logging.info(f"Found {len(links_to_open)} links on page {current_page}")

        for index, link in enumerate(links_to_open, start=1):
            logging.info(f"[{current_page}_{index}] Processing link: {link}")
            # Here you could call `
            add_data_to_sheet(f"{current_page}_{index}",  link)

        if not click_next():
            break  # Stop if "Next" button is unavailable

        current_page += 1

    logging.info("Finished processing all pages.")

except WebDriverException as e:
    logging.error(f"WebDriverException occurred: {e}")
finally:
    if 'driver' in locals():
        driver.quit()
