import bcrypt
from src.database.config import supabase

def hash_password(password: str) -> str:
    """Hashes a password using bcrypt."""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    """Verifies a password against a bcrypt hash."""
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def teacher_exists(username: str) -> bool:
    """Checks if a teacher username already exists in the database."""
    try:
        response = supabase.table('teachers').select('id').eq('username', username).execute()
        return len(response.data) > 0
    except Exception as e:
        print(f"Error checking if teacher exists: {e}")
        return False

def register_teacher(username: str, password: str, **kwargs) -> dict:
    """
    Registers a new teacher. 
    Returns a dict with 'success' boolean and 'data' or 'error' message.
    """
    # 1. Check if teacher name already exists
    if teacher_exists(username):
        return {"success": False, "error": "Teacher username already exists."}
    
    # 2. Hash the password using bcrypt
    hashed_password = hash_password(password)
    
    # 3. Prepare data for insert
    data = {
        "username": username,
        "password": hashed_password,
        **kwargs  # Allows passing extra fields like name, etc.
    }
    
    # 4. Insert into Supabase
    try:
        response = supabase.table('teachers').insert(data).execute()
        return {"success": True, "data": response.data}
    except Exception as e:
        return {"success": False, "error": str(e)}

def login_teacher(username: str, password: str) -> dict:
    """
    Logs in a teacher by verifying username and password.
    Returns a dict with 'success' boolean and 'data' or 'error' message.
    """
    try:
        # Fetch the teacher by username
        response = supabase.table('teachers').select('*').eq('username', username).execute()
        
        if len(response.data) == 0:
            return {"success": False, "error": "Teacher not found."}
            
        teacher = response.data[0]
        
        # Verify the password
        if verify_password(password, teacher['password']):
            # Remove the password from the dictionary before returning it for security
            teacher.pop('password', None)
            return {"success": True, "data": teacher}
        else:
            return {"success": False, "error": "Incorrect password."}
    except Exception as e:
        return {"success": False, "error": str(e)}
