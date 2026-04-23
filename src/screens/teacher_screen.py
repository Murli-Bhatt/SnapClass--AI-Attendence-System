import streamlit as st
from src.database.db import register_teacher, login_teacher
from src.utils.styles import apply_global_styles

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

    _, center_col, _ = st.columns([1, 1.5, 1])

    with center_col:
        # ---- DASHBOARD VIEW (Logged In) ----
        if st.session_state["teacher_auth_view"] == "dashboard":
            teacher_name = st.session_state.get("logged_in_teacher_name", "Teacher")
            
            # Show a toast pop-up on successful login
            if st.session_state.get("show_login_toast", False):
                st.toast(f"Welcome, {teacher_name}! 👋", icon="✅")
                st.session_state["show_login_toast"] = False
                
            st.markdown(f"<h3 style='text-align: center; color: #a855f7; margin-top: 2rem;'>Hello, {teacher_name}!</h3>", unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Logout", use_container_width=True):
                st.session_state["teacher_auth_view"] = "login"
                st.rerun()

        # ---- LOGIN VIEW ----
        elif st.session_state["teacher_auth_view"] == "login":
            st.markdown("<h3 style='text-align: center; color: #fff; margin-bottom: 1.5rem;'>Login to Account</h3>", unsafe_allow_html=True)
            
            default_user = st.session_state.get("prefill_username", "")
            default_pass = st.session_state.get("prefill_password", "")
            
            username = st.text_input("Username", value=default_user, placeholder="Enter username", key="login_username")
            password = st.text_input("Password", type="password", value=default_pass, placeholder="Enter password", key="login_pass")
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            if st.button("Login", use_container_width=True, type="primary"):
                if username and password:
                    res = login_teacher(username, password)
                    if res["success"]:
                        st.session_state["logged_in_teacher_name"] = res["data"].get("name", username)
                        st.session_state["teacher_auth_view"] = "dashboard"
                        st.session_state["show_login_toast"] = True
                        st.rerun()
                    else:
                        st.error(res["error"])
                else:
                    st.warning("Please fill in both fields.")
            
            st.markdown('<div class="auth-divider">OR</div>', unsafe_allow_html=True)
            
            if st.button("Create a New Account", use_container_width=True):
                st.session_state["teacher_auth_view"] = "register"
                st.rerun()

        # ---- REGISTER VIEW ----
        elif st.session_state["teacher_auth_view"] == "register":
            st.markdown("<h3 style='text-align: center; color: #fff; margin-bottom: 1.5rem;'>Create Account</h3>", unsafe_allow_html=True)

            name = st.text_input("Full Name", placeholder="e.g. John Doe", key="reg_name")
            username = st.text_input("Username", placeholder="Choose a username", key="reg_username")
            password = st.text_input("Password", type="password", placeholder="Create a password", key="reg_pass")
            confirm_password = st.text_input("Confirm Password", type="password", placeholder="Repeat your password", key="reg_confirm")
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            if st.button("Register", use_container_width=True, type="primary"):
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
            
            if st.button("Back to Login", use_container_width=True):
                st.session_state["teacher_auth_view"] = "login"
                st.rerun()
