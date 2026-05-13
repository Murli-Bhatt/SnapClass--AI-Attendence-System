import streamlit as st
import numpy as np
from src.database.config import supabase
import json

@st.cache_resource(show_spinner=False)
def load_voice_encoder():
    """Load the VoiceEncoder model once and cache it to avoid high latency."""
    from resemblyzer import VoiceEncoder
    return VoiceEncoder()

def get_voice_encoding(audio_input):
    """
    Takes an audio input (file path or file-like object), preprocesses it,
    and returns a 256D voice embedding for the utterance.
    """
    import librosa
    from resemblyzer import preprocess_wav
    
    encoder = load_voice_encoder()
    
    try:
        # Load audio using librosa. It handles file paths and file-like objects.
        wav, source_sr = librosa.load(audio_input, sr=None)
        
        # Preprocess the waveform for Resemblyzer (resampling, normalization, etc.)
        wav_preprocessed = preprocess_wav(wav, source_sr=source_sr)
        
        # Ensure the audio isn't too short or mostly silence
        duration = len(wav_preprocessed) / 16000 # Resemblyzer uses 16k sr
        if duration < 1.2:
            return None
            
        # Compute the 256D vector representing the voice
        voice_encoding = np.array(encoder.embed_utterance(wav_preprocessed))
        
        return voice_encoding
    except Exception as e:
        return None

@st.cache_resource(show_spinner=False)
def get_known_voices():
    """
    Fetches student voice encodings from the database.
    Caches the encodings so we only query the DB ONCE until invalidated.
    """
    try:
        response = supabase.table('students').select('student_id, voice_embedding').execute()
        data = response.data
    except Exception as e:
        return None
        
    X = []
    y = []
    
    for row in data:
        if row.get('voice_embedding') is not None:
            try:
                embedding = row['voice_embedding'] 
                if isinstance(embedding, str):
                    embedding = json.loads(embedding)
                    
                X.append(np.array(embedding))
                y.append(row['student_id'])
            except Exception as e:
                pass
                
    if len(X) == 0:
        return None
        
    return {"X": np.array(X), "y": y}

def recognize_multiple_voices(audio_input, threshold=0.65):
    """
    Scans a long audio file by splitting it into segments of speech (VAD).
    This is much more accurate for detecting 'voice changes' between students.
    """
    import librosa
    from resemblyzer import preprocess_wav
    
    encoder = load_voice_encoder()
    
    try:
        # Load audio
        wav, source_sr = librosa.load(audio_input, sr=None)
        
        # 1. Voice Activity Detection (VAD) - Split audio into non-silent chunks
        # top_db=20 is a standard sensitivity for classroom background noise
        intervals = librosa.effects.split(wav, top_db=25)
        
        if len(intervals) == 0:
            return {"success": False, "error": "No speech detected in the recording."}
            
        known_data = get_known_voices()
        if not known_data:
            return {"success": False, "error": "No students registered."}
            
        norm_X = known_data["X"] / np.linalg.norm(known_data["X"], axis=1, keepdims=True)
        student_ids = known_data["y"]
        
        detected_students = {} # student_id -> highest_confidence
        
        # 2. Analyze each segment
        for start_i, end_i in intervals:
            # Extract the segment
            segment_wav = wav[start_i:end_i]
            
            # Preprocess for Resemblyzer
            segment_processed = preprocess_wav(segment_wav, source_sr=source_sr)
            
            # Skip if too short to be a valid "Present" (less than 0.6s)
            if len(segment_processed) < 16000 * 0.6:
                continue
                
            # If segment is very long (> 4s), it might be multiple people speaking. 
            # We could sub-split, but VAD usually handles this if they pause.
            
            try:
                emb = encoder.embed_utterance(segment_processed)
                norm_emb = emb / np.linalg.norm(emb)
                
                similarities = np.dot(norm_X, norm_emb)
                max_idx = np.argmax(similarities)
                max_sim = similarities[max_idx]
                
                if max_sim >= threshold:
                    s_id = student_ids[max_idx]
                    if s_id not in detected_students or max_sim > detected_students[s_id]:
                        detected_students[s_id] = float(max_sim)
            except:
                continue
                
        if not detected_students:
            return {"success": False, "error": "Voices detected, but none matched registered students."}
            
        # Format results
        results = []
        for s_id, conf in detected_students.items():
            results.append({"student_id": s_id, "confidence": conf})
            
        return {"success": True, "data": results}
        
    except Exception as e:
        return {"success": False, "error": f"Voice analysis failed: {str(e)}"}

def recognize_student_voice(audio_input, threshold=0.65):
    """
    Recognizes the voice in the audio using cosine similarity.
    Threshold set to 0.65 based on user preference.
    """
    encoding = get_voice_encoding(audio_input)
    if encoding is None:
        return {"success": False, "error": "Could not extract voice features. Please try recording again."}
        
    known_data = get_known_voices()
    
    if known_data is None:
        return {"success": False, "error": "Database is empty. No voices to compare against."}
        
    X = known_data["X"]
    y = known_data["y"]
    
    # Normalize vectors to ensure dot product represents cosine similarity
    norm_encoding = encoding / np.linalg.norm(encoding)
    norm_X = X / np.linalg.norm(X, axis=1, keepdims=True)
    
    # Calculate cosine similarities
    similarities = np.dot(norm_X, norm_encoding)
    
    max_sim_index = np.argmax(similarities)
    max_sim = similarities[max_sim_index]
    
    # Check against the increased threshold
    if max_sim >= threshold:
        return {"success": True, "student_id": y[max_sim_index], "confidence": float(max_sim)}
    else:
        return {"success": False, "error": f"Voice not recognized (Confidence: {max_sim:.2f}). Please try again."}

def register_student_voice_in_db(student_id: int, audio_input):
    """
    Extracts encoding from the audio and updates the student's voice_embedding in Supabase.
    """
    encoding = get_voice_encoding(audio_input)
    if encoding is None:
        return {"success": False, "error": "Could not extract voice features. Please try again."}
        
    embedding_list = encoding.tolist()
    
    try:
        response = supabase.table('students').update({
            "voice_embedding": embedding_list
        }).eq('student_id', student_id).execute()
        
        get_known_voices.clear()
        
        return {"success": True, "data": response.data}
    except Exception as e:
        return {"success": False, "error": str(e)}
