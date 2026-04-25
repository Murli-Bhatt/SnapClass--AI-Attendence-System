import streamlit as st

# ── Page Configuration ──
st.set_page_config(
    page_title="Snap Class - AI Attendance System",
    page_icon="📸",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Imports ──
from src.components.header import render_header


# ── Hide Streamlit Default Elements & Fix Spacing ──
st.markdown(
    """
    <style>
        /* Hide hamburger menu, footer, and default header */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header[data-testid="stHeader"] {visibility: hidden; height: 0;}

        /* Tighten main container padding */
        .block-container {
            padding-top: 0.5rem !important;
            padding-bottom: 1rem !important;
        }

        /* Scrollbar */
        ::-webkit-scrollbar {
            width: 5px;
        }
        ::-webkit-scrollbar-track {
            background: transparent;
        }
        ::-webkit-scrollbar-thumb {
            background: rgba(108, 92, 231, 0.3);
            border-radius: 3px;
        }
        ::-webkit-scrollbar-thumb:hover {
            background: rgba(108, 92, 231, 0.5);
        }

        /* Hide sidebar */
        [data-testid="stSidebar"] {
            display: none;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# ── Session State Init ──
if "current_screen" not in st.session_state:
    st.session_state["current_screen"] = "home"

# ── Render Header ──
render_header()

# ── Screen Router ──
screen = st.session_state["current_screen"]

if screen == "home":
    from src.screens.home_screen import render_home_screen
    render_home_screen()
elif screen == "teacher":
    from src.screens.teacher_screen import render_teacher_screen
    render_teacher_screen()
elif screen == "student":
    from src.screens.student_screen import render_student_screen
    render_student_screen()
elif screen == "student_dashboard":
    from src.screens.student_dashboard import render_student_dashboard
    render_student_dashboard()
else:
    st.session_state["current_screen"] = "home"
    st.rerun()
