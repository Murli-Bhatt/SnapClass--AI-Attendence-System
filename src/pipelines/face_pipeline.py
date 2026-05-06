import streamlit as st
import numpy as np
from src.database.config import supabase
import json

@st.cache_resource(show_spinner=False)
def load_dlib_models():
    """Load dlib models once and cache them to avoid high latency."""
    import dlib
    import face_recognition_models
    
    # Frontal face detector
    detector = dlib.get_frontal_face_detector()
    # 68-point shape predictor
    predictor = dlib.shape_predictor(face_recognition_models.pose_predictor_model_location())
    # 128D Face Encoder
    face_encoder = dlib.face_recognition_model_v1(face_recognition_models.face_recognition_model_location())
    
    return detector, predictor, face_encoder

def get_robust_faces(image_np, detector):
    """
    Tries multiple strategies to find a face: original, grayscale, downsampled, and contrast-enhanced.
    This handles issues with webcams where the face is too large, too dark, or poorly contrasted.
    """
    import numpy as np
    from PIL import Image, ImageEnhance
    import dlib
    
    # 1. Try original image
    faces = detector(image_np, 0)
    if len(faces) > 0: return faces
    
    faces = detector(image_np, 1)
    if len(faces) > 0: return faces
    
    # 2. Try grayscale
    gray_img = Image.fromarray(image_np).convert('L')
    gray = np.array(gray_img)
    
    faces = detector(gray, 0)
    if len(faces) > 0: return faces
    
    faces = detector(gray, 1)
    if len(faces) > 0: return faces
    
    # 3. Try downsampling (for very large, close-up faces that exceed HOG window size)
    max_size = max(gray_img.width, gray_img.height)
    if max_size > 400:
        scale = 400.0 / max_size
        new_w, new_h = int(gray_img.width * scale), int(gray_img.height * scale)
        small_img = gray_img.resize((new_w, new_h))
        small_gray = np.array(small_img)
        
        small_faces = detector(small_gray, 0)
        if len(small_faces) == 0:
            small_faces = detector(small_gray, 1)
            
        if len(small_faces) > 0:
            faces = dlib.rectangles()
            for f in small_faces:
                left = int(f.left() / scale)
                top = int(f.top() / scale)
                right = int(f.right() / scale)
                bottom = int(f.bottom() / scale)
                faces.append(dlib.rectangle(left, top, right, bottom))
            return faces
            
    # 4. Try slight contrast enhancement
    try:
        enhancer = ImageEnhance.Contrast(gray_img)
        high_contrast = np.array(enhancer.enhance(1.5))
        faces = detector(high_contrast, 0)
        if len(faces) > 0: return faces
    except:
        pass
        
    # 5. Ultimate Fallback: CNN Face Detector (much more robust to angles and tilts)
    try:
        import face_recognition_models
        cnn_detector = dlib.cnn_face_detection_model_v1(face_recognition_models.cnn_face_detector_model_location())
        # CNN detector expects RGB image
        cnn_faces = cnn_detector(image_np, 0)
        if len(cnn_faces) > 0:
            faces = dlib.rectangles()
            for f in cnn_faces:
                # CNN detector returns mmod_rectangle, we need to extract the standard dlib.rectangle
                faces.append(f.rect)
            return faces
    except Exception as e:
        print(f"CNN detector fallback failed: {e}")
        
    return dlib.rectangles()


def get_face_encoding(image_np):
    """
    Detects faces, finds landmarks, and returns the 128D encoding for the first face found.
    Returns None if no face is found.
    """
    detector, predictor, face_encoder = load_dlib_models()
    
    # Run the robust face detector on the image data
    faces = get_robust_faces(image_np, detector)
            
    if len(faces) == 0:
        return None
        
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
    from sklearn.svm import SVC
    
    try:
        # Fetch only necessary columns
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
                if isinstance(embedding, str):
                    embedding = json.loads(embedding)
                    
                X.append(np.array(embedding))
                y.append(row['student_id'])
            except Exception as e:
                print(f"Error parsing embedding for student {row['student_id']}: {e}")
                
    if len(X) == 0:
        return None
        
    # Always use distance-based matching (fallback) because students typically 
    # only have 1 registration photo. SVC requires more samples per class 
    # for proper probability calibration (Platt scaling).
    return {"type": "fallback", "X": X, "y": y}

def recognize_student_face(image_np, tolerance=0.6):
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
        X = np.array(model_data["X"])
        y = model_data["y"]
        
        distances = np.linalg.norm(X - encoding, axis=1)
        min_distance_index = np.argmin(distances)
        
        if distances[min_distance_index] <= tolerance:
            confidence = max(0, 1.0 - distances[min_distance_index])
            return {"success": True, "student_id": y[min_distance_index], "confidence": confidence}
        else:
            return {"success": False, "error": "Face not recognized in the system."}
            
    elif model_data["type"] == "svc":
        clf = model_data["model"]
        encoding_reshaped = encoding.reshape(1, -1)
        
        prediction = clf.predict(encoding_reshaped)
        probabilities = clf.predict_proba(encoding_reshaped)[0]
        max_prob = max(probabilities)
        
        if max_prob >= 0.7: 
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
        
    embedding_list = encoding.tolist()
    
    try:
        response = supabase.table('students').update({
            "face_embedding": embedding_list
        }).eq('student_id', student_id).execute()
        
        get_trained_svc.clear()
        
        return {"success": True, "data": response.data}
    except Exception as e:
        return {"success": False, "error": str(e)}

def recognize_multiple_faces(image_np, tolerance=0.6):
    """
    Detects multiple faces in an image, extracts their encodings, 
    and predicts student IDs for each using the trained SVC logic.
    Returns a list of recognized students.
    """
    detector, predictor, face_encoder = load_dlib_models()
    # Run the robust face detector on the image data
    faces = get_robust_faces(image_np, detector)
            
    if len(faces) == 0:
        return {"success": False, "error": "No faces detected in the image."}
        
    model_data = get_trained_svc()
    if model_data is None:
        return {"success": False, "error": "Database is empty. No faces to compare against."}
        
    results = []
    
    for face in faces:
        bbox = (face.top(), face.right(), face.bottom(), face.left())
        shape = predictor(image_np, face)
        encoding = np.array(face_encoder.compute_face_descriptor(image_np, shape))
        
        if model_data["type"] == "fallback":
            X = np.array(model_data["X"])
            y = model_data["y"]
            
            distances = np.linalg.norm(X - encoding, axis=1)
            min_distance_index = np.argmin(distances)
            
            if distances[min_distance_index] <= tolerance:
                confidence = max(0, 1.0 - distances[min_distance_index])
                results.append({"student_id": y[min_distance_index], "confidence": confidence, "bbox": bbox})
                
        elif model_data["type"] == "svc":
            clf = model_data["model"]
            encoding_reshaped = encoding.reshape(1, -1)
            
            prediction = clf.predict(encoding_reshaped)
            probabilities = clf.predict_proba(encoding_reshaped)[0]
            max_prob = max(probabilities)
            
            if max_prob >= 0.7: 
                results.append({"student_id": prediction[0], "confidence": max_prob, "bbox": bbox})
                
    if len(results) > 0:
        return {"success": True, "data": results}
    else:
        return {"success": False, "error": "Faces were detected, but none were recognized as registered students."}
