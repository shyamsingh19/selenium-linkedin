import logging
import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import (
    NoSuchElementException,
    TimeoutException,
    WebDriverException,
)
from urllib.parse import urlparse, parse_qs

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Logging Configuration
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

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
driver = webdriver.Chrome(service=service, options=chrome_options)


class PageManager:
    def __init__(self, driver):
        self.driver = driver

    def open_link(self, link):
        """Opens the given link in the browser."""
        logging.info(f"Opening the page: {link}")
        self.driver.get(link)
        self.driver.maximize_window()

    def scroll_incrementally(self, driver, max_scroll_attempts=10):
        """Scrolls the page incrementally to locate the 'Next' button."""
        for attempt in range(max_scroll_attempts):
            try:
                next_button = driver.find_element(
                    By.XPATH,
                    "//button[contains(@class, 'artdeco-pagination__button--next')]",
                )
                if next_button.is_displayed():
                    logging.info("Found the 'Next' button during scrolling.")
                    return next_button
            except NoSuchElementException:
                pass

            driver.execute_script("window.scrollBy(0, 500);")  # Scroll down by 500px
            time.sleep(1)  # Wait for elements to load
        logging.error("Failed to locate 'Next' button after scrolling.")
        return None

    def click_next(self, driver):
        """Attempts to click the 'Next' button with scrolling and retries."""
        retries = 3
        for attempt in range(1, retries + 1):
            try:
                logging.info(f"Attempt {attempt} to click the 'Next' button.")

                # Perform incremental scrolling to locate the button
                next_button = self.scroll_incrementally(driver)

                if next_button:
                    # Scroll to the button and click
                    driver.execute_script(
                        "arguments[0].scrollIntoView({block: 'center'});", next_button
                    )
                    driver.execute_script("arguments[0].click();", next_button)
                    time.sleep(5)  # Wait for the next page to load
                    logging.info("Successfully clicked the 'Next' button.")
                    return True
                else:
                    logging.warning("Button not found or not visible after scrolling.")

            except TimeoutException:
                logging.error("Timeout while waiting for the 'Next' button.")
            except Exception as e:
                logging.error(f"Unexpected error during attempt {attempt}: {e}")

            # Retry logic: refresh the page
            logging.info("Retrying the click operation...")
            driver.refresh()
            time.sleep(5)

        logging.error("Failed to click the 'Next' button after multiple attempts.")
        return False

    def get_current_page_number_from_url(self, driver):
        """Extracts the current page number from the URL of the LinkedIn search page."""
        try:
            # Get the current URL of the page
            current_url = driver.current_url

            # Parse the URL and extract the page number from query parameters
            parsed_url = urlparse(current_url)
            query_params = parse_qs(parsed_url.query)
            print(f"{query_params = }")

            # Look for the 'page' parameter in the URL query string
            page_number = query_params.get("page", [1])[0]

            if page_number:
                logging.info(f"Current page number extracted from URL: {page_number}")
                return int(page_number)
            else:
                logging.warning("Page number not found in the URL.")
                return 1  # If no page parameter, assume it's the first page
        except Exception as e:
            logging.error(f"Error extracting page number from URL: {e}")
            return None


def add_data_to_sheet(num, link):
    """Shows basic usage of the Sheets API.
    Appends data to a sample spreadsheet.
    """

    # Update the scope to allow writing to the spreadsheet.
    SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

    # The ID and range of the sample spreadsheet.
    SAMPLE_SPREADSHEET_ID = "1-pGW-36Oj28X0dyTwm1ZoeHhQpuP1tSamcdCg25Y2MI"
    SAMPLE_RANGE_NAME = "Sheet4!B2:E"  # Adjust sheet name and range as needed

    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    try:
        service = build("sheets", "v4", credentials=creds)

        # Prepare the data to append
        values_to_append = [
            [f"Id_{num}", link]  # Example data to append (replace with your own)
        ]

        # Call the Sheets API to append the data
        request = (
            service.spreadsheets()
            .values()
            .append(
                spreadsheetId=SAMPLE_SPREADSHEET_ID,
                range=SAMPLE_RANGE_NAME,
                valueInputOption="RAW",  # Use "RAW" or "USER_ENTERED" based on your preference
                insertDataOption="INSERT_ROWS",  # Insert new rows
                body={"values": values_to_append},
            )
        )
        response = request.execute()

        logging.info(f"Data appended: {response}")

    except HttpError as err:
        logging.error(f"An error occurred: {err}")


if __name__ == "__main__":
    try:
        # Open LinkedIn Search Page
        link = "https://www.linkedin.com/search/results/people/?geoUrn=%5B%22115918471%22%2C%22102106636%22%2C%2290009626%22%2C%22106187582%22%2C%22104869687%22%2C%22106442238%22%5D&keywords=SDE&network=%5B%22S%22%2C%22O%22%5D&origin=FACETED_SEARCH&sid=(0B)"
        page_manage_obj = PageManager(driver)
        page_manage_obj.open_link(link)

        # current_page = page_manage_obj.get_current_page_number_from_url(driver)
        # if current_page:
        #     logging.info(f"Currently on page {current_page}")

        # # Attempt to click the 'Next' button
        # if not page_manage_obj.click_next(driver):
        #     logging.error("Unable to navigate to the next page.")

        xpath_selector = "//div[contains(@class, 'faUjwyjcfeuMLUteNCRttWCgFNPyDBuduA')]//a[@href and contains(@href, '/in/')]"
        cur_page = page_manage_obj.get_current_page_number_from_url(driver)
        while cur_page <100:
            cur_page = page_manage_obj.get_current_page_number_from_url(driver)

            elements = driver.find_elements(By.XPATH, xpath_selector)
            elements = list(set(elements))
            logging.info(f"Found {len(elements)} elements matching the selector.")
            links_to_open = []
            for element in elements:
                # if not is_mutual_connection(element):
                href = element.get_attribute("href")
                links_to_open.append(href)
            i = 1
            for link in links_to_open:
                id = f"{cur_page}_{i}"
                add_data_to_sheet(id, link)
                i += 1

            page_manage_obj.click_next(driver)
    except WebDriverException as e:
        logging.error(f"WebDriverException occurred: {e}")
    finally:
        if "driver" in locals():
            driver.quit()


"""

The button element we are trying to press:


<button aria-label="Next" id="ember157" class="artdeco-button artdeco-button--muted artdeco-button--icon-right artdeco-button--1 artdeco-button--tertiary ember-view artdeco-pagination__button artdeco-pagination__button--next" type="button">        <svg role="none" aria-hidden="true" class="artdeco-button__icon " xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16" data-supported-dps="16x16" data-test-icon="chevron-right-small" data-rtl="true">
<!---->    
    <use href="#chevron-right-small" width="16" height="16"></use>
</svg>


<span class="artdeco-button__text">
    Next
</span></button>
"""
