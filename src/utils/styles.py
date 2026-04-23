import streamlit as st
import contextlib

def apply_global_styles():
    """Applies common CSS used across multiple screens."""
    st.markdown(
        """
        <style>
            /* ── Common Header/Input Styles ── */
            div[data-testid="stTextInput"] label p {
                color: rgba(255, 255, 255, 0.8) !important;
                font-weight: 600 !important;
                font-size: 0.95rem !important;
            }
            div[data-testid="InputInstructions"] {
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

            /* ── Screen Headers ── */
            .screen-header {
                display: flex;
                align-items: center;
                gap: 1rem;
                margin-bottom: 2rem;
            }
            .screen-header-icon {
                width: 50px;
                height: 50px;
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
            
            /* ── Auth Divider ── */
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
        """,
        unsafe_allow_html=True
    )

@contextlib.contextmanager
def full_screen_spinner(text, color="#55efc4"):
    """Reusable full-screen overlay with a spinner."""
    placeholder = st.empty()
    placeholder.markdown(
        f"""
        <style>
            .fullscreen-overlay {{
                position: fixed;
                top: 0;
                left: 0;
                width: 100vw;
                height: 100vh;
                background: rgba(15, 15, 15, 0.7);
                backdrop-filter: blur(8px);
                z-index: 999999;
                display: flex;
                flex-direction: column;
                justify-content: center;
                align-items: center;
                color: {color};
                font-family: sans-serif;
            }}
            .spinner-loader {{
                border: 6px solid rgba(255, 255, 255, 0.1);
                border-top: 6px solid {color};
                border-radius: 50%;
                width: 60px;
                height: 60px;
                animation: spin 1s linear infinite;
                margin-bottom: 20px;
                box-shadow: 0 0 20px {color}44;
            }}
            @keyframes spin {{
                0% {{ transform: rotate(0deg); }}
                100% {{ transform: rotate(360deg); }}
            }}
        </style>
        <div class="fullscreen-overlay">
            <div class="spinner-loader"></div>
            <h3>{text}</h3>
        </div>
        """,
        unsafe_allow_html=True
    )
    try:
        yield
    finally:
        placeholder.empty()
