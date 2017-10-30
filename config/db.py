from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

# mongodb://<dbuser>:<dbpassword>@ds241025.mlab.com:41025/python_social
url = "mongodb://python_social:python_social123@ds241025.mlab.com:41025/python_social"
# url = "mongodb://localhost:27017/"
# client = MongoClient('mongodb://localhost:27017/')
client = MongoClient(url)
connected = False
try:
   mongoServerInfo = client.server_info()
   connected = True
   print("Successfully Connected to MongoServer ")
except ConnectionFailure:
    print("server is down.")

if connected:
    db = client['python_social']
