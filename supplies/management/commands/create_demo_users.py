from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = 'Creates demo users for the application'

    def handle(self, *args, **kwargs):
        # Create regular user if it doesn't exist
        if not User.objects.filter(username='user1').exists():
            User.objects.create_user(
                username='user1',
                password='password123',
                email='user1@example.com',
                first_name='Regular',
                last_name='User'
            )
            self.stdout.write(self.style.SUCCESS('Regular user created successfully'))
        else:
            self.stdout.write(self.style.WARNING('Regular user already exists'))
            
        # Create admin user if it doesn't exist
        if not User.objects.filter(username='admin').exists():
            admin_user = User.objects.create_user(
                username='admin',
                password='admin123',
                email='admin@example.com',
                first_name='Admin',
                last_name='User'
            )
            admin_user.is_staff = True
            admin_user.is_superuser = True
            admin_user.save()
            self.stdout.write(self.style.SUCCESS('Admin user created successfully'))
        else:
            self.stdout.write(self.style.WARNING('Admin user already exists'))



