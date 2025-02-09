from models.base_model import BaseModel

class Brand(BaseModel):
  collection_name = "brands"

  def __init__ (self, name:str, website:str):
    self.name = name
    self.website = website
  
  def reset_brand(self):
    self.name = ""
    self.website = ""

  def get_name(self):
    return self.name

  def get_website(self):
    return self.website
  
  def set_name(self, name):
    self.name = name

  def set_website(self, website):
    self.website = website
