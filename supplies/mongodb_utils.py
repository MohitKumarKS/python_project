from pymongo import MongoClient
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

def get_mongodb_client():
    """
    Get a MongoDB client connection
    """
    try:
        client = MongoClient(settings.MONGODB_URI)
        # Test the connection
        client.admin.command('ping')
        return client
    except Exception as e:
        logger.error(f"Error connecting to MongoDB: {str(e)}")
        return None

def get_database():
    """
    Get the MongoDB database
    """
    client = get_mongodb_client()
    if client is not None:
        return client[settings.MONGODB_NAME]
    return None

def get_collection(collection_name):
    """
    Get a MongoDB collection
    """
    db = get_database()
    if db is not None:
        return db[collection_name]
    return None



