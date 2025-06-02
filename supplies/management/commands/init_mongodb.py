from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from supplies.mongodb_utils import get_database, get_collection
from pymongo import IndexModel, ASCENDING
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Initialize MongoDB collections and indexes'

    def handle(self, *args, **kwargs):
        db = get_database()
        if db is None:
            self.stdout.write(self.style.ERROR('Failed to connect to MongoDB'))
            return
        
        # Create collections if they don't exist
        collections = ['locations', 'supplies', 'disaster_reports', 'supply_requests']
        existing_collections = db.list_collection_names()
        
        for collection_name in collections:
            if collection_name not in existing_collections:
                db.create_collection(collection_name)
                self.stdout.write(self.style.SUCCESS(f'Created collection: {collection_name}'))
            else:
                self.stdout.write(self.style.WARNING(f'Collection already exists: {collection_name}'))
        
        # Create indexes
        try:
            # Locations collection
            locations_coll = get_collection('locations')
            locations_coll.create_index([('name', ASCENDING)], unique=True)
            
            # Supplies collection
            supplies_coll = get_collection('supplies')
            supplies_coll.create_index([('location', ASCENDING)])
            
            # Disaster reports collection
            reports_coll = get_collection('disaster_reports')
            reports_coll.create_index([('location', ASCENDING)])
            reports_coll.create_index([('reported_by', ASCENDING)])
            reports_coll.create_index([('is_active', ASCENDING)])
            
            # Supply requests collection
            requests_coll = get_collection('supply_requests')
            requests_coll.create_index([('location', ASCENDING)])
            requests_coll.create_index([('requested_by', ASCENDING)])
            requests_coll.create_index([('status', ASCENDING)])
            
            self.stdout.write(self.style.SUCCESS('Created indexes for all collections'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error creating indexes: {str(e)}'))
        
        # Create initial data if collections are empty
        if locations_coll.count_documents({}) == 0:
            # Create some sample locations
            locations = [
                {'name': 'Downtown Shelter', 'address': '123 Main St, Downtown'},
                {'name': 'Westside Community Center', 'address': '456 West Ave, Westside'},
                {'name': 'Eastside Hospital', 'address': '789 East Blvd, Eastside'},
                {'name': 'Northside School', 'address': '101 North Rd, Northside'}
            ]
            
            location_ids = {}
            for loc in locations:
                result = locations_coll.insert_one(loc)
                location_id = result.inserted_id
                location_ids[loc['name']] = location_id
                
                # Create initial supplies for each location
                supplies_coll.insert_one({
                    'location': location_id,
                    'food_packs': 50,
                    'water_supply': 100,
                    'medical_supply': 30,
                    'last_updated': datetime.now()
                })
            
            self.stdout.write(self.style.SUCCESS('Created sample locations and supplies'))





