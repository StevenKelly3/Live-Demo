''' This will be used to store information on
    1) The PYKWT secret_key
    2) Connection details for mongoDB
'''

### --- IMPORTS --- ###
from pymongo import MongoClient
import os
from dotenv import load_dotenv # used to read the .env file

### --- GET SECRET KEY --- ###
load_dotenv()

### --- SECRET KEY --- ###
#secret_key = 'hellothere'
secret_key = os.environ.get("ALCHEMAX_SECRET_KEY")

### --- DB CONNECTION --- ###
client = MongoClient("mongodb://127.0.0.1:27017"); db = client.Project_Alchemax