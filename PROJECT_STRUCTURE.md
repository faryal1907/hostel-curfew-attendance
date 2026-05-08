# 📂 Project Organization & System Flow

This document provides a comprehensive overview of the file structure and the logical flow of the **Hostel Curfew Attendance System**.

---

## 1. Directory Structure & File Purpose

### 📂 `backend/`
The core logic of the application, built with **FastAPI** and **SQLAlchemy**.

*   **📂 `app/`**
    *   `main.py`: The application entry point. It initializes the FastAPI app, sets up CORS (Cross-Origin Resource Sharing), seeds the default admin account, and mounts the API routes.
    *   `routes.py`: Contains all API endpoints. This is the "brain" that handles HTTP requests for login, registration, attendance processing, and dashboard statistics.
*   **📂 `models/`**
    *   `database.py`: Defines the SQLite database schema using SQLAlchemy ORM. It includes models for `User` (Students), `Admin`, and `AttendanceLog`.
    *   `face_model.py`: Wraps the `face_recognition` library. It handles face detection,Affined Alignment, and 128-D vector encoding.
    *   `curfew.py`: Logic for checking if the current time falls within the allowed attendance window.
*   **📂 `utils/`**
    *   Contains helper functions for general tasks (e.g., coordinate calculations).

### 📂 `frontend/`
A lightweight, modern UI built with **HTML5, Vanilla CSS, and JavaScript**.

*   `index.css`: The global design system (Glassmorphism, dark mode, responsive media queries).
*   `admin_login.html`: Secure gateway for hostel managers.
*   `register.html`: Interface for enrolling new students into the system.
*   `attendance.html`: The **Kiosk Mode** interface for floor-level attendance using a laptop/tablet camera.
*   `mobile.html`: The **Remote Check-in** interface for students, utilizing GPS and selfie verification.
*   `dashboard.html`: Real-time monitoring panel showing attendance stats, activity logs, and security alerts.

---

## 2. Overall System Flow

When a user interacts with the project, the following lifecycle occurs:

### Phase 1: Enrollment (Admin)
1.  **Action**: The Admin logs in and opens `register.html`.
2.  **Process**: They input student details and take a high-quality registration photo.
3.  **Backend**: The image is sent to `/register`. The `face_model.py` generates a 128-D embedding.
4.  **Storage**: The student’s info and the mathematical embedding (JSON) are saved into `database.db`.

### Phase 2: Attendance Verification (Student)
There are two ways to mark attendance:

#### **A. The Kiosk Flow (1:N Match)**
1.  **Action**: Student stands in front of the camera on `attendance.html`.
2.  **Process**: The system captures a live frame and sends it to `/attendance`.
3.  **Search**: The backend performs a "Linear Scan," comparing the live face against *all* registered students in the database.
4.  **Result**: If a match is found (Distance < 0.6) and the curfew is active, the student is marked "Present."

#### **B. The Mobile Flow (1:1 Verification)**
1.  **Action**: Student opens `mobile.html` on their phone and enters their CMS ID.
2.  **Process**: The system captures a selfie and the phone’s GPS coordinates.
3.  **Verification**: The backend fetches *only* the embedding for that specific CMS ID. It then checks:
    - **Identity**: Does the selfie match the registered student?
    - **Location**: Is the student within 100m of their hostel?
    - **Time**: Is the curfew currently active?
4.  **Result**: Attendance is logged only if all three conditions are met.

### Phase 3: Monitoring & Alerts (Management)
1.  **Polling**: The `dashboard.html` polls the `/dashboard-stats` endpoint every 5 seconds.
2.  **Logic**: The backend calculates totals for "Present" and "Absent" students.
3.  **Security Alerts**: 
    - If a face is unrecognized, it generates an "Unknown Person" alert.
    - If the curfew ends, the system automatically identifies students who haven't checked in and flags them as "Absentees."

---

## 3. Data Flow Diagram (Conceptual)
`User Input` ➔ `FastAPI Route` ➔ `Deep Learning Model (Embeddings)` ➔ `SQLite Query/Update` ➔ `Real-time Dashboard Feedback`
