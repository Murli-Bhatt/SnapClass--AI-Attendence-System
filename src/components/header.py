import streamlit as st

def render_header():
    """Renders the main header/navbar for Snap Class."""
    
    is_home = st.session_state.get("current_screen", "home") == "home"

    st.markdown(
        f"""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');

            /* ── Global Reset ── */
            .stApp {{
                background: linear-gradient(145deg, #0a0a0f 0%, #0d1117 40%, #0f0a1a 100%);
                font-family: 'Inter', sans-serif;
            }}

            /* ── Header Container ── */
            .snap-header {{
                display: flex;
                align-items: center;
                justify-content: space-between;
                padding: 0.9rem 1.5rem;
                background: rgba(255, 255, 255, 0.03);
                border-bottom: 1px solid rgba(255, 255, 255, 0.06);
                backdrop-filter: blur(20px);
                -webkit-backdrop-filter: blur(20px);
                margin-bottom: {'-3.3rem' if not is_home else '2rem'}; /* Pull inner button up visually */
                min-height: 4.8rem;
            }}

            .snap-header-brand {{
                display: flex;
                align-items: center;
                gap: 10px;
            }}

            .snap-header-logo {{
                width: 38px;
                height: 38px;
                background: linear-gradient(135deg, #6C5CE7, #a855f7);
                border-radius: 10px;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 18px;
                box-shadow: 0 4px 15px rgba(108, 92, 231, 0.3);
            }}

            .snap-header-title {{
                font-size: 1.35rem;
                font-weight: 800;
                background: linear-gradient(135deg, #ffffff 0%, #a78bfa 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
                letter-spacing: -0.5px;
                line-height: 1.2;
            }}

            .snap-header-sub {{
                font-size: 0.6rem;
                color: rgba(167, 139, 250, 0.6);
                font-weight: 500;
                letter-spacing: 2px;
                text-transform: uppercase;
                line-height: 1;
                margin-top: 2px;
            }}
        </style>

        <div class="snap-header">
            <div class="snap-header-brand">
                <div class="snap-header-logo">📸</div>
                <div>
                    <div class="snap-header-title">Snap Class</div>
                    <div class="snap-header-sub">AI Attendance System</div>
                </div>
            </div>
            <!-- The right side is gracefully filled by the overlaying Streamlit button when required -->
        </div>
        """,
        unsafe_allow_html=True,
    )

    if not is_home:
        # Create columns to safely overlay a native Streamlit button onto the right side of the navbar
        col1, col2 = st.columns([7.5, 1])
        with col2:
            if st.button("Home ↲", key="header_home_btn", use_container_width=True, type="tertiary"):
                st.session_state["current_screen"] = "home"
                st.rerun()

        st.markdown(
            """
            <style>
            /* Make this specific button look like a compact navbar text link */
            div[data-testid="column"]:nth-of-type(2) .stButton > button,
            div[data-testid="column"]:nth-of-type(2) .stButton > button * {
                background: transparent !important;
                background-color: transparent !important;
                border: 0px solid transparent !important;
                outline: none !important;
                box-shadow: none !important;
                text-decoration: none !important;
            }
            div[data-testid="column"]:nth-of-type(2) .stButton > button {
                color: rgba(255, 255, 255, 0.6) !important;
                padding: 0 !important;
                font-weight: 500 !important;
                font-size: 0.85rem !important;
                min-height: 0 !important;
                height: 2.1rem !important;
                margin-top: 0.4rem !important;
                justify-content: flex-end !important; /* Align text to the right natively */
                transition: all 0.3s ease !important;
            }
            div[data-testid="column"]:nth-of-type(2) .stButton > button:hover {
                color: #ffffff !important;
                transform: translateX(-3px); /* subtle interaction */
            }
            </style>
            <br>
            """,
            unsafe_allow_html=True
        )
