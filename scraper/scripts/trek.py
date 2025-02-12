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
      component.pop("createdAt", None) 
      operations.append(UpdateOne({"name": component["name"]}, {"$set": component, "$setOnInsert": {"createdAt": datetime.now()}}, upsert=True))
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
    with sync_playwright() as pw:
      browser = pw.chromium.launch(headless=True)
      page = browser.new_page()

      main_url = replace_query_param(self.url, "page", self.page)
      page.goto(main_url)  # go to url
      page.wait_for_selector(".searchresultslistcomponent")  # wait for content to load

      if self.page == 0:
        self.result_count = int(page.query_selector("#results-count--product").inner_text().split(" ")[0])
      bike_elements = page.query_selector_all(".product-list__item")  # Adjust selector

      for bike in bike_elements:
        elem = bike.query_selector("a")
        color_list = elem.query_selector(".pdl-swatches")
        if color_list is not None:
          color_elements = color_list.query_selector_all(".pdl-swatch-container")
          link = elem.get_attribute("href")

          for color in color_elements:
            col = color.query_selector("label").get_attribute("title")
            base_url = replace_query_param(link, "colorCode", "")
            bike_link = {
              "base_url": f"https://www.trekbikes.com{base_url}",
              "color": col
            }
            self.bike_links.append(bike_link)
          self.bike_count += 1

        else:
          print(f"Skipping a bike due to error")
      browser.close()
  
  def get_specs_1(self, spec, current_spec_type):
    newSpec = {}
    weight = ""
    weight_limit = ""
    spec_sizes = []

    spec_type_sel = spec.query_selector("th")

    if spec_type_sel is not None:
      spec_type = spec_type_sel.inner_text().strip().replace("*", "")
      spec_td = spec.query_selector("td")
      spec_value = spec_td.inner_text().strip()

      spec_a = spec_td.query_selector("a")

      if spec_a is not None:
        spec_link = spec_a.get_attribute("href")
        spec_brand = self.brand_id
      else:
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
      
      if spec_link:
        spec_link = f"https://www.trekbikes.com{spec_link}"

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

    else:
      spec_type = current_spec_type
      spec_td = spec.query_selector("td")
      spec_value = spec_td.inner_text().strip()

      spec_a = spec_td.query_selector("a")

      if spec_a is not None:
        spec_link = spec_a.get_attribute("href")
        spec_brand = self.brand_id
      else:
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
      
      if spec_link:
        spec_link = f"https://www.trekbikes.com{spec_link}"

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
    spec_data = spec.query_selector("dl")
    spec_type_sel = spec_data.query_selector("dt")

    if spec_type_sel is not None:
      spec_data = spec.query_selector("dl")
      spec_type = spec_type_sel.inner_text().strip().replace("*", "")
      spec_td = spec_data.query_selector("dd")
      spec_value = spec_td.inner_text().strip()
      spec_a = spec_td.query_selector("a")

      if spec_a is not None:
        spec_link = spec_a.get_attribute("href")
        spec_brand = self.brand_id
      else:
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

      if spec_link:
        spec_link = f"https://www.trekbikes.com{spec_link}"

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

    else:
      spec_type = current_spec_type
      spec_td = spec.query_selector("dd")
      spec_value = spec_td.inner_text().strip()
      spec_a = spec_td.query_selector("a")

      if spec_a is not None:
        spec_link = spec_a.get_attribute("href")
        spec_brand = self.brand_id
      else:
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
      
      if spec_link:
        spec_link = f"https://www.trekbikes.com{spec_link}"

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
      self.pw_get_bike(link, previous_url, base_url, next_url, bike)
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

  def pw_get_bike(self, link, previous_url, base_url, next_url, bike: Bike):
    with sync_playwright() as pw:
      browser = pw.chromium.launch(headless=True)
      page = browser.new_page()

      page.goto(base_url)  # go to url
      page.wait_for_selector("div[class=pdp-product-details]")  # wait for content to load

      if link["base_url"] != previous_url:
        current_spec_type = ""
        bike.set_name(page.query_selector("h1[class=buying-zone__title]").inner_text())
        bike.set_description(page.query_selector("p[qaid=product-positioning-statement]").inner_text())
        bike.set_currentPrice(extract_price(page.query_selector("span[qaid=actual-price]").inner_text()))
        bike.set_imageUrl(f"https:{page.query_selector("img[class=swiper-lazy]").get_attribute("src")}")

        specs_container = page.query_selector(".pdp-spec-collapse")
        if specs_container is not None: 
          specs_items = specs_container.query_selector_all("tr")
          for spec in specs_items:
            newSpec, weight, weight_limit, spec_type = self.get_specs_1(spec, current_spec_type)
            current_spec_type = spec_type
            if newSpec != {}:
              bike.append_component(newSpec)
            if weight !="":
              bike.set_weight(weight)
            if weight_limit !="":
              bike.set_weightLimit(weight_limit)

        else: 
          specs_section = page.query_selector("#trekProductSpecificationsComponent")
          specs_container = specs_section.query_selector("ul")
          specs_items = specs_container.query_selector_all("li")
          for spec in specs_items:
            newSpec, weight, weight_limit, spec_type = self.get_specs_2(spec, current_spec_type)
            current_spec_type = spec_type
            if newSpec != {}:
              bike.append_component(newSpec)
            if weight !="":
              bike.set_weight(weight)
            if weight_limit !="":
              bike.set_weightLimit(weight_limit)

      sizes = []
      size_elements = page.query_selector_all(".product-attribute-btn")
      for size in size_elements:
          if "unavailable" not in size.get_attribute("class"):
            sizes.append(size.inner_text())

      color = link["color"]
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

      browser.close()

# Example usage
trek_url = "https://www.trekbikes.com/ca/en_CA/bikes/c/B100/?pageSize=24&page=0&q=%3Arelevance%3AfacetFrameset%3AfacetFrameset2&sort=relevance#"
trek = Trek(trek_url)
""" bike = Bike(name="", description="", brand="", type="", currentPrice="", currency="", imageUrl="", source="", affiliateLink={"base_url": "", "color": ""}, weight="", weight_limit="", variations=[], components=[])
trek.pw_get_bike({"base_url": "https://www.trekbikes.com/ca/en_CA/bikes/electric-bikes/electric-road-bikes/domane-slr/domane-slr-7-axs/p/44607/?colorCode=", "color": "black"}, "", "https://www.trekbikes.com/ca/en_CA/bikes/electric-bikes/electric-road-bikes/domane-slr/domane-slr-7-axs/p/44607/?colorCode=black", "", bike) """
trek.get_bikes()
""" bike = Bike(name="", description="", brand="", type="", currentPrice="", currency="", imageUrl="", source="", affiliateLink={"base_url": "", "color": ""}, weight="", weight_limit="", variations=[], components=[])
trek.scrape_bike_details({"base_url": "https://www.trekbikes.com/ca/en_CA/bikes/electric-bikes/electric-road-bikes/domane-slr/domane-slr-7-axs/p/44607/?colorCode=", "color": "black"}, "", "https://www.trekbikes.com/ca/en_CA/bikes/electric-bikes/electric-road-bikes/domane-slr/domane-slr-7-axs/p/44607/?colorCode=black", "", bike) """