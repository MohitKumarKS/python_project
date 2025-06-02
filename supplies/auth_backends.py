from django.contrib.auth.backends import ModelBackend

# Use Django's default authentication backend
class CustomAuthBackend(ModelBackend):
    """
    Standard Django authentication
    """
    pass
