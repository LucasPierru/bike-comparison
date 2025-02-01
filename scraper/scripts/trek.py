from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
import time

# Set up Selenium
options = webdriver.ChromeOptions()
options.add_argument("--headless")  # Run without opening a browser
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

def scrape_bikes_selenium(url):
    driver.get(url)
    time.sleep(3)  # Wait for JS to load

    bikes = []
    bike_elements = driver.find_elements(By.CLASS_NAME, "product-list__item")  # Adjust selector

    for item in bike_elements:
        try: 
          elem = item.find_element(By.TAG_NAME, "a")
          link = elem.get_attribute("href")
          body = elem.find_element(By.CLASS_NAME, "product-card-item__body")
          image = item.find_element(By.TAG_NAME, "img").get_attribute("src")
          name = body.find_element(By.CLASS_NAME, "product-card-item__title").text
          price = body.find_element(By.CLASS_NAME, "product-card-item__price").text 

          bikes.append({"name": name, "price": price, "link": link, "image": image, "source": url})
        except NoSuchElementException:
           print("Element not found, skipping...")

    """ collection.insert_many(bikes) """
    print(f"Scraped {len(bikes)} bikes from {url}")

# Example usage
scrape_bikes_selenium("https://www.trekbikes.com/ca/en_CA/bikes/road-bikes/c/B200/?pageSize=72&q=%3Arelevance%3AfacetFrameset%3AfacetFrameset2&sort=relevance#")
driver.quit()