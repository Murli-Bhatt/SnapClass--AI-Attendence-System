import streamlit as st
from src.database.db import get_subject_by_code, enroll_student, get_student_attendance_summary

def render_student_dashboard():
    """Placeholder for the student dashboard."""
    # Check if student is logged in
    if "current_student_id" not in st.session_state:
        st.session_state["current_screen"] = "student"
        st.rerun()

    st.markdown(
        """
        <style>
            .dashboard-header {
                display: flex;
                align-items: center;
                justify-content: space-between;
                margin-bottom: 2rem;
            }
            .dashboard-title h2 {
                margin: 0;
                color: #ffffff;
                font-size: 1.8rem;
                font-weight: 700;
            }
            .dashboard-title p {
                margin: 0;
                color: rgba(255,255,255,0.6);
                font-size: 0.9rem;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
        <div class="dashboard-header">
            <div class="dashboard-title">
                <h2>Welcome to your Dashboard</h2>
                <p>Student ID: {st.session_state["current_student_id"]}</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    
    st.markdown("### Enroll in a Subject")
    st.markdown("Enter the subject code provided by your teacher to enroll in their class.")
    
    with st.container():
        col1, col2 = st.columns([3, 1])
        with col1:
            subject_code = st.text_input("Subject Code", placeholder="e.g. CS101", label_visibility="collapsed")
        with col2:
            enroll_clicked = st.button("Enroll", use_container_width=True, type="primary")
            
        if enroll_clicked:
            if not subject_code.strip():
                st.warning("Please enter a subject code.")
            else:
                with st.spinner("Enrolling..."):
                    subject_res = get_subject_by_code(subject_code.strip())
                    if not subject_res["success"]:
                        st.error(subject_res["error"])
                    else:
                        subject_data = subject_res["data"]
                        subject_id = subject_data["subject_id"]
                        subject_name = subject_data["name"]
                        student_id = st.session_state["current_student_id"]
                        
                        enroll_res = enroll_student(student_id, subject_id)
                        if enroll_res["success"]:
                            st.success(f"Successfully enrolled in {subject_name} ({subject_code})!")
                        else:
                            st.error(enroll_res["error"])
                            
    st.divider()
    
    st.markdown("### 📊 My Attendance")
    with st.spinner("Fetching your attendance records..."):
        attendance_summary = get_student_attendance_summary(st.session_state["current_student_id"])
        
    if attendance_summary:
        import pandas as pd
        df = pd.DataFrame(attendance_summary)
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("You haven't enrolled in any subjects yet, or no classes have been held.")

    st.divider()

    if st.button("Logout", key="student_logout"):
        st.session_state.pop("current_student_id", None)
        st.session_state["current_screen"] = "home"
        st.rerun()
