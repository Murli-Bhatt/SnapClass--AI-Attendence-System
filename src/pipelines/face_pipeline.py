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
    
    # CNN detector (for Deep Scan)
    cnn_detector = dlib.cnn_face_detection_model_v1(face_recognition_models.cnn_face_detector_model_location())
    
    return detector, predictor, face_encoder, cnn_detector

def fix_image_rotation(image):
    """
    Corrects image orientation using EXIF metadata (standard for mobile photos).
    Takes a PIL Image and returns a PIL Image.
    """
    from PIL import ImageOps
    return ImageOps.exif_transpose(image)

MAX_DETECTION_DIM = 1024

def get_robust_faces(image_np, detector, cnn_detector, scan_mode="quick"):
    """
    Detects faces based on the selected mode:
    - quick: HOG detector (fast, CPU)
    - deep: CNN detector (highly accurate, handles angles/tilts)
    
    Handles high-resolution images by downsampling for detection and 
    scaling coordinates back to the original size.
    """
    import dlib
    from PIL import Image
    
    # Calculate scaling factor for high-resolution images
    h, w = image_np.shape[:2]
    max_dim = max(h, w)
    scale = 1.0
    detect_image_np = image_np
    
    if max_dim > MAX_DETECTION_DIM:
        scale = MAX_DETECTION_DIM / max_dim
        new_w = int(w * scale)
        new_h = int(h * scale)
        
        # Resize for faster detection
        img_pil = Image.fromarray(image_np)
        img_pil = img_pil.resize((new_w, new_h), Image.Resampling.LANCZOS)
        detect_image_np = np.array(img_pil)
    
    faces = dlib.rectangles()
    
    if scan_mode == "quick":
        # Try HOG detector (multi-scale)
        faces = detector(detect_image_np, 0)
        if len(faces) == 0:
            faces = detector(detect_image_np, 1) # One upsample for smaller faces
            
    elif scan_mode == "deep":
        # Try CNN detector
        try:
            cnn_faces = cnn_detector(detect_image_np, 1)
            for f in cnn_faces:
                faces.append(f.rect)
        except Exception as e:
            pass
            # Fallback to HOG if CNN fails
            faces = detector(detect_image_np, 1)
            
    # Rescale rectangles back to original image dimensions
    if scale != 1.0:
        inv_scale = 1.0 / scale
        final_faces = dlib.rectangles()
        for rect in faces:
            final_faces.append(dlib.rectangle(
                int(rect.left() * inv_scale),
                int(rect.top() * inv_scale),
                int(rect.right() * inv_scale),
                int(rect.bottom() * inv_scale)
            ))
        return final_faces
            
    return faces


def get_face_encoding(image_np, scan_mode="quick"):
    """
    Detects faces, finds landmarks, and returns the 128D encoding for the first face found.
    """
    detector, predictor, face_encoder, cnn_detector = load_dlib_models()
    
    faces = get_robust_faces(image_np, detector, cnn_detector, scan_mode=scan_mode)
            
    if len(faces) == 0:
        return None
        
    shape = predictor(image_np, faces[0])
    face_encoding = np.array(face_encoder.compute_face_descriptor(image_np, shape))
    
    return face_encoding

@st.cache_resource(show_spinner=False)
def get_trained_svc():
    """
    Fetches student encodings from the database and trains an SVM model.
    Uses data augmentation (Gaussian noise) to expand single samples into clusters.
    """
    from sklearn.svm import SVC
    
    try:
        response = supabase.table('students').select('student_id, face_embedding').execute()
        data = response.data
    except Exception as e:
        return None
        
    X_raw = []
    y_raw = []
    
    for row in data:
        if row.get('face_embedding') is not None:
            try:
                embedding = row['face_embedding'] 
                if isinstance(embedding, str):
                    embedding = json.loads(embedding)
                    
                X_raw.append(np.array(embedding))
                y_raw.append(row['student_id'])
            except Exception as e:
                pass
                
    if len(X_raw) == 0:
        return None
        
    # Check for Fallback: If only one student is registered
    unique_students = list(set(y_raw))
    if len(unique_students) < 2:
        return {"type": "fallback", "X": X_raw, "y": y_raw}
        
    # Data Augmentation: Expand 1 sample into 10 per student
    X_aug = []
    y_aug = []
    noise_level = 0.01
    samples_per_student = 10
    
    for emb, s_id in zip(X_raw, y_raw):
        # Original sample
        X_aug.append(emb)
        y_aug.append(s_id)
        # Synthetic samples with small Gaussian noise
        for _ in range(samples_per_student - 1):
            noise = np.random.normal(0, noise_level, emb.shape)
            X_aug.append(emb + noise)
            y_aug.append(s_id)
            
    # Train SVM
    clf = SVC(kernel='linear', probability=True)
    clf.fit(X_aug, y_aug)
    
    return {"type": "svc", "model": clf}

