Here is your project documentation formatted in clean, organized Markdown.

# 📌 Hostel Curfew Attendance and Alert System (Prototype)

## 🧠 Overview
This project is a web-based prototype of a **Deep Learning-powered** Hostel Curfew Attendance and Alert System. It utilizes facial recognition to simulate attendance marking, detect unknown users, and prepare for curfew-based enforcement logic. 

The system is built using a lightweight and fast stack optimized for rapid prototyping and semester-level demonstrations.

## ⚙️ Tech Stack
* **Backend:** FastAPI
* **Database:** SQLite (via SQLAlchemy)
* **Face Recognition:** `face-recognition` (dlib-based embeddings)
* **Image Processing:** OpenCV
* **Server:** Uvicorn
* **Language:** Python

---

## 🏗️ Project Structure (Current Stage)
```text
hostel-curfew-attendance/
│
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── routes.py
│   │
│   ├── models/
│   │   ├── database.py
│   │   ├── face_model.py
│   │
│   └── database.db
│
├── frontend/ (not implemented yet)
├── venv/
├── requirements.txt
└── README.md
```

---

## 🚀 Current Features Implemented

### ✅ 1. FastAPI Backend Setup
* Initialized FastAPI application.
* Configured routing system.
* Running local development server using Uvicorn.

### ✅ 2. Database Setup (SQLite)
* Created SQLite database using **SQLAlchemy**.
* **Defined Core Models:**
    * `User`: Student information + face embedding.
    * `AttendanceLog`: Timestamped attendance records.

### ✅ 3. Face Recognition Module
Implemented face detection and encoding using the `face-recognition` library.
* **Features:**
    * Converts images to 128-d embeddings.
    * Compares face embeddings using distance metrics.
    * Detects unknown faces.

### ✅ 4. API Endpoints
| Endpoint | Functionality |
| :--- | :--- |
| `POST /register` | Registers student with Name, Roll No, Room No, and Face Image. Stores embeddings in SQLite. |
| `POST /attendance` | Accepts webcam image, extracts embedding, and compares with database. |

---

## 🧪 Current System Behavior
* Students can be registered via API.
* Attendance can be marked using webcam images.
* System identifies **Known** vs **Unknown** individuals.
* All records are persisted in the SQLite database.

> [!CAUTION]
> **Known Notes / Warnings:**
> * The first run automatically downloads face recognition models.
> * Internet is required only once for model initialization.
> * `pkg_resources` warnings are dependency-related and not critical to system function.

---

## 📍 Next Planned Features
1.  **⏱ Curfew Logic:** Implementation of a strict 30-minute reporting window.
2.  **🚨 Auto-Detection:** Automatic identification of non-reporting students.
3.  **📊 Manager Dashboard:** React-based frontend for monitoring.
4.  **🔔 Alert System:** Automated notifications for absent students.
5.  **🎨 UI/UX:** Implementation of a "Dark Premium" dashboard theme.

---

## 🎯 Project Status
* **Phase 1: Backend Core System** → `COMPLETED ✔️`
* **Phase 2: Logic + Curfew System** → `IN PROGRESS`

## 👥 Team Scope
This is a **2-member semester project** focusing on:
* Applied deep learning (face embeddings).
* Real-world system design.
* Attendance automation logic.
* Alert-based monitoring systems.