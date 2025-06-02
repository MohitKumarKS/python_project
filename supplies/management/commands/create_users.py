from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = 'Creates default admin and user accounts'

    def handle(self, *args, **kwargs):
        # Create admin user if it doesn't exist
        if not User.objects.filter(username='admin').exists():
            admin = User.objects.create_user(
                username='admin',
                password='admin123',
                email='admin@example.com'
            )
            admin.is_staff = True
            admin.is_superuser = True
            admin.save()
            self.stdout.write(self.style.SUCCESS('Admin user created successfully'))
        else:
            self.stdout.write(self.style.WARNING('Admin user already exists'))

        # Create regular user if it doesn't exist
        if not User.objects.filter(username='user1').exists():
            user = User.objects.create_user(
                username='user1',
                password='password123',
                email='user1@example.com'
            )
            user.save()
            self.stdout.write(self.style.SUCCESS('Regular user created successfully'))
        else:
            self.stdout.write(self.style.WARNING('Regular user already exists'))
