import streamlit as st
from src.database.db import get_teacher_subjects, create_subject, log_attendance, get_attendance_records
from src.pipelines.face_pipeline import recognize_multiple_faces
from src.pipelines.voice_pipeline import recognize_student_voice
from src.database.config import supabase

def handle_add_subject(teacher_id):
    code = st.session_state.get("add_subj_code", "").strip()
    sec = st.session_state.get("add_subj_sec", "").strip()
    name = st.session_state.get("add_subj_name", "").strip()
    
    if code and name and sec:
        res = create_subject(code, name, sec, teacher_id)
        if res["success"]:
            st.toast(f"Subject {code} registered successfully!", icon="✅")
        else:
            st.toast(f"Failed to register subject: {res.get('error')}", icon="❌")
    else:
        st.toast("Please fill in all fields.", icon="⚠️")

def render_manage_subject(teacher_id):
    import pandas as pd
    
    st.markdown("### Existing Subjects")
    subjects = get_teacher_subjects(teacher_id)
    
    if subjects:
        df = pd.DataFrame(subjects)
        # Reorder and rename columns for display
        df = df[['subject_code', 'name', 'section']]
        df.columns = ['Subject Code', 'Course Name', 'Section']
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("You haven't registered any subjects yet.")
        
    st.markdown("---")
    st.markdown("### Add New Subject")
    
    with st.form("add_subject_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            st.text_input("Subject Code (e.g., CS101)", key="add_subj_code")
            st.text_input("Section (e.g., A)", key="add_subj_sec")
        with col2:
            st.text_input("Course Name (e.g., Intro to Computer Science)", key="add_subj_name")
            
        st.form_submit_button(
            "Register Subject", 
            type="primary", 
            on_click=handle_add_subject, 
            args=(teacher_id,)
        )


def render_take_attendance(teacher_id):
    import numpy as np
    from PIL import Image
    
    subjects = get_teacher_subjects(teacher_id)
    
    if not subjects:
        st.warning("Please register a subject first from the 'Manage Subject' tab.")
        return
        
    subject_options = {f"{s['subject_code']} - {s['name']} (Sec {s['section']})": s['subject_id'] for s in subjects}
    
    selected_subject_name = st.selectbox("Select Subject", options=list(subject_options.keys()))
    selected_subject_id = subject_options[selected_subject_name]
    
    st.markdown("---")
    
    tab1, tab2, tab3 = st.tabs(["📸 Group Photo Upload", "📷 Live Camera", "🎤 Voice Recognition"])
    
    # Initialize session state for detected students
    if "detected_students" not in st.session_state:
        st.session_state["detected_students"] = []
    
    with tab1:
        st.markdown("<p style='color: rgba(255,255,255,0.7);'>Upload a photo of the classroom to automatically log attendance for all recognized faces.</p>", unsafe_allow_html=True)
        
        st.markdown(
            """
            <style>
            /* Make the file uploader dropzone much shorter and compact */
            div[data-testid="stFileUploader"] section {
                padding: 10px !important;
                min-height: 80px !important;
            }
            div[data-testid="stFileUploader"] section > div {
                gap: 5px;
            }
            /* Force uploaded image preview to match camera dimensions */
            div[data-testid="stImage"] img {
                aspect-ratio: 16/9 !important;
                object-fit: cover !important;
                max-height: 350px !important;
            }
            </style>
            """, 
            unsafe_allow_html=True
        )
        
        _, upload_col, _ = st.columns([1, 1.5, 1])
        with upload_col:
            uploaded_file = st.file_uploader("Upload Group Photo", type=["jpg", "jpeg", "png"], label_visibility="collapsed")
            
            if uploaded_file is not None:
                image = Image.open(uploaded_file)
                st.markdown('<div style="border-radius: 12px; overflow: hidden; border: 2px solid rgba(168, 85, 247, 0.3); box-shadow: 0 8px 30px rgba(0,0,0,0.5); margin-bottom: 1rem;">', unsafe_allow_html=True)
                st.image(image, use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)
                
        if uploaded_file is not None:
            _, btn_col, _ = st.columns([1, 1, 1])
            with btn_col:
                analyze_clicked = st.button("Analyze Photo", key="btn_analyze_upload", type="primary", use_container_width=True)
            
            if analyze_clicked:
                with st.spinner("Detecting and recognizing faces..."):
                    img_array = np.array(image.convert("RGB")) # Ensure RGB
                    res = recognize_multiple_faces(img_array)
                    
                    if res["success"]:
                        st.session_state["detected_students"] = res["data"]
                    else:
                        st.error(res["error"])
                        st.session_state["detected_students"] = []
                        
    with tab2:
        st.markdown("<p style='color: rgba(255,255,255,0.7);'>Use your device's camera to capture a photo of the classroom.</p>", unsafe_allow_html=True)
        
        _, cam_col, _ = st.columns([1, 1.5, 1])
        with cam_col:
            camera_file = st.camera_input("Take Picture", label_visibility="collapsed")
        
        if camera_file is not None:
            _, cam_btn_col, _ = st.columns([1, 1, 1])
            with cam_btn_col:
                analyze_camera_clicked = st.button("Analyze Picture", key="btn_analyze_camera", type="primary", use_container_width=True)
                
            if analyze_camera_clicked:
                with st.spinner("Detecting and recognizing faces..."):
                    image = Image.open(camera_file)
                    img_array = np.array(image.convert("RGB"))
                    res = recognize_multiple_faces(img_array)
                    
                    if res["success"]:
                        st.session_state["detected_students"] = res["data"]
                    else:
                        st.error(res["error"])
                        st.session_state["detected_students"] = []
                        
    with tab3:
        st.markdown("<p style='color: rgba(255,255,255,0.7);'>Verify a student's attendance using their voice.</p>", unsafe_allow_html=True)
        voice_audio = st.audio_input("Record Student Voice")
        
        if voice_audio is not None:
            if st.button("Analyze Voice", key="btn_analyze_voice", type="primary"):
                with st.spinner("Recognizing voice..."):
                    res = recognize_student_voice(voice_audio)
                    if res["success"]:
                        # Format it to match the list structure of face detection
                        st.session_state["detected_students"] = [{"student_id": res["student_id"], "confidence": res["confidence"]}]
                    else:
                        st.error(res["error"])
                        st.session_state["detected_students"] = []
                        
    # Display Results & Submit
    if st.session_state.get("detected_students"):
        st.markdown("---")
        st.markdown("### Recognized Students")
        
        students_to_log = []
        student_ids = [match["student_id"] for match in st.session_state["detected_students"]]
        
        # Fetch names for these IDs
        name_map = {}
        if student_ids:
            try:
                # Use in_ for array filtering
                name_res = supabase.table('students').select('student_id, name').in_('student_id', student_ids).execute()
                name_map = {row['student_id']: row['name'] for row in name_res.data}
            except Exception as e:
                print(f"Error fetching names: {e}")
                
        # Use a nice container to display them
        for match in st.session_state["detected_students"]:
            s_id = match["student_id"]
            s_name = name_map.get(s_id, "Unknown")
            # Avoid logging duplicates if the same face was detected twice
            if s_id not in students_to_log:
                students_to_log.append(s_id)
                st.success(f"✅ Recognized: **{s_name}** (ID: {s_id}) - Confidence: {match['confidence']:.2f}")
            
        st.markdown("<br>", unsafe_allow_html=True)
        
        if st.button("Confirm & Log Attendance", type="primary", use_container_width=True):
            with st.spinner("Saving records to database..."):
                res = log_attendance(selected_subject_id, students_to_log)
                if res["success"]:
                    st.toast("Attendance logged successfully!", icon="🎉")
                    st.session_state["detected_students"] = [] # Clear state after logging
                    st.rerun()
                else:
                    st.error(f"Failed to log attendance: {res['error']}")


def render_attendance_record(teacher_id):
    import pandas as pd
    
    subjects = get_teacher_subjects(teacher_id)
    
    if not subjects:
        st.warning("Please register a subject first from the 'Manage Subject' tab.")
        return
        
    subject_options = {f"{s['subject_code']} - {s['name']} (Sec {s['section']})": s['subject_id'] for s in subjects}
    
    selected_subject_name = st.selectbox("Select Subject to View Records", options=list(subject_options.keys()))
    selected_subject_id = subject_options[selected_subject_name]
    
    st.markdown("---")
    
    with st.spinner("Fetching attendance records..."):
        records = get_attendance_records(selected_subject_id)
        
    if records:
        df = pd.DataFrame(records)
        
        # Format the timestamp
        df['timestamp'] = pd.to_datetime(df['timestamp']).dt.strftime('%Y-%m-%d %I:%M %p')
        
        # Reorder and rename for UI
        display_df = df[['timestamp', 'student_name', 'student_id', 'is_present']]
        display_df.columns = ['Date & Time', 'Student Name', 'Student ID', 'Present']
        
        st.dataframe(
            display_df, 
            use_container_width=True, 
            hide_index=True,
            column_config={
                "Present": st.column_config.CheckboxColumn("Present", default=True)
            }
        )
        
        # Summary Stats
        total_logs = len(df)
        unique_students = df['student_id'].nunique()
        
        st.markdown(
            f"""
            <div style="display: flex; gap: 20px; margin-top: 1rem;">
                <div style="background: rgba(168, 85, 247, 0.1); padding: 15px 20px; border-radius: 10px; border: 1px solid rgba(168, 85, 247, 0.3);">
                    <span style="color: rgba(255,255,255,0.6); font-size: 0.9rem;">Total Records</span><br>
                    <span style="font-size: 1.5rem; font-weight: 700; color: #fff;">{total_logs}</span>
                </div>
                <div style="background: rgba(0, 184, 148, 0.1); padding: 15px 20px; border-radius: 10px; border: 1px solid rgba(0, 184, 148, 0.3);">
                    <span style="color: rgba(255,255,255,0.6); font-size: 0.9rem;">Unique Students</span><br>
                    <span style="font-size: 1.5rem; font-weight: 700; color: #fff;">{unique_students}</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
        
    else:
        st.info("No attendance records found for this subject.")
