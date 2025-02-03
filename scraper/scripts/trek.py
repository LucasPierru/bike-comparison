from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
import time

# Set up Selenium
options = webdriver.ChromeOptions()
options.add_argument("--headless")  # Run without opening a browser
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

def scrape_bikes_selenium(url):
    driver.get(url)
    WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CLASS_NAME, "product-list__item")))

    bikes = []
    bike_links = []

    bike_elements = driver.find_elements(By.CLASS_NAME, "product-list__item")  # Adjust selector

    for bike in bike_elements:
      try:
          elem = bike.find_element(By.TAG_NAME, "a")
          link = elem.get_attribute("href")
          bike_links.append(link)
      except StaleElementReferenceException:
          continue  # Skip stale elements

    for link in bike_links:
       try:
          driver.get(link)
          time.sleep(3)

          header = driver.find_element(By.CLASS_NAME, "buying-zone__header")
          name = header.find_element(By.CLASS_NAME, "buying-zone__title").text

          image = driver.find_element(By.CLASS_NAME, "swiper-lazy").get_attribute("src")
          if image is not None:
            imageUrl = image.split("%20")[0]

          footer = driver.find_element(By.CLASS_NAME, "buying-zone__footer")

          priceSpan = footer.find_element(By.TAG_NAME, "span")
          currentPrice = priceSpan.find_element(By.CLASS_NAME, "actual-price").text

          description = footer.find_element(By.TAG_NAME, "p").text
          color_elements = driver.find_elements(By.CLASS_NAME, "pdl-swatch-container")
          colors = []

          for color in color_elements:
            col = color.find_element(By.TAG_NAME, "label")
            colors.append(col.get_attribute("title"))

          newBike = {"name": name, "currentPrice": currentPrice, "link": link, "imageUrl": imageUrl, "source": url, "description": description}

          print(f"bike: {newBike}")
          bikes.append(newBike)

       except NoSuchElementException as e:
        print(f"Skipping a bike due to error {link} {e}")

    """ collection.insert_many(bikes) """
    print(f"Scraped {len(bikes)} bikes from {url}")
    print(bikes[:5])

# Example usage
scrape_bikes_selenium("https://www.trekbikes.com/ca/en_CA/bikes/road-bikes/c/B200/?pageSize=72&q=%3Arelevance%3AfacetFrameset%3AfacetFrameset2&sort=relevance#")
driver.quit()