from django.core.management.base import BaseCommand
from django.core.management import call_command

class Command(BaseCommand):
    help = 'Setup the entire project (run migrations, create users, initialize MongoDB)'

    def handle(self, *args, **kwargs):
        # Run migrations
        self.stdout.write(self.style.NOTICE('Running migrations...'))
        call_command('migrate')
        
        # Create demo users
        self.stdout.write(self.style.NOTICE('Creating demo users...'))
        call_command('create_demo_users')
        
        # Initialize MongoDB
        self.stdout.write(self.style.NOTICE('Initializing MongoDB...'))
        call_command('init_mongodb')
        
        self.stdout.write(self.style.SUCCESS('Project setup complete!'))
        self.stdout.write(self.style.SUCCESS('You can now run the server with: python manage.py runserver'))