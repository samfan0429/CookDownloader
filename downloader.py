import os
import time
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# 🔹 Set the path to manually downloaded ChromeDriver (CHANGE THIS!) ################################
CHROMEDRIVER_PATH = "C:/Users/sgpark/Desktop/ani/PersonalWork/chromedriver-win64/chromedriver.exe"

# 🔹 Set Chrome binary location (CHANGE THIS IF DIFFERENT) ####################################
CHROME_BINARY_PATH = "C:/Program Files/Google/Chrome/Application/chrome.exe"

# 🔹 Target website to scrape images from (CHANGE THIS AND download_folder!) #############################
URL = "http://154.219.3.228/detail/30320"
download_folder = "bamboo14"

# 🔹 Setup Selenium with Chrome
options = Options()
options.binary_location = CHROME_BINARY_PATH
options.add_argument("--headless")  # Optional: Run in headless mode
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")

# Initialize WebDriver
service = Service(CHROMEDRIVER_PATH)
driver = webdriver.Chrome(service=service, options=options)

try:
    # Open the webpage
    driver.get(URL)

    # 🔹 Step 1: Wait for first "lazy-img-wrap" div to load
    timeout = 60  # Wait up to 60 seconds
    WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located((By.CLASS_NAME, "lazy-img-wrap"))
    )

    # 🔹 Step 2: Scroll until no more images are loading (to load all images)
    last_height = driver.execute_script("return document.body.scrollHeight")
    for _ in range(50):  # Scroll multiple times to load more images
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(5)  # Allow time for new images to load
        new_height = driver.execute_script("return document.body.scrollHeight")
        last_height = new_height

    # 🔹 Step 3: Extract image URLs and sort by last part of the URL
    image_urls = []  # Use list to preserve order

    # Find all divs with class "lazy-img-wrap"
    divs = driver.find_elements(By.CLASS_NAME, "lazy-img-wrap")

    for div in divs:
        try:
            img = div.find_element(By.TAG_NAME, "img")  # Get the <img> inside the div
            img_url = img.get_attribute("src")
            if img_url and img_url not in image_urls:  # Avoid duplicates
                image_urls.append(img_url)
        except:
            pass  # Skip if an image is missing

    # 🔹 Step 4: Sort image URLs by the last part of the URL
    def get_last_part(url):
        return url.split("/")[-1]  # Extract the last part of the URL

    image_urls.sort(key=get_last_part)

    # 🔹 Step 5: Ensure the download directory exists
    os.makedirs(download_folder, exist_ok=True)

    # 🔹 Step 6: Download images in sorted order
    for idx, img_url in enumerate(image_urls):
        try:
            response = requests.get(img_url, stream=True)
            if response.status_code == 200:
                ext = img_url.split(".")[-1].split("?")[0]  # Extract file extension
                if ext not in ["jpg", "png", "jpeg", "gif", "webp"]:
                    ext = "png"  # Default to PNG if unknown
                img_path = os.path.join(download_folder, f"image_{idx+1:03d}.{ext}")  # Ordered filenames
                with open(img_path, "wb") as file:
                    for chunk in response.iter_content(1024):
                        file.write(chunk)
                print(f"✅ Downloaded: {img_path}")
        except Exception as e:
            print(f"❌ Failed to download {img_url}: {e}")

finally:
    # Close Selenium
    driver.quit()

print("\n🎉 Image downloading completed in order!")
