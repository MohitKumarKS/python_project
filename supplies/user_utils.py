from .mongodb_utils import get_collection
import bcrypt

def create_mongodb_user(username, password, is_staff=False, is_superuser=False, email=None):
    """
    Create a new user in MongoDB
    """
    users_coll = get_collection('users')
    if users_coll is None:
        return False
    
    # Check if user already exists
    if users_coll.find_one({'username': username}):
        return False
    
    # Hash password
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    # Create user document
    user_doc = {
        'username': username,
        'password': hashed_password,
        'is_staff': is_staff,
        'is_superuser': is_superuser,
        'email': email
    }
    
    # Insert user
    result = users_coll.insert_one(user_doc)
    return result.inserted_id is not None