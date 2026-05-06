import streamlit as st
from src.database.db import register_teacher, login_teacher
from src.utils.styles import apply_global_styles
from src.screens.teacher_dashboard_features import render_manage_subject, render_take_attendance, render_attendance_record

def render_teacher_screen():
    # Apply shared styles
    apply_global_styles()

    # ── Initialize State ──
    if "teacher_auth_view" not in st.session_state:
        st.session_state["teacher_auth_view"] = "login"

    # ── Styling & Header ──
    st.markdown(
        """
        <style>
            .screen-header-icon-teacher {
                background: linear-gradient(135deg, rgba(108, 92, 231, 0.2), rgba(168, 85, 247, 0.2));
                border: 1px solid rgba(108, 92, 231, 0.2);
            }
        </style>
        
        <div class="screen-header">
            <div class="screen-header-icon screen-header-icon-teacher">🎓</div>
            <div class="screen-header-text">
                <h2>Teacher Portal</h2>
                <p>Authentication Required</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.session_state["teacher_auth_view"] == "dashboard":
        _, dash_center, _ = st.columns([0.2, 3, 0.2])
        
        with dash_center:
            teacher_name = st.session_state.get("logged_in_teacher_name", "Teacher")
            
            # Show a toast pop-up on successful login
            if st.session_state.get("show_login_toast", False):
                st.toast(f"Welcome, {teacher_name}! 👋", icon="✅")
                st.session_state["show_login_toast"] = False
                
            st.markdown(
                f"""
                <div style="text-align: center; margin-bottom: -1.5rem; margin-top: -1rem;">
                    <h3 style='color: #ffffff; font-weight: 700; margin-bottom: 0.2rem;'>Teacher Dashboard</h3>
                    <p style='color: #a855f7; font-size: 1rem; font-weight: 500;'>Welcome back, {teacher_name}!</p>
                </div>
                """, 
                unsafe_allow_html=True
            )
            
            # Initialize dashboard view state
            if "teacher_dashboard_view" not in st.session_state:
                st.session_state["teacher_dashboard_view"] = None
                
            # Dashboard feature selection styles
            st.markdown(
                """
                <style>
                /* Style for the feature buttons */
                div[data-testid="column"] .stButton > button {
                    border-radius: 12px !important;
                    height: 55px !important;
                    font-size: 0.95rem !important;
                    font-weight: 600 !important;
                    border: 1px solid rgba(168, 85, 247, 0.2) !important;
                    background: rgba(45, 52, 54, 0.3) !important;
                    color: rgba(255, 255, 255, 0.8) !important;
                    transition: all 0.3s ease !important;
                }
                div[data-testid="column"] .stButton > button:hover {
                    background: rgba(168, 85, 247, 0.15) !important;
                    color: #ffffff !important;
                    border-color: rgba(168, 85, 247, 0.6) !important;
                    transform: translateY(-2px);
                }
                
                /* The card container that opens */
                .dashboard-card {
                    background: rgba(255, 255, 255, 0.02);
                    border: 1px solid rgba(168, 85, 247, 0.3);
                    border-radius: 16px;
                    padding: 2rem;
                    margin-top: 1rem;
                    margin-bottom: 2rem;
                    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
                    animation: fadeIn 0.4s ease-out forwards;
                }
                
                @keyframes fadeIn {
                    from { opacity: 0; transform: translateY(10px); }
                    to { opacity: 1; transform: translateY(0); }
                }
                
                .card-header {
                    font-size: 1.3rem;
                    color: #ffffff;
                    font-weight: 600;
                    margin-bottom: 0.5rem;
                    display: flex;
                    align-items: center;
                    gap: 10px;
                }
                
                .card-subtitle {
                    color: rgba(255, 255, 255, 0.5);
                    font-size: 0.9rem;
                    margin-bottom: 1.5rem;
                }
                </style>
                """,
                unsafe_allow_html=True
            )
            
            # The 3 feature buttons
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("📸 Take Attendance", width="stretch"):
                    st.session_state["teacher_dashboard_view"] = "take_attendance"
                    st.rerun()
            with col2:
                if st.button("📚 Manage Subject", width="stretch"):
                    st.session_state["teacher_dashboard_view"] = "manage_subject"
                    st.rerun()
            with col3:
                if st.button("📊 Attendance Record", width="stretch"):
                    st.session_state["teacher_dashboard_view"] = "attendance_record"
                    st.rerun()
                    
            view = st.session_state["teacher_dashboard_view"]
            
            # Render the selected card
            if view:
                teacher_id = st.session_state.get("logged_in_teacher_id")
                st.markdown('<div class="dashboard-card">', unsafe_allow_html=True)
                
                if view == "take_attendance":
                    st.markdown('<div class="card-header">📸 Take Attendance</div>', unsafe_allow_html=True)
                    render_take_attendance(teacher_id)
                    
                elif view == "manage_subject":
                    st.markdown('<div class="card-header">📚 Manage Subject</div>', unsafe_allow_html=True)
                    render_manage_subject(teacher_id)
                    
                elif view == "attendance_record":
                    st.markdown('<div class="card-header">📊 Attendance Record</div>', unsafe_allow_html=True)
                    render_attendance_record(teacher_id)
                    
                st.markdown('</div>', unsafe_allow_html=True)
            else:
                # If no view is selected yet, show a nice prompt
                st.markdown(
                    """
                    <div style="text-align: center; padding: 3rem 1rem; color: rgba(255,255,255,0.4); border: 1px dashed rgba(255,255,255,0.1); border-radius: 12px; margin-top: 1rem;">
                        <span style="font-size: 2rem;">👆</span><br>
                        Select a feature above to get started
                    </div>
                    """, 
                    unsafe_allow_html=True
                )
            
            # Logout button at the very bottom
            st.markdown("<hr style='border-color: rgba(255,255,255,0.05); margin: 2rem 0 1.5rem 0;'>", unsafe_allow_html=True)
            _, logout_col, _ = st.columns([1, 1, 1])
            with logout_col:
                if st.button("Logout", width="stretch"):
                    st.session_state["teacher_auth_view"] = "login"
                    st.session_state["teacher_dashboard_view"] = None
                    st.rerun()

    else:
        _, center_col, _ = st.columns([1, 1.5, 1])

        with center_col:
            # ---- LOGIN VIEW ----
            if st.session_state["teacher_auth_view"] == "login":
                st.markdown("<h3 style='text-align: center; color: #fff; margin-bottom: 1.5rem;'>Login to Account</h3>", unsafe_allow_html=True)
                
                default_user = st.session_state.get("prefill_username", "")
                default_pass = st.session_state.get("prefill_password", "")
                
                with st.form("login_form", clear_on_submit=False):
                    username = st.text_input("Username", value=default_user, placeholder="Enter username", key="login_username")
                    password = st.text_input("Password", type="password", value=default_pass, placeholder="Enter password", key="login_pass")
                    
                    st.markdown("<br>", unsafe_allow_html=True)
                    
                    submitted = st.form_submit_button("Login", width="stretch", type="primary")
                    
                    if submitted:
                        if username and password:
                            res = login_teacher(username, password)
                            if res["success"]:
                                st.session_state["logged_in_teacher_name"] = res["data"].get("name", username)
                                st.session_state["logged_in_teacher_id"] = res["data"].get("teacher_id")
                                st.session_state["teacher_auth_view"] = "dashboard"
                                st.session_state["show_login_toast"] = True
                                st.rerun()
                            else:
                                st.error(res["error"])
                        else:
                            st.warning("Please fill in both fields.")
                
                st.markdown('<div class="auth-divider">OR</div>', unsafe_allow_html=True)
                
                if st.button("Create a New Account", width="stretch"):
                    st.session_state["teacher_auth_view"] = "register"
                    st.rerun()

            # ---- REGISTER VIEW ----
            elif st.session_state["teacher_auth_view"] == "register":
                st.markdown("<h3 style='text-align: center; color: #fff; margin-bottom: 1.5rem;'>Create Account</h3>", unsafe_allow_html=True)

                with st.form("register_form", clear_on_submit=False):
                    name = st.text_input("Full Name", placeholder="e.g. John Doe", key="reg_name")
                    username = st.text_input("Username", placeholder="Choose a username", key="reg_username")
                    password = st.text_input("Password", type="password", placeholder="Create a password", key="reg_pass")
                    confirm_password = st.text_input("Confirm Password", type="password", placeholder="Repeat your password", key="reg_confirm")
                    
                    st.markdown("<br>", unsafe_allow_html=True)
                    
                    submitted = st.form_submit_button("Register", width="stretch", type="primary")
                    
                    if submitted:
                        if name and username and password and confirm_password:
                            if password == confirm_password:
                                res = register_teacher(username, password, name=name)
                                if res["success"]:
                                    st.success("Registration successful! Switching to login...")
                                    st.session_state["prefill_username"] = username
                                    st.session_state["prefill_password"] = password
                                    st.session_state["teacher_auth_view"] = "login"
                                    st.rerun()
                                else:
                                    st.error("Username already exists. Please try a different one.")
                            else:
                                st.error("Passwords do not match!")
                        else:
                            st.warning("Please fill in all fields.")
                
                st.markdown('<div class="auth-divider">OR</div>', unsafe_allow_html=True)
                
                if st.button("Back to Login", width="stretch"):
                    st.session_state["teacher_auth_view"] = "login"
                    st.rerun()

    # JS snippet to enable 'Enter' to focus the next input field
    import streamlit.components.v1 as components
    components.html(
        """
        <script>
            const parentDoc = window.parent.document;
            function attachListeners() {
                const inputs = Array.from(parentDoc.querySelectorAll('input[type="text"], input[type="password"]'));
                inputs.forEach((input, index) => {
                    if (input.dataset.hasEnterListener === "true") return;
                    input.addEventListener('keydown', function(event) {
                        if (event.key === 'Enter') {
                            event.preventDefault();
                            if (index < inputs.length - 1) {
                                inputs[index + 1].focus();
                            } else {
                                const btn = parentDoc.querySelector('button[kind="primaryFormSubmit"]') || parentDoc.querySelector('button[kind="primary"]');
                                if (btn) btn.click();
                            }
                        }
                    });
                    input.dataset.hasEnterListener = "true";
                });
            }
            // Run multiple times to catch elements after Streamlit renders
            attachListeners();
            setTimeout(attachListeners, 100);
            setTimeout(attachListeners, 500);
        </script>
        """,
        height=0,
        width=0
    )
