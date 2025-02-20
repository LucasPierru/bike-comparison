from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
from playwright.async_api import async_playwright, ElementHandle, Page
import asyncio
import time
import sys
import os
from datetime import datetime
from pymongo import UpdateOne

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from models.bike import Bike
from toolbox.toolbox import clean_string, replace_query_param, previous_and_next, parse_sizes, extract_price, find_brand_in_component
from db import get_database

MAX_CONCURRENCY = 5 

db = get_database()
bike_collection = db["bikes"]
brand_collection = db["brands"]
component_collection = db["components"]
bike_component_collection = db["bikecomponents"]

class Specialized:
  bike_links = []
  bikes = []
  brands = []
  type_set = set()

  def __init__(self, url: str):
    self.url = url

  def get_brand(self, name):
    existing_brand = brand_collection.find_one({"name": name})
    self.brand_id = existing_brand["_id"]

  def get_brands(self):
    brands = brand_collection.find({})
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

  async def gather_bike_links(self):
    async with async_playwright() as pw:
      browser = await pw.chromium.launch(headless=True, args=['--no-sandbox', "--disable-gpu"])
      page = await browser.new_page()

      main_url = self.url
      await page.goto(main_url)  # go to url
      await page.set_extra_http_headers({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
      })

      await page.wait_for_selector("body")  # wait for content to load
      btn_section = await page.query_selector('section[class="sc-33bfb7a-0 iPDlzn"]')


      while btn_section is not None:
        show_more_btn = await btn_section.query_selector('button')
        await show_more_btn.click()
        time.sleep(10)
        btn_section = await page.query_selector('section[class="sc-33bfb7a-0 iPDlzn"]')

      bike_elements = await page.query_selector_all("article[data-component=product-tile]")  # Adjust selector

      for bike in bike_elements:
        await self.get_link(bike)
        # os.system('cls')
        print(f"links gathered: {len(self.get_bike_links())}/{len(bike_elements)}")

      await browser.close()

  async def get_bike_data(self, link):
    async with async_playwright() as pw:
      bike = Bike(name="", description="", brand="", type="", currentPrice="", currency="", imageUrl="", source="", affiliateLink={"base_url": "", "color": ""}, weight="", weight_limit="", variations=[], components=[])
      browser = await pw.chromium.launch(headless=True, args=['--no-sandbox', "--disable-gpu"])
      page = await browser.new_page()
      for idx, variation in enumerate(link["variations"]):
        try:
          sizes = []
          await page.set_extra_http_headers({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
          })
          await page.goto(variation["link"])
          await page.wait_for_selector("body")  # wait for content to load
          time.sleep(4)
          if idx == 0:
            h1 = await page.query_selector("h1")
            product_details_section = await page.query_selector("section[id=product-details]")
            h5 = await page.query_selector("h5")
            img = await page.query_selector("div[class=swiper-wrapper] img")
            components_section_elements = await page.query_selector_all("section[id=technical-specifications] div div div div div div div div div")
            nav = await page.query_selector("nav[aria-label=breadcrumb]")
            first_size_button = await page.query_selector('button[class="sc-60406dd7-0 sc-60406dd7-2 iMRIVl iwdvda sc-a8ed3f79-0 flntDk"]')

            if first_size_button is not None:
              await first_size_button.click()
              time.sleep(3)
            
            bike.set_source(link["base_url"])
            bike.set_currency("CAD")
            bike.set_brand(self.brand_id)

            if h1 is not None:
              name = await h1.inner_text()
              bike.set_name(name)
              """ self.bikes.append({"title": title}) """
            if product_details_section is not None:
              description_tag = await product_details_section.query_selector("p")
              if description_tag is None:
                raise Exception("description error")
              description = await description_tag.inner_text()
              bike.set_description(clean_string(description))
            
            if h5 is not None:
              price_value = await h5.inner_text()
              if "-" in price_value:
                price_value = price_value.split("-")[0]
              price = extract_price(price_value)
              bike.set_currentPrice(price)

            if img is not None:
              image_url = await img.get_attribute("src")
              bike.set_imageUrl(image_url)
            
            if nav is not None:
              crumbs = await nav.query_selector_all("li[itemprop=itemListElement]")
              if crumbs[-2] is None:
                raise Exception("nav error")
              bike_type = await crumbs[-2].inner_text()
              bike.set_type(bike.map_to_general_bike_type(bike_type))
              self.type_set.add(bike_type)

            for component in components_section_elements:
              components_p = await component.query_selector_all('p')
              if len(components_p) < 2:
                continue
              component_type_sel = components_p[0]
              component_value_sel = components_p[1]
              component_type = await component_type_sel.inner_text()
              component_value = await component_value_sel.inner_text()
              if component_type == "Weight":
                bike.set_weight(component_value)
              elif component_type == "Weight Size":
                continue
              else:
                brand = find_brand_in_component(component_value, self.brands)
                brand_id = None
                if brand is not None:
                  brand_id = brand["_id"]
                bike.append_component({
                  "type": component_type, 
                  "name": component_value, 
                  "brand": brand_id, 
                  "source": "https://www.specialized.com",
                  "affiliateLink": "",
                  "sizes": []
                })

          size_selection = await page.query_selector('div[data-component="size-selection"]')  
          if size_selection is None:
            print(link)
          if size_selection is not None:
            size_buttons = await size_selection.query_selector_all("button")
            for button in size_buttons:
              button_html = await button.inner_html()
              if "after" not in button_html:
                # If the button doesn't have the ::after element, click it or interact with it
                sizes.append(await button.inner_text())
          bike.append_variation({"color": variation["color"], "sizes": sizes})
          if idx == (len(link["variations"])-1):
            bike.set_affiliateLink({"base_url": variation["link"], "color": variation["color"]})
            self.bikes.append(bike.__dict__)
            newBike = {
              "createdAt": datetime.now(), 
              "updatedAt": datetime.now(), 
              "name": bike.get_name(), 
              "description": bike.get_description(), 
              "brand": self.brand_id,
              "type": bike.get_type(),
              "currentPrice": bike.get_currentPrice(), 
              "currency": "CAD",
              "imageUrl": bike.get_imageUrl(), 
              "source": bike.get_source(), 
              "affiliateLink": bike.get_affiliateLink(), 
              "weight": bike.get_weight(),
              "weightLimit": None,
              "variations": bike.get_variations(), 
            }

            print(newBike)
            
            new_bike_id = self.post_bike(newBike)
            component_ids = self.post_components(bike.get_components())
            self.post_bike_components(new_bike_id, component_ids)
            print(f"progress: {len(self.bikes)}/{len(self.bike_links)}")
        except Exception as e:
          print(e)
          print(variation["link"])
      await browser.close()

  async def get_bikes(self):
    tasks = []
    semaphore = asyncio.Semaphore(MAX_CONCURRENCY)

    async def scrape_with_semaphore(link):
      async with semaphore:
        await self.get_bike_data(link)
    
    for link in self.bike_links:
      tasks.append(scrape_with_semaphore(link))
      
        
    await asyncio.gather(*tasks)
    print(self.bikes)
    print(self.type_set)
      

  async def get_link(self, bike: ElementHandle):
    a_tag = await bike.query_selector("a")
    link_end = await a_tag.get_attribute("href")
    link = f"https://www.specialized.com{link_end.split("?")[0]}"
    ul = await bike.query_selector("ul")
    colors = await ul.query_selector_all("li")
    bike_colors = []
    for color in colors:
      await color.hover()
      await color.wait_for_selector("a")
      color_a = await color.query_selector("a")
      color_link = await color_a.get_attribute("href")
      col = await color_a.get_attribute("title")
      bike_colors.append({"link": f"https://www.specialized.com{color_link}", "color": col})
    self.bike_links.append({"base_url": link, "variations": bike_colors})
  
  def get_bike_links(self):
    return self.bike_links
  
