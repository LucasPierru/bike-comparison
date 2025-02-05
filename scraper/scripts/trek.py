from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
import time
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from toolbox.toolbox import replace_query_param, previous_and_next, parse_sizes

# Set up Selenium
options = webdriver.ChromeOptions()
options.add_argument("--headless")  # Run without opening a browser
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

class Trek:
  bike_links = []
  bikes = []

  def __init__(self, url):
    self.url = url

  def get_bike_links(self):
    driver.get(self.url)
    WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CLASS_NAME, "product-list__item")))

    bike_elements = driver.find_elements(By.CLASS_NAME, "product-list__item")  # Adjust selector

    for bike in bike_elements:
      try:
          elem = bike.find_element(By.TAG_NAME, "a")
          color_list = elem.find_element(By.CLASS_NAME, "pdl-swatches")
          color_elements = color_list.find_elements(By.CLASS_NAME, "pdl-swatch-container")
          link = elem.get_attribute("href")

          for color in color_elements:
            col = color.find_element(By.TAG_NAME, "label").get_attribute("title")
            base_url = replace_query_param(link, "colorCode", "")
            bike_link = {
              "base_url": base_url,
              "color": col
            }
            self.bike_links.append(bike_link)

      except StaleElementReferenceException:
          continue  # Skip stale elements
      except NoSuchElementException:
          print(f"Skipping a bike due to error")

  def scrape_bikes_selenium(self):
    self.get_bike_links()

    for previous, link, nxt in previous_and_next(self.bike_links):
      base_url = f"{link["base_url"]}{link["color"]}"
      if previous is not None:
        previous_url = previous["base_url"]
      else:
        previous_url = ""

      if nxt is not None:
        next_url = nxt["base_url"]
      else:
        next_url = ""
    
      try:
        driver.get(base_url)
        time.sleep(3)

        if link["base_url"] != previous_url:
          variations = []
          components = []
          header = driver.find_element(By.CLASS_NAME, "buying-zone__header")
          name = header.find_element(By.CLASS_NAME, "buying-zone__title").text

          image = driver.find_element(By.CLASS_NAME, "swiper-lazy").get_attribute("src")
          if image is not None:
            imageUrl = image.split("%20")[0]

          footer = driver.find_element(By.CLASS_NAME, "buying-zone__footer")

          priceSpan = footer.find_element(By.TAG_NAME, "span")
          currentPrice = priceSpan.find_element(By.CLASS_NAME, "actual-price").text

          description = footer.find_element(By.TAG_NAME, "p").text
          specs_container = driver.find_element(By.ID, "trekRoadProductSpecificationsComponentBOM")
          specs_items = specs_container.find_elements(By.TAG_NAME, "tr")

          for spec in specs_items:
            try :
              spec_type = spec.find_element(By.TAG_NAME, "th").get_attribute("innerText").strip().replace("*", "")
              spec_value = spec.find_element(By.TAG_NAME, "td").get_attribute("innerText").strip()

              if "Size" in spec_value: 
                spec_value = parse_sizes(spec_value)

              newSpec = {"type": spec_type, "value": spec_value}
              components.append(newSpec)
            except NoSuchElementException:
              spec_value = spec.find_element(By.TAG_NAME, "td").get_attribute("innerText").strip()

              if "Size" in spec_value: 
                spec_value = parse_sizes(spec_value)

              newSpec = {"type": spec_type, "value": spec_value}
              components.append(newSpec)
        
        size_elements = driver.find_elements(By.CLASS_NAME, "product-attribute-btn")
        sizes = []
        color = link["color"]

        for size in size_elements:
          sizes.append(size.find_element(By.TAG_NAME, "span").text)

        variations.append({"color": color, "sizes": sizes})
        
        if link["base_url"] != next_url:
          newBike = {"name": name, "currentPrice": currentPrice, "link": link, "imageUrl": imageUrl, "source": self.url, "description": description, "variations": variations, "components": components}

          print(f"bike: {newBike}")
          self.bikes.append(newBike)

      except NoSuchElementException as e:
        print(f"Skipping a bike due to error {link} {e}")

    """ collection.insert_many(bikes) """
    print(f"Scraped {len(self.bikes)} bikes from {self.url}")
    print(self.bikes[:5])

# Example usage
trek = Trek("https://www.trekbikes.com/ca/en_CA/bikes/road-bikes/c/B200/?pageSize=72&q=%3Arelevance%3AfacetFrameset%3AfacetFrameset2&sort=relevance#")
trek.scrape_bikes_selenium()
driver.quit()