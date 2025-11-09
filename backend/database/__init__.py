"""
Database package initialization.

Sets up a MongoDB client using the provided Atlas connection string so other
modules can import `backend.database` and rely on the client being ready.
"""
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

URI = (
    "mongodb+srv://admin:48aX6qgzAjf9uZ2Y@hackutd2025.3wkesnl.mongodb.net/"
    "?appName=HackUTD2025"
)

client = MongoClient(URI, server_api=ServerApi("1"))

try:
    client.admin.command("ping")
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as exc:
    print(exc)