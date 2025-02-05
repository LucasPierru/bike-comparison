from pymongo import MongoClient
import config
import certifi

ca = certifi.where()

def get_database():
   # Create a connection using MongoClient. You can import MongoClient or use pymongo.MongoClient
   client = MongoClient(config.MONGO_URI, tlsCAFile=ca)
 
   # Create the database for our example (we will use the same database throughout the tutorial
   return client[config.DB_NAME]
  
# This is added so that many files can reuse the function get_database()
if __name__ == "__main__":   
  
   # Get the database
   dbname = get_database()