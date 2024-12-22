import logging
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time
import os

# Set up logging configuration
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

# Path to the current script directory
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# Path to your ChromeDriver executable
CHROMEDRIVER_PATH = os.path.join(SCRIPT_DIR, "chromedriver.exe")

# Path to your Chrome user data directory (ensure it's correct for your system)
USER_DATA_DIR = "C:\\Users\\shyam\\AppData\\Local\\Google\\Chrome\\User Data"

# Set up Chrome options for speed
chrome_options = Options()
chrome_options.add_argument(f"--user-data-dir={USER_DATA_DIR}")
chrome_options.add_argument("--profile-directory=Profile 3")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--remote-debugging-port=9222")
chrome_options.add_argument("--disable-gpu")  # Disable GPU for faster processing
chrome_options.add_argument("--disable-extensions")  # Disable extensions

# Set up WebDriver with Chrome options
service = Service(executable_path=CHROMEDRIVER_PATH)
driver = webdriver.Chrome(service=service, options=chrome_options)
driver.maximize_window()  # Maximize the window

# Open the desired page
link = "https://www.google.com"  # Add https:// to the link
logging.info(f"Opening the page: {link}")
driver.get(link)
time.sleep(5)

# Close the browser
logging.info("Closing the browser.")
driver.quit()
