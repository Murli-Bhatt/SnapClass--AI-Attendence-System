import streamlit as st


def render_home_screen():
    """Renders the home screen with Teacher & Student portal buttons."""

    # ── Custom CSS for Home Screen ──
    st.markdown(
        """
        <style>
            /* ── Hero Section ── */
            .hero-section {
                text-align: center;
                padding: 3rem 1rem 1.5rem 1rem;
            }

            .hero-badge {
                display: inline-block;
                padding: 5px 14px;
                background: rgba(108, 92, 231, 0.15);
                border: 1px solid rgba(108, 92, 231, 0.3);
                border-radius: 50px;
                color: #a78bfa;
                font-size: 0.7rem;
                font-weight: 600;
                letter-spacing: 1.5px;
                text-transform: uppercase;
                margin-bottom: 1.2rem;
            }

            .hero-title {
                font-size: 2.8rem;
                font-weight: 900;
                color: #ffffff;
                line-height: 1.1;
                margin-bottom: 0.8rem;
                letter-spacing: -1.5px;
            }

            .hero-title span {
                background: linear-gradient(135deg, #6C5CE7, #a855f7, #c084fc);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
            }

            .hero-description {
                font-size: 0.95rem;
                color: rgba(255, 255, 255, 0.45);
                max-width: 460px;
                margin: 0 auto 2rem auto;
                line-height: 1.7;
                font-weight: 400;
            }

            /* ── Portal Cards Grid ── */
            .portal-grid {
                display: flex;
                justify-content: center;
                gap: 1.5rem;
                padding: 0 1rem;
                max-width: 740px;
                margin: 0 auto;
            }

            .portal-card {
                flex: 1;
                background: rgba(255, 255, 255, 0.03);
                border: 1px solid rgba(255, 255, 255, 0.06);
                border-radius: 18px;
                padding: 2rem 1.5rem;
                text-align: center;
                cursor: pointer;
                transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
                position: relative;
                overflow: hidden;
            }

            .portal-card::before {
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                height: 3px;
                border-radius: 18px 18px 0 0;
                opacity: 0;
                transition: opacity 0.4s ease;
            }

            .portal-card-teacher::before {
                background: linear-gradient(90deg, #6C5CE7, #a855f7);
            }

            .portal-card-student::before {
                background: linear-gradient(90deg, #00b894, #55efc4);
            }

            .portal-card:hover {
                transform: translateY(-6px);
                border-color: rgba(255, 255, 255, 0.12);
                box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
            }

            .portal-card:hover::before {
                opacity: 1;
            }

            .portal-icon {
                width: 60px;
                height: 60px;
                border-radius: 16px;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 28px;
                margin: 0 auto 1.2rem auto;
                transition: transform 0.3s ease;
            }

            .portal-card:hover .portal-icon {
                transform: scale(1.1);
            }

            .portal-icon-teacher {
                background: linear-gradient(135deg, rgba(108, 92, 231, 0.2), rgba(168, 85, 247, 0.2));
                border: 1px solid rgba(108, 92, 231, 0.2);
            }

            .portal-icon-student {
                background: linear-gradient(135deg, rgba(0, 184, 148, 0.2), rgba(85, 239, 196, 0.2));
                border: 1px solid rgba(0, 184, 148, 0.2);
            }

            .portal-title {
                font-size: 1.15rem;
                font-weight: 700;
                color: #ffffff;
                margin-bottom: 0.4rem;
                letter-spacing: -0.3px;
            }

            .portal-desc {
                font-size: 0.8rem;
                color: rgba(255, 255, 255, 0.35);
                line-height: 1.6;
                margin-bottom: 1.2rem;
            }

            .portal-arrow {
                font-size: 0.75rem;
                font-weight: 600;
                letter-spacing: 1px;
                text-transform: uppercase;
                transition: all 0.3s ease;
            }

            .portal-arrow-teacher {
                color: #a78bfa;
            }

            .portal-arrow-student {
                color: #55efc4;
            }

            .portal-card:hover .portal-arrow {
                letter-spacing: 3px;
            }

            /* ── Background Glow Effects ── */
            .glow-purple {
                position: fixed;
                bottom: -100px;
                left: -100px;
                width: 350px;
                height: 350px;
                background: radial-gradient(circle, rgba(108, 92, 231, 0.08) 0%, transparent 70%);
                pointer-events: none;
                z-index: 0;
            }

            .glow-green {
                position: fixed;
                bottom: -100px;
                right: -100px;
                width: 350px;
                height: 350px;
                background: radial-gradient(circle, rgba(0, 184, 148, 0.06) 0%, transparent 70%);
                pointer-events: none;
                z-index: 0;
            }

            /* ── Feature Pills ── */
            .features-row {
                display: flex;
                justify-content: center;
                gap: 0.7rem;
                margin-top: 2.5rem;
                flex-wrap: wrap;
                padding: 0 1rem;
            }

            .feature-pill {
                display: flex;
                align-items: center;
                gap: 6px;
                padding: 8px 14px;
                background: rgba(255, 255, 255, 0.03);
                border: 1px solid rgba(255, 255, 255, 0.06);
                border-radius: 50px;
                color: rgba(255, 255, 255, 0.4);
                font-size: 0.72rem;
                font-weight: 500;
            }

            .feature-pill-icon {
                font-size: 0.85rem;
            }

            /* ── Override Streamlit Button Styling ── */
            div[data-testid="stHorizontalBlock"] .stButton > button {
                background: transparent !important;
                border: none !important;
                padding: 0 !important;
                color: transparent !important;
                height: 2px !important;
                min-height: 2px !important;
                margin: -1rem 0 0 0 !important;
                line-height: 0 !important;
                font-size: 0 !important;
                box-shadow: none !important;
                overflow: hidden !important;
            }

            div[data-testid="stHorizontalBlock"] .stButton > button:hover {
                background: transparent !important;
                border: none !important;
            }

            div[data-testid="stHorizontalBlock"] .stButton > button:focus {
                box-shadow: none !important;
            }
        </style>

        <div class="glow-purple"></div>
        <div class="glow-green"></div>

        <div class="hero-section">
            <div class="hero-badge">✨ Powered by AI</div>
            <div class="hero-title">
                Attendance,<br><span>Reimagined.</span>
            </div>
            <div class="hero-description">
                Smart face recognition attendance system that makes
                tracking effortless for teachers and students.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── Portal Cards using HTML + hidden Streamlit buttons for click handling ──
    col_spacer_l, col_teacher, col_student, col_spacer_r = st.columns(
        [0.5, 2, 2, 0.5], gap="small"
    )

    with col_teacher:
        st.markdown(
            """
            <div class="portal-card portal-card-teacher">
                <div class="portal-icon portal-icon-teacher">🎓</div>
                <div class="portal-title">Teacher Portal</div>
                <div class="portal-desc">
                    Manage classes, take attendance<br>with face recognition, and view reports.
                </div>
                <div class="portal-arrow portal-arrow-teacher">Enter →</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        teacher_clicked = st.button("t", key="btn_teacher", use_container_width=True)

    with col_student:
        st.markdown(
            """
            <div class="portal-card portal-card-student">
                <div class="portal-icon portal-icon-student">👨‍🎓</div>
                <div class="portal-title">Student Portal</div>
                <div class="portal-desc">
                    Register your face, view attendance<br>history, and download reports.
                </div>
                <div class="portal-arrow portal-arrow-student">Enter →</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        student_clicked = st.button("s", key="btn_student", use_container_width=True)

    # ── Feature Pills ──
    st.markdown(
        """
        <div class="features-row">
            <div class="feature-pill">
                <span class="feature-pill-icon">📸</span> Face Recognition
            </div>
            <div class="feature-pill">
                <span class="feature-pill-icon">📊</span> Real-time Reports
            </div>
            <div class="feature-pill">
                <span class="feature-pill-icon">🔒</span> Secure & Private
            </div>
            <div class="feature-pill">
                <span class="feature-pill-icon">⚡</span> Instant Matching
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── Handle Navigation ──
    if teacher_clicked:
        st.session_state["current_screen"] = "teacher"
        st.rerun()

    if student_clicked:
        st.session_state["current_screen"] = "student"
        st.rerun()
