import streamlit as st
import numpy as np
from PIL import Image

from src.database.db import create_student
from src.utils.styles import apply_global_styles, full_screen_spinner

def render_student_screen():
    """Student Portal screen with Face ID login and automated registration."""
    # Apply shared styles
    apply_global_styles()
    
    # Lazy imports for AI logic to keep UI snappy
    from src.pipelines.face_pipeline import recognize_student_face, get_face_encoding, get_trained_svc
    from src.pipelines.voice_pipeline import get_voice_encoding, get_known_voices

    # Initialize states
    if "student_auth_step" not in st.session_state:
        st.session_state["student_auth_step"] = "capture"
    if "temp_face_encoding" not in st.session_state:
        st.session_state["temp_face_encoding"] = None
    if "temp_face_img" not in st.session_state:
        st.session_state["temp_face_img"] = None
        
    step = st.session_state["student_auth_step"]

    st.markdown(
        """
        <style>
            .camera-container-title {
                text-align: center;
                color: #55efc4;
                margin-bottom: 0.5rem;
                font-size: 1.5rem;
                font-weight: 600;
            }
            .camera-container-subtitle {
                text-align: center;
                color: rgba(255,255,255,0.6);
                margin-bottom: 1.5rem;
                font-size: 0.9rem;
            }
            .registration-card {
                background: rgba(45, 52, 54, 0.5);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 12px;
                padding: 2rem;
                margin-top: 1rem;
            }
            .screen-header-icon-student {
                background: linear-gradient(135deg, rgba(0, 184, 148, 0.2), rgba(85, 239, 196, 0.2));
                border: 1px solid rgba(0, 184, 148, 0.2);
            }
        </style>
        """,
        unsafe_allow_html=True,
    )

    if step == "capture":
        st.markdown(
            """
            <div class="screen-header">
                <div class="screen-header-icon screen-header-icon-student">👨‍🎓</div>
                <div class="screen-header-text">
                    <h2>Student Portal</h2>
                    <p>Login securely using Face ID</p>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        
        st.markdown(
            """
            <div class="camera-container-title">📷 Face ID Authentication</div>
            <div class="camera-container-subtitle">Please position your face clearly in the camera view</div>
            """,
            unsafe_allow_html=True,
        )

        col1, col2, col3 = st.columns([1, 1.5, 1])
        with col2:
            img_file_buffer = st.camera_input("Authentication Camera", label_visibility="collapsed")

        if img_file_buffer is not None:
            # Process image
            img = Image.open(img_file_buffer)
            img_array = np.array(img)
            with full_screen_spinner("Analyzing face..."):
                result = recognize_student_face(img_array)
                
            if result.get("success"):
                st.toast("✅ Welcome back!", icon="🎉")
                st.session_state["current_student_id"] = result["student_id"]
                st.session_state["current_screen"] = "student_dashboard"
                st.rerun()
            else:
                # Face not recognized, proceed to registration
                # Extract the raw encoding to save for registration
                encoding = get_face_encoding(img_array)
                if encoding is None:
                    st.toast("❌ Could not detect a clear face. Please try again.", icon="⚠️")
                else:
                    st.toast("⚠️ Face not recognized. Redirecting to registration.", icon="ℹ️")
                    st.session_state["temp_face_encoding"] = encoding
                    st.session_state["temp_face_img"] = img
                    st.session_state["student_auth_step"] = "register"
                    st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("← Back to Home", key="student_back"):
            st.session_state["current_screen"] = "home"
            st.rerun()

    elif step == "register":
        st.markdown(
            """
            <div class="screen-header">
                <div class="screen-header-icon">📝</div>
                <div class="screen-header-text">
                    <h2>New Student Registration</h2>
                    <p>Enroll your details to complete setup</p>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        
        st.info("Your face has been successfully captured for enrollment.")
        
        with st.container(border=True):
            st.markdown("#### Enrollment Details")
            st.markdown("<span style='color: rgba(255,255,255,0.6); font-size: 0.9rem;'>You are enrolling using your face. Optionally add your voice for extra security.</span><br><br>", unsafe_allow_html=True)
            
            reg_col1, reg_col2 = st.columns([1, 2], gap="large")
            
            with reg_col1:
                if st.session_state["temp_face_img"]:
                    st.image(st.session_state["temp_face_img"], width="stretch", caption="Captured Photo")
                    
            with reg_col2:
                name = st.text_input("Full Name", placeholder="e.g. John Doe")
                
                st.markdown("<br>", unsafe_allow_html=True)
                enroll_voice = st.toggle("🎤 Optional: Enroll Voice for Multi-Factor Authentication")
                
                voice_audio = None
                if enroll_voice:
                    st.markdown("<div style='margin-bottom: 0.5rem; color: rgba(255,255,255,0.7); font-size: 0.9rem;'>Please say your full name clearly:</div>", unsafe_allow_html=True)
                    voice_audio = st.audio_input("Record Voice")
                    
        st.markdown("<br>", unsafe_allow_html=True)
        
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("Cancel & Go Back", width="stretch"):
                st.session_state["temp_face_encoding"] = None
                st.session_state["student_auth_step"] = "capture"
                st.rerun()
        with col2:
            if st.button("Complete Registration", type="primary", width="stretch"):
                if not name.strip():
                    st.toast("⚠️ Please enter your full name.", icon="⚠️")
                else:
                    voice_emb_list = None
                    if enroll_voice:
                        if voice_audio is None:
                            st.toast("⚠️ Please record your voice or disable the option.", icon="⚠️")
                            st.stop()
                        else:
                            with full_screen_spinner("Processing voice..."):
                                voice_emb = get_voice_encoding(voice_audio)
                                if voice_emb is None:
                                    st.toast("❌ Could not extract voice features. Try recording again.", icon="❌")
                                    st.stop()
                                voice_emb_list = voice_emb.tolist()
                                
                    # Proceed to save in DB
                    with full_screen_spinner("Enrolling student..."):
                        face_emb_list = st.session_state["temp_face_encoding"].tolist()
                        res = create_student(name, face_emb_list, voice_emb_list)
                        
                        if res["success"]:
                            # Invalidate model caches so they retrain automatically next time
                            get_trained_svc.clear()
                            get_known_voices.clear()
                            
                            st.toast("✅ Registration complete! Logging you in...", icon="🎉")
                            
                            # Log them in automatically if possible
                            data = res.get("data")
                            if data and len(data) > 0 and "student_id" in data[0]:
                                st.session_state["current_student_id"] = data[0]["student_id"]
                                st.session_state["current_screen"] = "student_dashboard"
                            else:
                                # Fallback if no data returned
                                st.session_state["student_auth_step"] = "capture"
                            
                            st.rerun()
                        else:
                            st.toast(f"❌ Error during registration: {res.get('error')}", icon="❌")
