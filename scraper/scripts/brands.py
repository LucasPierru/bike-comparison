import sys
import os
from datetime import datetime
from pymongo import UpdateOne

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import config
from db import get_database
db = get_database()
brand_collection = db["brands"]

def add_brands_to_db():
  brands = config.BRANDS_LIST
  operations=[]
  for brand in brands:
    brand["updatedAt"] = datetime.now()
    updateBrand = dict(brand)
    del updateBrand["name"]
    print(brand)
    operations.append(UpdateOne({"name": brand["name"]}, {"$set": updateBrand, "$setOnInsert": {"createdAt": datetime.now()}}, upsert=True))
  brand_collection.bulk_write(operations)

if __name__ == '__main__':
  add_brands_to_db()