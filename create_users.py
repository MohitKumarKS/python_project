from django.contrib.auth.models import User

# Check if admin exists, if not create it
if not User.objects.filter(username='admin').exists():
    admin = User.objects.create_user(
        username='admin',
        password='admin123',
        email='admin@example.com'
    )
    admin.is_staff = True
    admin.is_superuser = True
    admin.save()
    print("Admin user created")
else:
    print("Admin user already exists")

# Check if regular user exists, if not create it
if not User.objects.filter(username='user1').exists():
    user = User.objects.create_user(
        username='user1',
        password='password123',
        email='user1@example.com'
    )
    user.save()
    print("Regular user created")
else:
    print("Regular user already exists")

exit()