import streamlit as st
import numpy as np
import dlib
import face_recognition_models
from sklearn.svm import SVC
from src.database.config import supabase
import json

@st.cache_resource(show_spinner=False)
def load_dlib_models():
    """Load dlib models once and cache them to avoid high latency."""
    # Frontal face detector
    detector = dlib.get_frontal_face_detector()
    # 68-point shape predictor
    predictor = dlib.shape_predictor(face_recognition_models.pose_predictor_model_location())
    # 128D Face Encoder
    face_encoder = dlib.face_recognition_model_v1(face_recognition_models.face_recognition_model_location())
    
    return detector, predictor, face_encoder

def get_face_encoding(image_np):
    """
    Detects faces, finds landmarks, and returns the 128D encoding for the first face found.
    Returns None if no face is found.
    """
    detector, predictor, face_encoder = load_dlib_models()
    
    # Run the HOG face detector on the image data
    # image_np is expected to be an RGB numpy array (which st.camera_input -> PIL -> np.array produces)
    faces = detector(image_np, 1)
    
    if len(faces) == 0:
        return None
        
    # We only take the first face found (index 0) for simplicity.
    shape = predictor(image_np, faces[0])
    
    # Compute the 128D vector representing the face.
    face_encoding = np.array(face_encoder.compute_face_descriptor(image_np, shape))
    
    return face_encoding

@st.cache_resource(show_spinner=False)
def get_trained_svc():
    """
    Fetches student encodings from the database and trains an SVC model.
    Caches the trained model so we only query the DB & train ONCE until invalidated.
    """
    try:
        # Fetch the student ID and their face embedding (JSONB)
        response = supabase.table('students').select('student_id, face_embedding').execute()
        data = response.data
    except Exception as e:
        print(f"Error fetching students from db: {e}")
        return None
        
    X = []
    y = []
    
    for row in data:
        if row.get('face_embedding') is not None:
            try:
                embedding = row['face_embedding'] 
                # Supabase python client usually parses JSONB into a python list automatically
                if isinstance(embedding, str):
                    embedding = json.loads(embedding)
                    
                X.append(np.array(embedding))
                y.append(row['student_id'])
            except Exception as e:
                print(f"Error parsing embedding for student {row['student_id']}: {e}")
                
    if len(X) == 0:
        return None
        
    unique_classes = len(set(y))
    
    # SVC requires at least 2 distinct classes (2 distinct students) to train
    if unique_classes < 2:
        # Return a fallback dictionary mapped system
        return {"type": "fallback", "X": X, "y": y}
        
    # We have >= 2 students, so let's train the SVC!
    clf = SVC(kernel='linear', probability=True)
    clf.fit(X, y)
    return {"type": "svc", "model": clf}

def recognize_student_face(image_np, tolerance=0.5):
    """
    Recognizes the face in the image array using the trained SVC logic.
    """
    encoding = get_face_encoding(image_np)
    if encoding is None:
        return {"success": False, "error": "No face detected in the image. Please position yourself clearly."}
        
    model_data = get_trained_svc()
    
    if model_data is None:
        return {"success": False, "error": "Database is empty. No faces to compare against."}
        
    if model_data["type"] == "fallback":
        # Cannot use SVC (< 2 students). Fallback to Euclidean array distance comparison
        X = np.array(model_data["X"])
        y = model_data["y"]
        
        # Calculate distances from the captured encoding to all known encodings
        distances = np.linalg.norm(X - encoding, axis=1)
        min_distance_index = np.argmin(distances)
        
        if distances[min_distance_index] <= tolerance:
            confidence = max(0, 1.0 - distances[min_distance_index])
            return {"success": True, "student_id": y[min_distance_index], "confidence": confidence}
        else:
            return {"success": False, "error": "Face not recognized in the system."}
            
    elif model_data["type"] == "svc":
        clf = model_data["model"]
        # Reshape to a 2D array for the scikit-learn model
        encoding_reshaped = encoding.reshape(1, -1)
        
        # Predict class and probabilities
        prediction = clf.predict(encoding_reshaped)
        probabilities = clf.predict_proba(encoding_reshaped)[0]
        max_prob = max(probabilities)
        
        if max_prob >= 0.7:  # 70% confidence threshold
            return {"success": True, "student_id": prediction[0], "confidence": max_prob}
        else:
            return {"success": False, "error": f"Face not recognized (low confidence: {max_prob:.2f}). Please try again."}

def register_student_face_in_db(student_id: int, image_np):
    """
    Extracts encoding from the image and updates the student's face_embedding in Supabase.
    Invalidates the @st.cache_resource model so it's fresh for next login.
    """
    encoding = get_face_encoding(image_np)
    if encoding is None:
        return {"success": False, "error": "No face detected in the image. Please try again."}
        
    # Convert numpy array to list for JSON serialization in Supabase
    embedding_list = encoding.tolist()
    
    try:
        # Update the student's record with the face embedding JSONB data
        # Note: `student_id` should be of type matching schema (int8)
        response = supabase.table('students').update({
            "face_embedding": embedding_list
        }).eq('student_id', student_id).execute()
        
        # ── CRITICAL STEP ── 
        # Clear the cached SVC model so that on the next recognition attempt,
        # it fetches the fresh data and retrains the model with the new student.
        get_trained_svc.clear()
        
        return {"success": True, "data": response.data}
    except Exception as e:
        return {"success": False, "error": str(e)}
