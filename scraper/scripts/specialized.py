from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
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

class Specialized:
  bike_links = []

  def __init__(self, url, page=0):
    self.url = url

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

  def get_bike_links(self):
    with sync_playwright() as pw:
      browser = pw.chromium.launch(headless=True)
      page = browser.new_page()

      main_url = self.url
      page.goto(main_url)  # go to url
      page.set_extra_http_headers({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
      })

      page.wait_for_selector("body")  # wait for content to load
      btn_section = page.query_selector('section[class="sc-33bfb7a-0 iPDlzn"]')

      while btn_section is not None:
        show_more_btn = btn_section.query_selector('button[class="sc-60406dd7-0 sc-60406dd7-2 hWXKCL iwdvda"]')
        show_more_btn.click()
        time.sleep(10)
        btn_section = page.query_selector('section[class="sc-33bfb7a-0 iPDlzn"]')
        print(btn_section)

      bike_elements = page.query_selector_all("article[data-component=product-tile]")  # Adjust selector

      for bike in bike_elements:
        link = f"https://www.specialized.com{bike.query_selector("a").get_attribute("href").split("?")[0]}"
        ul = bike.query_selector("ul")
        colors = ul.query_selector_all("li")
        bike_colors = []
        for color in colors:
          color.hover()
          color_a = color.query_selector("a")
          color_link = color_a.get_attribute("href")
          col = color_a.get_attribute("title")
          bike_colors.append({"link": f"https://www.specialized.com{color_link}", "color": col})
        self.bike_links.append({"base_url": link, "variations": bike_colors})
        os.system('cls')
        print(f"{len(self.bike_links)}/{len(bike_elements)}")
      browser.close()

url = "https://www.specialized.com/ca/en/shop/bikes?group=Bikes"
spec = Specialized(url)
spec.get_bike_links()