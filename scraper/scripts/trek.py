from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException, TimeoutException
from playwright.sync_api import sync_playwright
import time
import sys
import os
from datetime import datetime
from pymongo import UpdateOne

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from models.bike import Bike
from toolbox.toolbox import replace_query_param, previous_and_next, parse_sizes, extract_price, find_brand_in_component
from db import get_database
# Set up Selenium
options = webdriver.ChromeOptions()
options.add_argument("--headless")  # Run without opening a browser
options.add_argument("--no-sandbox")  # Required for Docker
options.add_argument("--disable-dev-shm-usage")  # Avoid shared memory issues
options.add_argument("--disable-gpu")  # Disable GPU acceleration
options.add_argument("--remote-debugging-port=9222")  # Useful for debugging
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
db = get_database()
bike_collection = db["bikes"]
brand_collection = db["brands"]
component_collection = db["components"]
bike_component_collection = db["bikecomponents"]

class Trek:
  bike_links = []
  bikes = []
  result_count = 1
  bike_count = 0
  brand_id = ""
  brands = []

  def __init__(self, url, page=0):
    self.url = url
    self.page = page

  def get_brand(self, name):
    existing_brand = brand_collection.find_one({"name": name})
    self.brand_id = existing_brand["_id"]

  def get_brands(self):
    brands = brand_collection.find()
    self.brands = brands.to_list()

  def post_brand(self, brand):
    existing_brand = brand_collection.find_one({"name": brand["name"]})

    if existing_brand:
        self.brand_id = existing_brand["_id"]
        print(f"Brand already exists in DB: {brand['name']}")
    else:
        new_brand = brand_collection.insert_one(brand)
        self.brand_id = new_brand.inserted_id
        print(f"Brand inserted: {brand['name']}")
  
  def post_components(self, components):
    operations=[]
    for component in components:
      operations.append(UpdateOne({"name": component["name"]}, {"$set": component}, upsert=True))
    component_collection.bulk_write(operations)
    component_names = [c["name"] for c in components]
    component_docs = component_collection.find({"name": {"$in": component_names}}, {"_id": 1})
    component_ids = [doc["_id"] for doc in component_docs]
    
    return component_ids

  def post_bike_components(self, bike_id, component_ids):
    operations=[]
    for component_id in component_ids:
      operations.append(UpdateOne(
        {"bike": bike_id, "component": component_id}, 
        {"$set": {
            "createdAt": datetime.now(), 
            "updatedAt": datetime.now(), 
            "bike": bike_id, 
            "component": component_id,
          }
        }, 
        upsert=True)
      )
    bike_component_collection.bulk_write(operations)

  def post_bike(self, bike):
    existing_bike = bike_collection.find_one({"source": bike["source"]})

    if existing_bike:
        print(f"Bike already exists in DB: {bike['name']}, updating")
        bike.pop("createdAt", None) 
        bike_collection.update_one({"_id": existing_bike["_id"]}, {"$set": bike})
        return existing_bike["_id"]
    else:
        new_bike = bike_collection.insert_one(bike)
        print(f"Bike inserted: {bike['name']}")
        return new_bike.inserted_id

  def go_to_next_page(self):
    self.page += 1

  def get_bike_links(self):
    main_url = replace_query_param(self.url, "page", self.page)
    driver.get(main_url)
    WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CLASS_NAME, "product-list__item")))

    if self.page == 0:
      self.result_count = int(driver.find_element(By.ID, "results-count--product").text.split(" ")[0])
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
        self.bike_count += 1

      except StaleElementReferenceException:
          continue  # Skip stale elements
      except NoSuchElementException:
          print(f"Skipping a bike due to error")
  
  def get_specs_1(self, spec, current_spec_type):
    newSpec = {}
    weight = ""
    weight_limit = ""
    spec_sizes = []
    try :
      spec_type = spec.find_element(By.TAG_NAME, "th").get_attribute("innerText").strip().replace("*", "")
      spec_td = spec.find_element(By.TAG_NAME, "td")
      spec_value = spec_td.get_attribute("innerText").strip()

      try:
        spec_a = spec_td.find_element(By.TAG_NAME, "a")
        spec_link = spec_a.get_attribute("href")
        spec_brand = self.brand_id
      except NoSuchElementException:
        spec_link = ""
        brand = find_brand_in_component(spec_value, self.brands)
        if brand is not None:
          spec_brand = brand["_id"]
        else:
          spec_brand = None

      if "Size" in spec_value: 
        parsed_size = parse_sizes(spec_value)
        spec_value = parsed_size["value"]
        spec_sizes = parsed_size["sizes"]

      if spec_type != "Weight" and spec_type != "Weight limit":
        newSpec = {
        "createdAt": datetime.now(), 
        "updatedAt": datetime.now(), 
        "name": spec_value, 
        "type": spec_type, 
        "brand": spec_brand,
        "source": spec_link,
        "affiliateLink": spec_link,
        "sizes": spec_sizes
      }
      elif spec_type == "Weight": 
        weight = spec_value
      elif spec_type == "Weight limit": 
        weight_limit = spec_value


    except NoSuchElementException:
      spec_type = current_spec_type
      spec_td = spec.find_element(By.TAG_NAME, "td")
      spec_value = spec_td.get_attribute("innerText").strip()

      try:
        spec_a = spec_td.find_element(By.TAG_NAME, "a")
        spec_link = spec_a.get_attribute("href")
        spec_brand = self.brand_id
      except NoSuchElementException:
        spec_link = ""
        brand = find_brand_in_component(spec_value, self.brands)
        if brand is not None:
          spec_brand = brand["_id"]
        else:
          spec_brand = None

      if "Size" in spec_value: 
        parsed_size = parse_sizes(spec_value)
        spec_value = parsed_size["value"]
        spec_sizes = parsed_size["sizes"]

      if spec_type != "Weight" and spec_type != "Weight limit":
          newSpec = {
            "createdAt": datetime.now(), 
            "updatedAt": datetime.now(), 
            "name": spec_value, 
            "type": spec_type, 
            "brand": spec_brand,
            "source": spec_link,
            "affiliateLink": spec_link,
            "sizes": spec_sizes
          }
      elif spec_type == "Weight": 
        weight = spec_value
      elif spec_type == "Weight limit": 
        weight_limit = spec_value
    
    return newSpec, weight, weight_limit, spec_type

  def get_specs_2(self, spec, current_spec_type):
    newSpec = {}
    weight = ""
    weight_limit = ""
    spec_sizes = []
    try :
      spec_data = spec.find_element(By.TAG_NAME, "dl")
      spec_type = spec_data.find_element(By.TAG_NAME, "dt").get_attribute("innerText").strip().replace("*", "")
      spec_td = spec_data.find_element(By.TAG_NAME, "dd")
      spec_value = spec_td.get_attribute("innerText").strip()

      try:
        spec_a = spec_td.find_element(By.TAG_NAME, "a")
        spec_link = spec_a.get_attribute("href")
        spec_brand = self.brand_id
      except NoSuchElementException:
        spec_link = ""
        brand = find_brand_in_component(spec_value, self.brands)
        if brand is not None:
          spec_brand = brand["_id"]
        else:
          spec_brand = None

      if "Size" in spec_value: 
        parsed_size = parse_sizes(spec_value)
        spec_value = parsed_size["value"]
        spec_sizes = parsed_size["sizes"]

      if spec_type != "Weight" and spec_type != "Weight limit":
        newSpec = {
          "createdAt": datetime.now(), 
          "updatedAt": datetime.now(), 
          "name": spec_value, 
          "type": spec_type, 
          "brand": spec_brand,
          "source": spec_link,
          "affiliateLink": spec_link,
          "sizes": spec_sizes
        }
      elif spec_type == "Weight": 
        weight = spec_value
      elif spec_type == "Weight limit": 
        weight_limit = spec_value

    except NoSuchElementException:
      spec_type = current_spec_type
      spec_td = spec.find_element(By.TAG_NAME, "dd")
      spec_value = spec_td.get_attribute("innerText").strip()

      try:
        spec_a = spec_td.find_element(By.TAG_NAME, "a")
        spec_link = spec_a.get_attribute("href")
        spec_brand = self.brand_id
      except NoSuchElementException:
        spec_link = ""
        brand = find_brand_in_component(spec_value, self.brands)
        if brand is not None:
          spec_brand = brand["_id"]
        else:
          spec_brand = None

      if "Size" in spec_value: 
        parsed_size = parse_sizes(spec_value)
        spec_value = parsed_size["value"]
        spec_sizes = parsed_size["sizes"]

      if spec_type != "Weight" and spec_type != "Weight limit":
        newSpec = {
          "createdAt": datetime.now(), 
          "updatedAt": datetime.now(), 
          "name": spec_value, 
          "type": spec_type, 
          "brand": spec_brand,
          "source": spec_link,
          "affiliateLink": spec_link,
          "sizes": spec_sizes
        }
      elif spec_type == "Weight": 
        weight = spec_value
      elif spec_type == "Weight limit": 
        weight_limit = spec_value
    return newSpec, weight, weight_limit, spec_type

  def scrape_bike_details(self, link, previous_url, base_url, next_url, bike: Bike): 
    try:
      driver.get(base_url)
      WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CLASS_NAME, "pdp-product-details")))
      # time.sleep(3)

      if link["base_url"] != previous_url:
        current_spec_type = ""
        header = driver.find_element(By.CLASS_NAME, "buying-zone__header")
        bike.set_name(header.find_element(By.CLASS_NAME, "buying-zone__title").text)
        image = driver.find_element(By.CLASS_NAME, "swiper-lazy").get_attribute("src")

        if image is not None:
          bike.set_imageUrl(image.split("%20")[0])

        footer = driver.find_element(By.CLASS_NAME, "buying-zone__footer")
        priceSpan = footer.find_element(By.TAG_NAME, "span")
        bike.set_currentPrice(extract_price(priceSpan.find_element(By.CLASS_NAME, "actual-price").text))
        bike.set_description(footer.find_element(By.TAG_NAME, "p").text)

        try: 
          specs_container = driver.find_element(By.CLASS_NAME, "pdp-spec-collapse")
          specs_items = specs_container.find_elements(By.TAG_NAME, "tr")
          for spec in specs_items:
            newSpec, weight, weight_limit, spec_type = self.get_specs_1(spec, current_spec_type)
            current_spec_type = spec_type
            if newSpec != {}:
              bike.append_component(newSpec)
            if weight !="":
              bike.set_weight(weight)
            if weight_limit !="":
              bike.set_weightLimit(weight_limit)

        except NoSuchElementException: 
          specs_section = driver.find_element(By.ID, "trekProductSpecificationsComponent")
          specs_container = specs_section.find_element(By.TAG_NAME, "ul")
          specs_items = specs_container.find_elements(By.TAG_NAME, "li")
          for spec in specs_items:
            newSpec, weight, weight_limit, spec_type = self.get_specs_2(spec, current_spec_type)
            current_spec_type = spec_type
            if newSpec != {}:
              bike.append_component(newSpec)
            if weight !="":
              bike.set_weight(weight)
            if weight_limit !="":
              bike.set_weightLimit(weight_limit)
                
      size_elements = driver.find_elements(By.CLASS_NAME, "product-attribute-btn")
      sizes = []
      color = link["color"]

      for size in size_elements:
        if "unavailable" not in size.get_attribute("class"):
          sizes.append(size.find_element(By.TAG_NAME, "span").text)

      bike.append_variation({"color": color, "sizes": sizes})
      
      if link["base_url"] != next_url:
        bike_type_parts = link["base_url"].split("/")
        index = bike_type_parts.index("bikes")  # Find the position of "bikes"
        bike_type = bike_type_parts[index + 2].rstrip("s")
        
        newBike = {
          "createdAt": datetime.now(), 
          "updatedAt": datetime.now(), 
          "name": bike.get_name(), 
          "description": bike.get_description(), 
          "brand": self.brand_id,
          "type": bike_type,
          "currentPrice": bike.get_currentPrice(), 
          "currency": "CAD",
          "imageUrl": bike.get_imageUrl(), 
          "source": link["base_url"], 
          "affiliateLink": link, 
          "weight": bike.get_weight(),
          "weightLimit": bike.get_weightLimit(),
          "variations": bike.get_variations(), 
        }
        new_bike_id = self.post_bike(newBike)
        component_ids = self.post_components(bike.get_components())
        self.post_bike_components(new_bike_id, component_ids)
        self.bikes.append(newBike)
        print(f"progress: {len(self.bikes)}/{self.result_count}")

    except NoSuchElementException as e:
      print(f"Skipping a bike due to error {link} {e}")

  def scrape_bikes_selenium(self):
    bike = Bike(name="", description="", brand="", type="", currentPrice="", currency="", imageUrl="", source="", affiliateLink={"base_url": "", "color": ""}, weight="", weight_limit="", variations=[], components=[])
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

      if link["base_url"] != previous_url: 
        bike.reset_bike()
      self.scrape_bike_details(link, previous_url, base_url, next_url, bike)
    print(f"Scraped {len(self.bikes)} bikes from {self.url}")

  def get_bikes(self):
    self.post_brand({"createdAt": datetime.now(), "updatedAt": datetime.now(), "name": "Trek", "website": "https://www.trekbikes.com/ca/en_CA/"})
    self.get_brands()
    while self.bike_count < self.result_count:
      self.get_bike_links()
      self.go_to_next_page()
      print(f"{len(self.bike_links)} links")
      print(f"links progress: {self.bike_count}/{self.result_count}")
    self.scrape_bikes_selenium()

  def pw_get_bike(self, url):
    with sync_playwright() as pw:
      browser = pw.chromium.launch(headless=True)
      page = browser.new_page()

      page.goto(url)  # go to url
      content = page.content()  # Gets the full HTML content of the page
      page.wait_for_selector("div[class=pdp-product-details]")  # wait for content to load

      parsed = []
      sizes = page.query_selector_all(".product-attribute-btn")
      for size in sizes:
          if "unavailable" not in size.get_attribute("class"):
            parsed.append(size.inner_text())
          """ parsed.append({
              "title": box.query_selector("h3").inner_text(),
              "url": box.query_selector(".tw-link").get_attribute("href"),
              "username": box.query_selector(".tw-link").inner_text(),
              "viewers": box.query_selector(".tw-media-card-stat").inner_text(),
              # tags are not always present:
              "tags": box.query_selector(".tw-tag").inner_text() if box.query_selector(".tw-tag") else None,
          }) """
      print(parsed)
      browser.close()

# Example usage
trek_url = "https://www.trekbikes.com/ca/en_CA/bikes/c/B100/?pageSize=24&page=0&q=%3Arelevance%3AfacetFrameset%3AfacetFrameset2&sort=relevance#"
trek = Trek(trek_url)
""" trek.pw_get_bike("https://www.trekbikes.com/ca/en_CA/bikes/mountain-bikes/trail-mountain-bikes/fuel-ex/fuel-ex-9-8-gx-axs-gen-6/p/36953/?colorCode=") """
trek.get_bikes()
""" bike = Bike(name="", description="", brand="", type="", currentPrice="", currency="", imageUrl="", source="", affiliateLink={"base_url": "", "color": ""}, weight="", weight_limit="", variations=[], components=[])
trek.scrape_bike_details({"base_url": "https://www.trekbikes.com/ca/en_CA/bikes/electric-bikes/electric-road-bikes/domane-slr/domane-slr-7-axs/p/44607/?colorCode=", "color": "black"}, "", "https://www.trekbikes.com/ca/en_CA/bikes/electric-bikes/electric-road-bikes/domane-slr/domane-slr-7-axs/p/44607/?colorCode=black", "", bike) """
driver.quit()