import streamlit as st


def render_header():
    """Renders the main header/navbar for Snap Class."""
    st.markdown(
        """
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');

            /* ── Global Reset ── */
            .stApp {
                background: linear-gradient(145deg, #0a0a0f 0%, #0d1117 40%, #0f0a1a 100%);
                font-family: 'Inter', sans-serif;
            }

            /* ── Header Container ── */
            .snap-header {
                display: flex;
                align-items: center;
                justify-content: space-between;
                padding: 0.9rem 1.5rem;
                background: rgba(255, 255, 255, 0.03);
                border-bottom: 1px solid rgba(255, 255, 255, 0.06);
                backdrop-filter: blur(20px);
                -webkit-backdrop-filter: blur(20px);
                margin-bottom: 0;
            }

            .snap-header-brand {
                display: flex;
                align-items: center;
                gap: 10px;
            }

            .snap-header-logo {
                width: 38px;
                height: 38px;
                background: linear-gradient(135deg, #6C5CE7, #a855f7);
                border-radius: 10px;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 18px;
                box-shadow: 0 4px 15px rgba(108, 92, 231, 0.3);
            }

            .snap-header-title {
                font-size: 1.35rem;
                font-weight: 800;
                background: linear-gradient(135deg, #ffffff 0%, #a78bfa 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
                letter-spacing: -0.5px;
                line-height: 1.2;
            }

            .snap-header-sub {
                font-size: 0.6rem;
                color: rgba(167, 139, 250, 0.6);
                font-weight: 500;
                letter-spacing: 2px;
                text-transform: uppercase;
                line-height: 1;
                margin-top: 2px;
            }
        </style>

        <div class="snap-header">
            <div class="snap-header-brand">
                <div class="snap-header-logo">📸</div>
                <div>
                    <div class="snap-header-title">Snap Class</div>
                    <div class="snap-header-sub">AI Attendance System</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
