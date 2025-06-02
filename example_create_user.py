from django.contrib.auth.models import User

# Create a regular user
new_user = User.objects.create_user(
    username='new_username',
    password='new_password',
    email='user@example.com',
    first_name='First',
    last_name='Last'
)

# Create an admin user
new_admin = User.objects.create_user(
    username='new_admin',
    password='admin_password',
    email='admin@example.com',
    first_name='Admin',
    last_name='User'
)
new_admin.is_staff = True
new_admin.is_superuser = True
new_admin.save()