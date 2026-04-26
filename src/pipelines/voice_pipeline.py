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
        
        # Compute the 256D vector representing the voice
        voice_encoding = np.array(encoder.embed_utterance(wav_preprocessed))
        
        return voice_encoding
    except Exception as e:
        print(f"Error extracting voice encoding: {e}")
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
        print(f"Error fetching students from db: {e}")
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
                print(f"Error parsing voice embedding for student {row['student_id']}: {e}")
                
    if len(X) == 0:
        return None
        
    return {"X": np.array(X), "y": y}

def recognize_student_voice(audio_input, threshold=0.60):
    """
    Recognizes the voice in the audio using cosine similarity.
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
    
    similarities = np.dot(norm_X, norm_encoding)
    
    max_sim_index = np.argmax(similarities)
    max_sim = similarities[max_sim_index]
    
    if max_sim >= threshold:
        return {"success": True, "student_id": y[max_sim_index], "confidence": max_sim}
    else:
        return {"success": False, "error": f"Voice not recognized (low confidence: {max_sim:.2f}). Please try again."}

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