def recognize_student_face(image_np, scan_mode="quick", tolerance=0.6):
    """
    Recognizes the face using the trained SVM (or fallback distance).
    """
    encoding = get_face_encoding(image_np, scan_mode=scan_mode)
    if encoding is None:
        return {"success": False, "error": "No face detected in the image."}
        
    model_data = get_trained_svc()
    if model_data is None:
        return {"success": False, "error": "Database is empty."}
        
    if model_data["type"] == "fallback":
        # Single student fallback (distance based)
        X = np.array(model_data["X"])
        y = model_data["y"]
        distances = np.linalg.norm(X - encoding, axis=1)
        min_idx = np.argmin(distances)
        if distances[min_idx] <= tolerance:
            return {"success": True, "student_id": y[min_idx], "confidence": 1.0 - distances[min_idx]}
        return {"success": False, "error": "Face not recognized."}
            
    elif model_data["type"] == "svc":
        clf = model_data["model"]
        encoding_reshaped = encoding.reshape(1, -1)
        prediction = clf.predict(encoding_reshaped)
        probs = clf.predict_proba(encoding_reshaped)[0]
        max_prob = max(probs)
        
        if max_prob >= 0.65: # Confidence threshold for SVM
            return {"success": True, "student_id": prediction[0], "confidence": max_prob}
        return {"success": False, "error": "Face not recognized (low confidence)."}

def register_student_face_in_db(student_id: int, image_np):
    """
    Extracts encoding from the image and updates the student's face_embedding in Supabase.
    Uses Quick Scan for registration to ensure high quality (HOG prefers upright, clear faces).
    """
    encoding = get_face_encoding(image_np, scan_mode="quick")
    if encoding is None:
        return {"success": False, "error": "No face detected in the image. Please try again."}
        
    try:
        supabase.table('students').update({
            "face_embedding": encoding.tolist()
        }).eq('student_id', student_id).execute()
        get_trained_svc.clear()
        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}

def recognize_multiple_faces(image_np, scan_mode="quick", tolerance=0.6):
    """
    Detects multiple faces in an image and recognizes them.
    """
    detector, predictor, face_encoder, cnn_detector = load_dlib_models()
    faces = get_robust_faces(image_np, detector, cnn_detector, scan_mode=scan_mode)
            
    if len(faces) == 0:
        return {"success": False, "error": "No faces detected in the image."}
        
    model_data = get_trained_svc()
    if model_data is None:
        return {"success": False, "error": "Database is empty."}
        
    results = []
    for face in faces:
        bbox = (face.top(), face.right(), face.bottom(), face.left())
        shape = predictor(image_np, face)
        encoding = np.array(face_encoder.compute_face_descriptor(image_np, shape))
        
        if model_data["type"] == "fallback":
            X = np.array(model_data["X"])
            y = model_data["y"]
            distances = np.linalg.norm(X - encoding, axis=1)
            min_idx = np.argmin(distances)
            if distances[min_idx] <= tolerance:
                results.append({"student_id": y[min_idx], "confidence": 1.0 - distances[min_idx], "bbox": bbox})
                
        elif model_data["type"] == "svc":
            clf = model_data["model"]
            encoding_reshaped = encoding.reshape(1, -1)
            prediction = clf.predict(encoding_reshaped)
            probs = clf.predict_proba(encoding_reshaped)[0]
            max_prob = max(probs)
            if max_prob >= 0.65:
                results.append({"student_id": prediction[0], "confidence": max_prob, "bbox": bbox})
                
    if len(results) > 0:
        return {"success": True, "data": results}
    return {"success": False, "error": "Faces detected, but none recognized."}
