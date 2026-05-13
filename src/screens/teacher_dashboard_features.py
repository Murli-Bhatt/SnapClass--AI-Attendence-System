import streamlit as st
from src.database.db import get_teacher_subjects, create_subject, log_attendance, get_attendance_records, get_enrolled_students
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
        for s in subjects:
            subj_id = s['subject_id']
            # Get enrolled students count
            enrolled = get_enrolled_students(subj_id)
            s['enrolled_count'] = len(enrolled)
            
            # Get classes held count (unique timestamps)
            try:
                logs = supabase.table('attendence_logs').select('timestamp').eq('subject_id', subj_id).execute()
                s['classes_held'] = len(set([log['timestamp'] for log in logs.data]))
            except Exception:
                s['classes_held'] = 0

        df = pd.DataFrame(subjects)
        # Reorder and rename columns for display
        df = df[['subject_code', 'name', 'section', 'enrolled_count', 'classes_held']]
        df.columns = ['Subject Code', 'Course Name', 'Section', 'Enrolled Students', 'Classes Held']
        st.dataframe(df, width="stretch", hide_index=True)
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
    
    # Clear state if subject changes
    if "last_selected_subject_id" not in st.session_state:
        st.session_state["last_selected_subject_id"] = selected_subject_id
    elif st.session_state["last_selected_subject_id"] != selected_subject_id:
        if "attendance_summary" in st.session_state:
            st.session_state["attendance_summary"] = None
        if "detected_students" in st.session_state:
            st.session_state["detected_students"] = []
        st.session_state["last_selected_subject_id"] = selected_subject_id
    
    st.markdown("---")
    
    tab1, tab2, tab3 = st.tabs(["📸 Group Photo Upload", "📷 Live Camera", "🎤 Voice Recognition"])
    
    # Initialize session state for detected students
    if "detected_students" not in st.session_state:
        st.session_state["detected_students"] = []
    
    with tab1:
        st.markdown("<p style='color: rgba(255,255,255,0.7);'>Upload a photo of the classroom to automatically log attendance for all recognized faces.</p>", unsafe_allow_html=True)
        
        _, upload_col, _ = st.columns([1, 1.5, 1])
        with upload_col:
            uploaded_files = st.file_uploader("Upload Group Photos (Max 5)", type=["jpg", "jpeg", "png"], accept_multiple_files=True, label_visibility="collapsed")
            images = []
            
            if uploaded_files:
                from src.pipelines.face_pipeline import fix_image_rotation
                if len(uploaded_files) > 5:
                    st.warning("You can only upload up to 5 photos at a time. Only the first 5 will be processed.")
                    uploaded_files = uploaded_files[:5]
                    
                cols = st.columns(len(uploaded_files))
                for idx, u_file in enumerate(uploaded_files):
                    # Fix rotation based on EXIF before processing
                    img = Image.open(u_file)
                    img = fix_image_rotation(img)
                    images.append(img)
                    with cols[idx]:
                        st.markdown('<div style="border-radius: 12px; overflow: hidden; border: 2px solid rgba(168, 85, 247, 0.3); box-shadow: 0 8px 30px rgba(0,0,0,0.5); margin-bottom: 1rem;">', unsafe_allow_html=True)
                        st.image(img, width="stretch")
                        st.markdown('</div>', unsafe_allow_html=True)
                
        if uploaded_files:
            # Show Scan Mode ONLY after upload
            scan_mode_col1, scan_mode_col2 = st.columns([1, 1])
            with scan_mode_col1:
                scan_mode = st.radio(
                    "Scan Quality",
                    options=["Quick Scan (HOG)", "Deep Scan (CNN)"],
                    horizontal=True,
                    help="Quick Scan is faster. Deep Scan is more accurate for tilted/sideways faces.",
                    key="upload_scan_mode"
                )
                mode_key = "quick" if "Quick" in scan_mode else "deep"
            
            _, btn_col, _ = st.columns([1, 1, 1])
            with btn_col:
                analyze_clicked = st.button("Analyze Photos", key="btn_analyze_upload", type="primary", width="stretch")
            
            if analyze_clicked:
                with st.spinner(f"Detecting and recognizing faces in {len(images)} photos..."):
                    all_detected = []
                    has_error = False
                    for idx, img in enumerate(images):
                        img_array = np.array(img.convert("RGB"))
                        res = recognize_multiple_faces(img_array, scan_mode=mode_key)
                        
                        if res["success"]:
                            for match in res["data"]:
                                match["source"] = f"Photo {idx + 1}"
                                all_detected.append(match)
                        else:
                            st.error(res["error"])
                            has_error = True
                            
                    if all_detected or not has_error:
                        # Deduplicate by student_id, keeping highest confidence and aggregating sources
                        deduped = {}
                        for match in all_detected:
                            s_id = match["student_id"]
                            if s_id not in deduped:
                                deduped[s_id] = {
                                    "student_id": s_id,
                                    "confidence": match["confidence"],
                                    "sources": [match["source"]]
                                }
                            else:
                                if match["source"] not in deduped[s_id]["sources"]:
                                    deduped[s_id]["sources"].append(match["source"])
                                if match["confidence"] > deduped[s_id]["confidence"]:
                                    deduped[s_id]["confidence"] = match["confidence"]
                                
                        st.session_state["detected_students"] = list(deduped.values())
                    else:
                        st.session_state["detected_students"] = []
                        
    with tab2:
        st.markdown("<p style='color: rgba(255,255,255,0.7);'>Use your device's camera to capture a photo of the classroom.</p>", unsafe_allow_html=True)
        
        _, cam_col, _ = st.columns([1, 1.5, 1])
        with cam_col:
            camera_file = st.camera_input("Take Picture", label_visibility="collapsed")
        
        if camera_file is not None:
            # Show Scan Mode ONLY after capture
            scan_mode_col1, scan_mode_col2 = st.columns([1, 1])
            with scan_mode_col1:
                cam_scan_mode = st.radio(
                    "Scan Quality",
                    options=["Quick Scan (HOG)", "Deep Scan (CNN)"],
                    horizontal=True,
                    help="Quick Scan is faster. Deep Scan is more accurate for tilted/sideways faces.",
                    key="camera_scan_mode"
                )
                cam_mode_key = "quick" if "Quick" in cam_scan_mode else "deep"
            
            _, cam_btn_col, _ = st.columns([1, 1, 1])
            with cam_btn_col:
                analyze_camera_clicked = st.button("Analyze Picture", key="btn_analyze_camera", type="primary", width="stretch")
                
            if analyze_camera_clicked:
                with st.spinner("Detecting and recognizing faces..."):
                    from src.pipelines.face_pipeline import fix_image_rotation
                    image = Image.open(camera_file)
                    image = fix_image_rotation(image)
                    img_array = np.array(image.convert("RGB"))
                    res = recognize_multiple_faces(img_array, scan_mode=cam_mode_key)
                    
                    if res["success"]:
                        for match in res["data"]:
                            match["sources"] = ["Camera"]
                        st.session_state["detected_students"] = res["data"]
                    else:
                        st.error(res["error"])
                        st.session_state["detected_students"] = []
                        
    with tab3:
        st.markdown("<p style='color: rgba(255,255,255,0.7);'>Verify a student's attendance using their voice.</p>", unsafe_allow_html=True)
        voice_audio = st.audio_input("Record Student Voice")
        
        if voice_audio is not None:
            if st.button("Analyze Voice", key="btn_analyze_voice", type="primary"):
                with st.spinner("Scanning recording for multiple voices..."):
                    from src.pipelines.voice_pipeline import recognize_multiple_voices
                    res = recognize_multiple_voices(voice_audio)
                    if res["success"]:
                        # Now 'res["data"]' is a list of detected students
                        for match in res["data"]:
                            match["sources"] = ["Voice"]
                        st.session_state["detected_students"] = res["data"]
                        st.toast(f"✅ Detected {len(res['data'])} student(s) by voice!", icon="🎤")
                    else:
                        st.error(res["error"])
                        st.session_state["detected_students"] = []
                        
    # Display Results & Submit
    if st.session_state.get("detected_students"):
        st.markdown("---")
        st.markdown("### Attendance Reports")
        st.markdown("<p style='color: rgba(255,255,255,0.7);'>Please review attendance before confirming.</p>", unsafe_allow_html=True)
        
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
                
        # Build DataFrame for Review
        review_data = []
        for match in st.session_state["detected_students"]:
            s_id = match["student_id"]
            s_name = name_map.get(s_id, "Unknown")
            if s_id not in students_to_log:
                students_to_log.append(s_id)
                
            review_data.append({
                "Name": s_name,
                "ID": s_id,
                "Source": ", ".join(match.get("sources", ["Unknown"])),
                "Status": "✅ Present"
            })
            
        import pandas as pd
        if review_data:
            df_review = pd.DataFrame(review_data)
            st.dataframe(df_review, width="stretch", hide_index=True)
            
        st.markdown("<br>", unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Discard", type="secondary", width="stretch"):
                st.session_state["detected_students"] = []
                st.rerun()
        with col2:
            if st.button("Confirm & Save", type="primary", width="stretch"):
                with st.spinner("Saving records to database..."):
                    # Ensure students to log are perfectly unique to prevent multiple records in one session
                    unique_students_to_log = list(set(students_to_log))
                    
                    res = log_attendance(selected_subject_id, unique_students_to_log)
                    if res["success"]:
                        st.toast("Attendance logged successfully!", icon="🎉")
                        
                        # Generate Summary
                        enrolled_students = get_enrolled_students(selected_subject_id)
                        present_ids = set(unique_students_to_log)
                        
                        present_list = []
                        absent_list = []
                        
                        for student in enrolled_students:
                            if student["student_id"] in present_ids:
                                present_list.append(student["name"])
                            else:
                                absent_list.append(student["name"])
                                
                        st.session_state["attendance_summary"] = {
                            "present": present_list,
                            "absent": absent_list
                        }
                        
                        st.session_state["detected_students"] = [] # Clear state after logging
                        st.rerun()
                    else:
                        st.error(f"Failed to log attendance: {res['error']}")
                    
    # Display Summary Card
    if st.session_state.get("attendance_summary"):
        summary = st.session_state["attendance_summary"]
        st.markdown("---")
        st.markdown("### 📊 Attendance Summary")
        
        sum_col1, sum_col2 = st.columns(2)
        with sum_col1:
            st.markdown(f"#### ✅ Present ({len(summary['present'])})")
            if summary['present']:
                for name in summary['present']:
                    st.success(name)
            else:
                st.info("No one present.")
                
        with sum_col2:
            st.markdown(f"#### ❌ Absent ({len(summary['absent'])})")
            if summary['absent']:
                for name in summary['absent']:
                    st.error(name)
            else:
                st.info("Everyone is present!")
                
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Close Summary", key="close_summary", width="stretch"):
            st.session_state["attendance_summary"] = None
            st.rerun()


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
            width="stretch", 
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
