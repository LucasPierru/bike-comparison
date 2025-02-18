from models.base_model import BaseModel

class Bike(BaseModel):
  collection_name = "bikes"
  bike_type_mapping = {
    'cross-country-mountain-bike': ['mountain'],
    'trail-mountain-bike': ['mountain'],
    'downhill-mountain-bike': ['mountain'],
    'dual-sport-bike': ['mountain', 'city'],
    'fat-bike': ['mountain'],
    'performance-road-bike': ['road'],
    'triathlon-bike': ['road', 'triathlon'],
    'gravel-bike': ['gravel', 'road'],
    'cyclocross-bike': ['gravel', 'road'],
    'cruiser-bike': ['city'],
    'fitness-bike': ['city', 'hybrid'],
    'loft': ['city'],
    'townie': ['city'],
    'recreation-bike': ['city', 'hybrid'],
    'electra-e-bike': ['electric'],
    'electra-kids-bike': ['electric', 'kids'],
    'electric-hybrid-bike': ['electric', 'hybrid'],
    'electric-mountain-bike': ['electric', 'mountain'],
    'electric-road-bike': ['electric', 'road'],
    'kids-hybrid-bike': ['kids', 'hybrid'],
    'Downhill Mountain Bikes': ['mountain'],
    'Performance Road Bikes': ['road'],
    'BMX and Dirt Jump Bikes': ['bmx', 'mountain'],
    'Cross Country Mountain Bikes': ['mountain'],
    'Vélos Enfants': ['kids'],
    'Trail Bikes': ['mountain'],
    'Kids Bikes': ['kids'],
    'Gravel Bikes': ['gravel', 'road'],
    'Mountain Bikes': ['bikes'],
    'Globe': ['city', 'electric'],
    'Fitness Bikes': ['city', 'hybrid'],
    'Bikes': ['city', 'hybrid']
}

  def map_to_general_bike_type(self, brand_type):
    # Convert the brand type to lowercase to handle case-insensitivity
    brand_type = brand_type.lower()
    return self.bike_type_mapping.get(brand_type, None)  

  def __init__ (self, name:str, description:str, brand, type:str, currentPrice, currency, imageUrl:str, source:str, affiliateLink, weight:str, weight_limit:str, variations, components):
    self.name = name
    self.description = description
    self.brand = brand
    self.type = type
    self.currentPrice = currentPrice
    self.currency = currency
    self.imageUrl = imageUrl
    self.source = source
    self.affiliateLink = affiliateLink
    self.weight = weight
    self.weight_limit = weight_limit
    self.variations = variations
    self.components = components
  
  def reset_bike(self):
    self.name = ""
    self.description = ""
    self.brand = ""
    self.type = ""
    self.currentPrice = ""
    self.currency = ""
    self.imageUrl = ""
    self.source = ""
    self.affiliateLink = {"base_url": "", "color": ""}
    self.weight = ""
    self.weight_limit = ""
    self.variations = []
    self.components = []

  def get_name(self):
    return self.name

  def get_description(self):
    return self.description
  
  def get_brand(self):
    return self.brand
  
  def get_type(self):
    return self.type
  
  def get_currentPrice(self):
    return self.currentPrice
  
  def get_currency(self):
    return self.currency
  
  def get_imageUrl(self):
    return self.imageUrl
  
  def get_source(self):
    return self.source
  
  def get_affiliateLink(self):
    return self.affiliateLink
  
  def get_weight(self):
    return self.weight
  
  def get_weightLimit(self):
    return self.weight_limit
  
  def get_variations(self):
    return self.variations

  def get_components(self):
    return self.components
  
  def set_name(self, name):
    self.name = name

  def set_description(self, description):
    self.description = description
  
  def set_brand(self, brand):
    self.brand = brand
  
  def set_type(self, type):
    self.type = type
  
  def set_currentPrice(self, currentPrice):
    self.currentPrice = currentPrice
  
  def set_currency(self, currency):
    self.currency = currency
  
  def set_imageUrl(self, imageUrl):
    self.imageUrl = imageUrl
  
  def set_source(self, source):
    self.source = source
  
  def set_affiliateLink(self, affiliateLink):
    self.affiliateLink = affiliateLink
  
  def set_weight(self, weight):
    self.weight = weight
  
  def set_weightLimit(self, weight_limit):
    self.weight_limit = weight_limit
  
  def set_variations(self, variations):
    self.variations = variations

  def append_variation(self, variation):
    self.variations.append(variation)

  def set_components(self, components):
    self.components = components

  def append_component(self, component):
    self.components.append(component)