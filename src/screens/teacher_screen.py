import streamlit as st


def render_teacher_screen():
    """Placeholder for the Teacher Portal screen."""
    st.markdown(
        """
        <style>
            .screen-header {
                display: flex;
                align-items: center;
                gap: 1rem;
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
        </style>
        <div class="screen-header">
            <div class="screen-header-icon">🎓</div>
            <div class="screen-header-text">
                <h2>Teacher Portal</h2>
                <p>Manage classes and attendance</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.info("🚧 Teacher Portal is under construction. Features coming soon!")

    if st.button("← Back to Home", key="teacher_back"):
        st.session_state["current_screen"] = "home"
        st.rerun()
