import streamlit as st

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
    
    st.info("🚧 Dashboard under construction. Your features will appear here soon!")

    if st.button("Logout", key="student_logout"):
        st.session_state.pop("current_student_id", None)
        st.session_state["current_screen"] = "home"
        st.rerun()
