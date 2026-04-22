import streamlit as st
import numpy as np
from PIL import Image

def render_student_screen():
    """Student Portal screen with Face ID login."""
    st.markdown(
        """
        <style>
            .screen-header {
                display: flex;
                align-items: center;
                gap: 1rem;
                margin-bottom: 2rem;
            }
            .screen-header-icon {
                width: 50px;
                height: 50px;
                background: linear-gradient(135deg, rgba(0, 184, 148, 0.2), rgba(85, 239, 196, 0.2));
                border: 1px solid rgba(0, 184, 148, 0.2);
                border-radius: 14px;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 24px;
            }
            .screen-header-text h2 {
                margin: 0;
                color: #ffffff;
                font-size: 1.5rem;
                font-weight: 700;
            }
            .screen-header-text p {
                margin: 0;
                color: rgba(255,255,255,0.4);
                font-size: 0.85rem;
            }
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
        </style>
        <div class="screen-header">
            <div class="screen-header-icon">👨‍🎓</div>
            <div class="screen-header-text">
                <h2>Student Portal</h2>
                <p>Login securely using Face ID</p>
            </div>
        </div>
        
        <div class="camera-container-title">📷 Face ID Authentication</div>
        <div class="camera-container-subtitle">Please position your face clearly in the camera view</div>
        """,
        unsafe_allow_html=True,
    )

    # Use columns to make the camera component smaller and centered
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        img_file_buffer = st.camera_input("Authentication Camera", label_visibility="collapsed")

    if img_file_buffer is not None:
        # Convert the captured image to a PIL Image
        img = Image.open(img_file_buffer)

        # Convert PIL Image to a numpy array for further processing (e.g., face recognition)
        img_array = np.array(img)
        
        st.success("✅ Face captured successfully!")
        st.info("Image converted to numpy array. Ready for facial recognition backend operations.")

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("← Back to Home", key="student_back"):
        st.session_state["current_screen"] = "home"
        st.rerun()
