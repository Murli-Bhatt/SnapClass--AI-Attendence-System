import bcrypt
from src.database.config import supabase

def hash_password(password: str) -> str:
    """Hashes a password using bcrypt."""
    # Speed up hashing time complexity by explicitly lowering the rounds factor to 4
    salt = bcrypt.gensalt(rounds=4)
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    """Verifies a password against a bcrypt hash."""
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def teacher_exists(username: str) -> bool:
    """Checks if a teacher username already exists in the database."""
    try:
        response = supabase.table('teachers').select('teacher_id').eq('username', username).execute()
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

def create_student(name: str, face_embedding: list, voice_embedding: list = None) -> dict:
    """
    Registers a new student with their face (and optional voice) embedding.
    Returns a dict with 'success' boolean and 'data' or 'error' message.
    """
    data = {
        "name": name,
        "face_embedding": face_embedding,
        "voice_embedding": voice_embedding
    }
    
    try:
        response = supabase.table('students').insert(data).execute()
        return {"success": True, "data": response.data}
    except Exception as e:
        return {"success": False, "error": str(e)}

def get_teacher_subjects(teacher_id: int) -> list:
    """Fetches all subjects registered by a specific teacher."""
    try:
        response = supabase.table('subjects').select('*').eq('teacher_id', teacher_id).execute()
        return response.data
    except Exception as e:
        print(f"Error fetching subjects: {e}")
        return []

def create_subject(subject_code: str, name: str, section: str, teacher_id: int) -> dict:
    """Registers a new subject for a teacher."""
    data = {
        "subject_code": subject_code,
        "name": name,
        "section": section,
        "teacher_id": teacher_id
    }
    try:
        response = supabase.table('subjects').insert(data).execute()
        return {"success": True, "data": response.data}
    except Exception as e:
        return {"success": False, "error": str(e)}

def log_attendance(subject_id: int, student_ids: list, is_present: bool = True) -> dict:
    """Bulk inserts attendance logs for multiple students."""
    from datetime import datetime
    
    if not student_ids:
        return {"success": True, "data": [], "message": "No students to log."}
        
    # Prepare bulk insert data
    now = datetime.utcnow().isoformat()
    data = [
        {
            "subject_id": subject_id,
            "student_id": s_id,
            "is_present": is_present,
            "timestamp": now
        }
        for s_id in student_ids
    ]
    
    try:
        response = supabase.table('attendence_logs').insert(data).execute()
        return {"success": True, "data": response.data}
    except Exception as e:
        return {"success": False, "error": str(e)}

def get_attendance_records(subject_id: int) -> list:
    """
    Fetches attendance logs for a subject, joined with student details.
    Supabase handles joins using foreign key relationships implicitly in select.
    """
    try:
        # Assuming foreign key exists from attendence_logs.student_id -> students.student_id
        # Supabase syntax for inner join is: '*, students(name, student_id)'
        response = supabase.table('attendence_logs') \
            .select('id, timestamp, is_present, student_id, students(name)') \
            .eq('subject_id', subject_id) \
            .order('timestamp', desc=True) \
            .execute()
            
        # Flatten the data for easier use in DataFrames
        flattened_data = []
        for row in response.data:
            student_data = row.get('students') or {}
            student_name = student_data.get('name', f"Unknown (ID: {row.get('student_id')})")
            
            flattened_data.append({
                "id": row.get("id"),
                "timestamp": row.get("timestamp"),
                "student_id": row.get("student_id"),
                "student_name": student_name,
                "is_present": row.get("is_present")
            })
            
        return flattened_data
    except Exception as e:
        print(f"Error fetching attendance records: {e}")
        return []

def get_subject_by_code(subject_code: str) -> dict:
    """Fetches a subject by its code."""
    try:
        response = supabase.table('subjects').select('*').eq('subject_code', subject_code).execute()
        if len(response.data) > 0:
            return {"success": True, "data": response.data[0]}
        else:
            return {"success": False, "error": "Subject not found."}
    except Exception as e:
        return {"success": False, "error": str(e)}

def enroll_student(student_id: int, subject_id: int) -> dict:
    """Enrolls a student in a subject."""
    data = {
        "student_id": student_id,
        "subject_id": subject_id
    }
    try:
        # First check if already enrolled
        check_response = supabase.table('subject_students').select('*').eq('student_id', student_id).eq('subject_id', subject_id).execute()
        if len(check_response.data) > 0:
            return {"success": False, "error": "Already enrolled in this subject."}
            
        response = supabase.table('subject_students').insert(data).execute()
        return {"success": True, "data": response.data}
    except Exception as e:
        return {"success": False, "error": str(e)}

def get_enrolled_students(subject_id: int) -> list:
    """Fetches all students enrolled in a specific subject."""
    try:
        # Join subject_students with students to get names
        response = supabase.table('subject_students') \
            .select('student_id, students(name)') \
            .eq('subject_id', subject_id) \
            .execute()
            
        enrolled = []
        for row in response.data:
            student_data = row.get('students') or {}
            enrolled.append({
                "student_id": row.get("student_id"),
                "name": student_data.get("name", "Unknown")
            })
        return enrolled
    except Exception as e:
        print(f"Error fetching enrolled students: {e}")
        return []

def get_student_attendance_summary(student_id: int) -> list:
    """Fetches a summary of a student's attendance across all their enrolled subjects."""
    try:
        # 1. Get subjects the student is enrolled in
        enrollments = supabase.table('subject_students') \
            .select('subject_id, subjects(subject_code, name)') \
            .eq('student_id', student_id).execute()
            
        summary = []
        for row in enrollments.data:
            subj_id = row['subject_id']
            subj_data = row.get('subjects') or {}
            
            # 2. Get total classes held (unique timestamps for this subject)
            all_logs = supabase.table('attendence_logs').select('timestamp').eq('subject_id', subj_id).execute()
            total_classes = len(set([log['timestamp'] for log in all_logs.data]))
            
            # 3. Get classes attended by this student
            student_logs = supabase.table('attendence_logs').select('id').eq('subject_id', subj_id).eq('student_id', student_id).execute()
            attended_classes = len(student_logs.data)
            
            percentage = (attended_classes / total_classes * 100) if total_classes > 0 else 0
            
            summary.append({
                "Subject Code": subj_data.get('subject_code', 'N/A'),
                "Subject Name": subj_data.get('name', 'N/A'),
                "Total Classes Held": total_classes,
                "Classes Attended": attended_classes,
                "Attendance %": f"{percentage:.1f}%"
            })
            
        return summary
    except Exception as e:
        print(f"Error fetching attendance summary: {e}")
        return []
