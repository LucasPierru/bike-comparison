from datetime import datetime
from db import get_database

class BaseModel:
  collection_name = None

  def __init__ (self, data=None):
    self.createdAt = datetime.now()
    self.updatedAt = datetime.now()
    self.db = get_database()
    if data:
      self.__dict__.update(data)

  def get_collection(self):
    """Return the correct MongoDB collection for this model."""
    if not self.collection_name:
        raise ValueError("collection_name must be defined in the subclass")
    return self.db[self.collection_name]
    
  def insert(self, insert_data):
    """Insert a new document with createdAt and updatedAt."""
    insert_data["createdAt"] = self.createdAt
    insert_data["updatedAt"] = self.updatedAt
    result = self.get_collection().insert_one(insert_data)
    return result.inserted_id  # Returns the number of documents updated

  def update(self, query, update_data):
    """Update an existing document and refresh updatedAt."""
    update_data["updatedAt"] = self.updatedAt
    result = self.get_collection().update_one(query, {"$set": update_data})
    return result.modified_count  # Returns the number of documents updated
  
  def insert_or_update(self, query, update_data):
    """Insert or update the document in the correct collection."""
    update_data["updatedAt"] = self.updatedAt
    return self.get_collection().update_one(query, {"$set": update_data, "$setOnInsert": {"createdAt": self.createdAt}}, upsert=True)
  