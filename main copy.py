import logging
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from concurrent.futures import ThreadPoolExecutor
import os
import json
import csv

import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Set up logging configuration (set to DEBUG for more detailed logs)
logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')

# Path to the current script directory
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# Path to your ChromeDriver executable
CHROMEDRIVER_PATH = os.path.join(SCRIPT_DIR, "chromedriver.exe")

# Path to your Chrome user data directory
USER_DATA_DIR = "C:\\Users\\shyam\\AppData\\Local\\Google\\Chrome\\User Data"

# Set up Chrome options for speed
chrome_options = Options()
chrome_options.add_argument(f"--user-data-dir={USER_DATA_DIR}")
chrome_options.add_argument("--profile-directory=Profile 3")
# chrome_options.add_argument("--no-sandbox")
# chrome_options.add_argument("--disable-webgl")
# chrome_options.add_argument("--disable-dev-shm-usage")
# chrome_options.add_argument("--remote-debugging-port=9222")
# chrome_options.add_argument("--headless")  # Uncomment for headless mode if needed
# chrome_options.add_argument("--disable-gpu")  # Disable GPU for faster processing
# chrome_options.add_argument("--disable-extensions")  # Disable extensions
# chrome_options.add_argument("--disable-webrtc")


# Set up WebDriver with Chrome options
service = Service(executable_path=CHROMEDRIVER_PATH)
driver = webdriver.Chrome(service=service, options=chrome_options)

driver.maximize_window()  # Maximize the window

# Open the desired page
link = "https://www.linkedin.com/search/results/people/?geoUrn=%5B%22115918471%22%2C%22102106636%22%2C%2290009626%22%2C%22106187582%22%2C%22104869687%22%2C%22106442238%22%5D&keywords=SDE&network=%5B%22S%22%2C%22O%22%5D&origin=FACETED_SEARCH&sid=(0B)"
logging.info(f"Opening the page: {link}")
driver.get(link)

# XPath to locate the 'a' tag with the profile link inside each li element
# xpath_selector = "//li[contains(@class, 'hfrnpHqiFIFjzRKUPdWXOHmVUInUMZAcTFUI')]//a[@href and contains(@href, '/in/')]"
xpath_selector = "//div[contains(@class, 'faUjwyjcfeuMLUteNCRttWCgFNPyDBuduA')]//a[@href and contains(@href, '/in/')]"
# xpath_selector = "//li[contains(@class, 'faUjwyjcfeuMLUteNCRttWCgFNPyDBuduA')]//a[@href and contains(@href, '/in/')]"
logging.info(f"Looking for elements with XPath selector: {xpath_selector}")

# Set to keep track of opened links
opened_links = set()

# Function to check if the element's parent contains the mutual connection
def is_mutual_connection(element):
    try:
        # Check if the parent div has the class 'entity-result__insights' which indicates mutual connection
        parent_div = element.find_element(By.XPATH, ".//ancestor::div[contains(@class, 'entity-result__insights')]")
        mutual_text = parent_div.find_element(By.XPATH, ".//span[contains(text(), 'is a mutual connection')]")
        return True if mutual_text else False
    except Exception:
        return False

# Function to open a link in a new tab (ensures unique tabs are opened)
def open_link(link_to_open):
    try:
        # Skip if the link has already been opened
        if link_to_open in opened_links:
            logging.debug(f"Link already opened: {link_to_open}")
            return

        # Open the link in a new tab using JavaScript (no wait for load)
        driver.execute_script(f"window.open('{link_to_open}', '_blank');")
        opened_links.add(link_to_open)
        logging.debug(f"Opened the link: {link_to_open}")
    
    except Exception as e:
        logging.error(f"Error opening link: {link_to_open}, Error: {e}")




def add_data_to_sheet(num, link):
    """Shows basic usage of the Sheets API.
    Appends data to a sample spreadsheet.
    """

    # Update the scope to allow writing to the spreadsheet.
    SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

    # The ID and range of the sample spreadsheet.
    SAMPLE_SPREADSHEET_ID = "1-pGW-36Oj28X0dyTwm1ZoeHhQpuP1tSamcdCg25Y2MI"
    SAMPLE_RANGE_NAME = "Sheet4!A2:E"  # Adjust sheet name and range as needed
    
    
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
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    try:
        service = build("sheets", "v4", credentials=creds)

        # Prepare the data to append
        values_to_append = [
            [f"link_{num}", link]  # Example data to append (replace with your own)
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



# Find all matching elements and open links in parallel
try:
    elements = driver.find_elements(By.XPATH, xpath_selector)
    elements = list(set(elements))
    logging.info(f"Found {len(elements)} elements matching the selector.")
    # Filter out mutual connections
    links_to_open = []
    for element in elements:
        # if not is_mutual_connection(element):
        if True:
            href = element.get_attribute("href")
            links_to_open.append(href)
    
    logging.debug(f"Links to open (excluding mutual connections): {links_to_open}")
    
    i=1
    for link in links_to_open:
        add_data_to_sheet(i, link)
        i+=1
        
    # # Optionally, print the links and save them to a JSON file
    # with open("sample.json", "w") as f:
    #     for link in links_to_open:
    #         f.write(json.dumps({"link": link}) + "\n")
            
    # with open("sample.csv", "a", newline="") as f:
    #     writer = csv.writer(f)

    #     # Write the data as rows
    #     for link in links_to_open:
    #         writer.writerow([link])
    

    
    logging.info("Closing the browser.")
    driver.quit()
    
    # Create a thread pool to open links in parallel
    with ThreadPoolExecutor(max_workers=10) as executor:  # You can adjust max_workers for more parallelism
        # Submit tasks to open links in parallel
        executor.map(open_link, links_to_open)

except Exception as e:
    logging.error(f"Error locating elements: {e}")

# Capture browser console logs after actions
# browser_logs = driver.get_log('browser')  # This will fetch the logs
# for entry in browser_logs:
#     logging.debug(f"Browser log: {entry}")

# Wait for a while before closing the browser (so you can see the result)
input("Press Enter to close the browser...")

# Close the browser
logging.info("Closing the browser.")
driver.quit()
