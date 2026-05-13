# 🎓 SnapClass: Next-Gen AI Biometric Attendance System

> A modern, AI-powered educational platform that replaces manual roll-calls with instant, multi-modal biometric authentication (Face & Voice).

![Python](https://img.shields.io/badge/Python-3.x-blue.svg?style=for-the-badge&logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-Framework-FF4B4B.svg?style=for-the-badge&logo=streamlit)
![Supabase](https://img.shields.io/badge/Supabase-Database-3ECF8E.svg?style=for-the-badge&logo=supabase)
![Machine Learning](https://img.shields.io/badge/AI-Biometrics-purple.svg?style=for-the-badge)

## 🌟 Overview

SnapClass is a state-of-the-art attendance management system built to streamline classroom operations and eliminate proxy attendance. By leveraging advanced deep learning models for both **Facial Recognition** and **Voice Verification**, it ensures highly secure and frictionless attendance logging. 

The entire application is wrapped in a premium, responsive "glassmorphism" UI built exclusively with Streamlit, providing an intuitive experience for both educators and students.

---

## ✨ Key Features

### 👨‍🏫 Teacher Dashboard
*   **📸 Group Photo Analysis:** Upload up to 5 photos of a classroom simultaneously. The AI detects all faces in the crowd, cross-references the 128D embeddings, and logs attendance instantly.
*   **📷 Live Camera Scanning:** Use a device webcam for real-time classroom scanning. Features a dynamic fallback pipeline to handle low resolution, extreme angles, and poor lighting.
*   **🎤 Voice Verification:** Biometrically verify a specific student using unique audio feature extraction.
*   **📚 Subject Management:** Create multiple subjects, monitor enrolled student counts, and track total classes held.
*   **📊 Analytics & Records:** Filterable, interactive grids displaying past attendance records with visual summaries.

### 👩‍🎓 Student Portal
*   **🔐 Biometric Enrollment:** A seamless onboarding flow where students register their unique facial map and voice print.
*   **📖 Easy Course Enrollment:** Join classes instantly using secure Subject Codes provided by the teacher.

---

## 🧠 Technical Architecture & AI Pipelines

### 1. Robust Face Recognition Pipeline (`src/pipelines/face_pipeline.py`)
Standard face detectors often fail on webcam feeds due to scaling issues or head tilts. This project utilizes a highly custom, multi-pass detection strategy using `dlib`:
1. **Zero-Upsample Scan:** Designed specifically to catch large, close-up faces (common in webcam usage) that exceed standard HOG sliding window sizes.
2. **Grayscale Enhancement:** Converts the image to grayscale and applies contrast adjustments to handle poor lighting.
3. **Dynamic Downsampling:** If a face is too large, the system shrinks the image, detects the face, and extrapolates the bounding box back to the original resolution.
4. **CNN Deep Learning Fallback:** If HOG detection completely fails due to an extreme head tilt, a Convolutional Neural Network (CNN) kicks in to locate the face.
5. **128D Encoding & Distance Matching:** The detected face is passed through a ResNet network to generate a 128-dimensional biometric vector. Recognition is achieved via Euclidean distance calculations against the Supabase dataset.

### 2. Voice Recognition Pipeline (`src/pipelines/voice_pipeline.py`)
*   Powered by `librosa` and `resemblyzer`.
*   Extracts highly unique audio features (Mel-frequency cepstral coefficients) from a short audio clip.
*   Converts the audio profile into a standardized array stored securely in the database for future voice-matching.

### 3. Cloud Database (`Supabase / PostgreSQL`)
*   **Real-time sync:** Instant updates across the Teacher and Student dashboards.
*   **Vector Storage:** Securely stores the 128D facial arrays and audio embeddings as JSON arrays for rapid querying.

---

## 📂 Folder Structure

```text
snapclass/
│
├── src/
│   ├── components/      # Reusable UI elements (Headers, Navbars)
│   ├── database/        # Supabase connection and CRUD operations
│   ├── pipelines/       # Core AI logic (face_pipeline.py, voice_pipeline.py)
│   ├── screens/         # Main views (Teacher, Student, Home)
│   └── utils/           # Custom CSS styling and helpers
│
├── app.py               # Main entry point for Streamlit
├── requirements.txt     # Python dependencies
└── .env                 # Environment variables (not tracked in git)