async def main():
  url = "https://www.specialized.com/ca/en/shop/bikes?group=Bikes"
  spec = Specialized(url)
  spec.get_brand("Specialized")
  spec.get_brands()
  print("Getting links")
  await spec.gather_bike_links()
  links = spec.get_bike_links()
  print("Getting bikes")
  await spec.get_bikes()

if __name__ == "__main__":
  asyncio.run(main())
""" url = "https://www.specialized.com/ca/en/shop/bikes?group=Bikes"
spec = Specialized(url)
spec.get_brand("Specialized")
spec.get_brands()
link = {'base_url': 'https://www.specialized.com/ca/en/diverge-sport-carbon/p/4223496', 'variations': [{'link': 'https://www.specialized.com/ca/en/diverge-sport-carbon/p/4223496?color=5381924-4223496', 'color': 'Satin Carbon / Blue Onyx'}, {'link': 'https://www.specialized.com/ca/en/diverge-sport-carbon/p/4223496?color=5381925-4223496', 'color': 'Satin Doppio / Gunmetal'}, {'link': 'https://www.specialized.com/ca/en/diverge-sport-carbon/p/4223496?color=5381904-4223496', 'color': 'Satin Metallic Spruce / Spruce'}]}
component_error_link = {
  'base_url': 'https://www.specialized.com/ca/en/rockhopper-sport/p/221599', 
  'variations': [
    {
      'link': 'https://www.specialized.com/ca/en/rockhopper-sport/p/221599?color=366665-221599', 
      'color': 'GLOSS PINE GREEN / OBSIDIAN'
    }, 
    {
      'link': 'https://www.specialized.com/ca/en/rockhopper-sport/p/221599?color=366667-221599', 
      'color': 'GLOSS SAPPHIRE / DUNE WHITE'
    }
  ]
}
asyncio.run(spec.get_bike_data(component_error_link)) """