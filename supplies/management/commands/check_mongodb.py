from django.core.management.base import BaseCommand
from supplies.mongodb_utils import get_database, get_collection
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Check MongoDB connection and list collections'

    def handle(self, *args, **kwargs):
        db = get_database()
        if db is None:
            self.stdout.write(self.style.ERROR('Failed to connect to MongoDB'))
            return
        
        self.stdout.write(self.style.SUCCESS('Successfully connected to MongoDB'))
        
        # List collections
        collections = db.list_collection_names()
        if collections:
            self.stdout.write(self.style.SUCCESS(f'Found {len(collections)} collections:'))
            for collection in collections:
                count = db[collection].count_documents({})
                self.stdout.write(f'  - {collection}: {count} documents')
        else:
            self.stdout.write(self.style.WARNING('No collections found in the database'))
        
        # Check if we have locations
        locations_coll = get_collection('locations')
        if locations_coll is not None:
            locations = list(locations_coll.find())
            if locations:
                self.stdout.write(self.style.SUCCESS(f'Found {len(locations)} locations:'))
                for loc in locations:
                    self.stdout.write(f'  - {loc["name"]}: {loc["address"]}')
            else:
                self.stdout.write(self.style.WARNING('No locations found. You may need to run init_mongodb command.'))