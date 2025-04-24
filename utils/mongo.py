import os
from pymongo import MongoClient
from dotenv import load_dotenv

# Check if we are running locally (no 'GOOGLE_CLOUD_PROJECT' environment variable).
if not os.getenv('GOOGLE_CLOUD_PROJECT'):
    # Load environment variables from a .env file for local development
    load_dotenv()
    # Use local MongoDB connection
    mongo_uri = "mongodb://localhost:27017"
    print("Using local MongoDB instance.")
else:
    # Retrieve MongoDB credentials and details from environment variables
    mongo_user = os.getenv('MONGO_USER')
    mongo_password = os.getenv('MONGO_PASSWORD')
    mongo_url = os.getenv('MONGO_URL')

    # Construct the MongoDB connection string for the remote database
    mongo_uri = f"mongodb+srv://{mongo_user}:{mongo_password}@{mongo_url}"
    print("Using remote MongoDB instance.")

print("MongoDB URI: ", mongo_uri)


'''
mongo_uri = os.getenv("MONGO_URI")

client = MongoClient(mongo_uri)
db = client["PlantConnectome"]
server_info = client.server_info()
print("✅ Connected to MongoDB Version:", server_info["version"])
'''
#Connect to the specific database
client = MongoClient(mongo_uri)
db = client.PlantConnectome