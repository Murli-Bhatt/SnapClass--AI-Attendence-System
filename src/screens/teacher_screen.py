import streamlit as st


def render_teacher_screen():
    # ── Initialize State ──
    if "teacher_auth_view" not in st.session_state:
        st.session_state["teacher_auth_view"] = "login"

    # ── Styling & Header ──
    st.markdown(
        """
        <style>
            .screen-header {
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 1rem;
                margin-top: 1rem;
                margin-bottom: 2rem;
            }
            .screen-header-icon {
                width: 50px;
                height: 50px;
                background: linear-gradient(135deg, rgba(108, 92, 231, 0.2), rgba(168, 85, 247, 0.2));
                border: 1px solid rgba(108, 92, 231, 0.2);
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
            
            /* Professional inputs styling for deep dark mode */
            div[data-testid="stTextInput"] label p {
                color: rgba(255, 255, 255, 0.8) !important;
                font-weight: 600 !important;
                font-size: 0.95rem !important;
            }
            /* Hide 'Press Enter to apply' text */
            div[data-testid="InputInstructions"] {
                display: none !important;
            }
            /* Hide default browser password reveal eye icons that conflict with Streamlit's */
            input[type="password"]::-ms-reveal,
            input[type="password"]::-ms-clear {
                display: none !important;
            }
            div[data-testid="stTextInput"] input {
                background: rgba(255, 255, 255, 0.04) !important;
                border: 1px solid rgba(255, 255, 255, 0.1) !important;
                color: #fff !important;
                border-radius: 8px !important;
                padding: 12px 14px !important;
            }
            div[data-testid="stTextInput"] input:focus {
                border-color: #a855f7 !important;
                box-shadow: 0 0 0 1px #a855f7 !important;
                background: rgba(255, 255, 255, 0.08) !important;
            }
            
            /* Centered Divider */
            .auth-divider {
                text-align: center;
                margin: 1.5rem 0;
                color: rgba(255, 255, 255, 0.3);
                font-size: 0.85rem;
                position: relative;
            }
            .auth-divider::before, .auth-divider::after {
                content: '';
                position: absolute;
                top: 50%;
                width: 35%;
                height: 1px;
                background: rgba(255, 255, 255, 0.1);
            }
            .auth-divider::before { left: 0; }
            .auth-divider::after { right: 0; }
        </style>
        
        <div class="screen-header">
            <div class="screen-header-icon">🎓</div>
            <div class="screen-header-text">
                <h2>Teacher Portal</h2>
                <p>Authentication Required</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── Centered Form Container ──
    _, center_col, _ = st.columns([1, 1.5, 1])

    with center_col:
        # ---- LOGIN VIEW ----
        if st.session_state["teacher_auth_view"] == "login":
            st.markdown("<h3 style='text-align: center; color: #fff; margin-bottom: 1.5rem;'>Login to Account</h3>", unsafe_allow_html=True)
            
            username = st.text_input("Username", placeholder="Enter username", key="login_username")
            password = st.text_input("Password", type="password", placeholder="Enter password", key="login_pass")
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            if st.button("Login", use_container_width=True, type="primary"):
                if username and password:
                    st.success("Login attempted. (Logic to be implemented)")
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
                        st.success("Registration attempted. (Logic to be implemented)")
                    else:
                        st.error("Passwords do not match!")
                else:
                    st.warning("Please fill in all fields.")
            
            st.markdown('<div class="auth-divider">OR</div>', unsafe_allow_html=True)
            
            if st.button("Back to Login", use_container_width=True):
                st.session_state["teacher_auth_view"] = "login"
                st.rerun()
