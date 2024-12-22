from selenium import webdriver
from selenium.webdriver.chrome.service import Service
import os

options = webdriver.ChromeOptions()
options.add_argument("--disable-webrtc")
options.add_argument("--disable-logging")
options.add_argument("--log-level=3")  # Reduces log verbosity

service = Service(log_path=os.devnull)  # Redirects logs to null
driver = webdriver.Chrome(service=service, options=options)

try:
    driver.get("https://www.example.com")
    print("Browser launched successfully.")
    input("Press Enter to exit...")
finally:
    driver.quit()
