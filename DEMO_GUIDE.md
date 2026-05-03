# 📽️ Live Demo Guide: Hostel Curfew System

Use this guide to perform a seamless demonstration anywhere at anytime. Each case highlights a specific technical feature of the project.

---

## 🛠️ Preparation
1.  **Backend**: `uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000`
2.  **Frontend**: `cd frontend` then `python -m http.server 3000`
3.  **Login**: Access `http://localhost:3000/dashboard.html` and log in as `admin` / `admin123`.

---

## 🎭 Scenario 1: The "Authorized Resident" (Kiosk)
**Goal**: Show successful Deep Learning face verification.
1.  **Navigate**: Open `Attendance Kiosk`.
2.  **Action**: Force an "AUTHORIZED" state in `backend/models/curfew.py`:
    ```python
    # In backend/models/curfew.py (Line 4)
    CURFEW_START = datetime.now().replace(second=0, microsecond=0)  
    ```
2.  **Action**: Stand in front of the camera and click **"Mark Attendance"**.
3.  **Result**: The system should recognize you, show **"PRESENT: [YOUR NAME]"**, and flash a green success overlay.

## 🎭 Scenario 2: The "Unrecognized Intruder" (Kiosk)
**Goal**: Show the CNN's ability to reject unknown people.
1.  **Action**: Have a classmate (not registered) or show a random face from your phone to the camera.
2.  **Result**: The system will display **"UNRECOGNIZED IDENTITY"** with a red warning overlay.
3.  **Dashboard**: Open the Dashboard; an alert for an "Unknown Person" will appear instantly.

## 🎭 Scenario 3: The "GPS Geofence" (Mobile)
**Goal**: Show the Haversine distance check in action.
1.  **Navigate**: Open `Mobile Check-in`.
2.  **Prerequisite**: Ensure your `HOSTEL_LOCATIONS` in `backend/app/routes.py` matches your current classroom coordinates:
    ```python
    # In backend/app/routes.py (Line 45)
    HOSTEL_LOCATIONS = {
        "amna": {"lat": YOUR_LAT, "lng": YOUR_LNG}, 
    }
    ```
3.  **Action**: Enter your CMS ID, take a selfie, and click **"Mark Location Attendance"**.
4.  **Success Result**: If you are within the range, it shows **"SUCCESS: Attendance marked"**.
5.  **Fail Result**: If you are too far (or spoofing), it shows **"DENIED: You are [X] meters away"**.

## 🎭 Scenario 4: The "Curfew Lock"
**Goal**: Show the automated security window.
1.  **Navigate**: Open `backend/models/curfew.py`.
2.  **Action**: Force a "Closed" state by setting the start time to the past in `backend/models/curfew.py`:
    ```python
    # In backend/models/curfew.py (Line 4)
    CURFEW_START = datetime.now() - timedelta(minutes=40) 
    ```
3.  **Attempt**: Try to mark attendance on either Kiosk or Mobile.
4.  **Result**: The system will display **"OUTSIDE CURFEW WINDOW"**.
5.  **Dashboard**: The Curfew status banner will turn yellow and say **"Status: Closed"**.
6.  **Toggle Back to Active**: To make the curfew active again, change line 4 in `curfew.py` to:
    ```python
    CURFEW_START = datetime.now().replace(second=0, microsecond=0)
    ```

## 🎭 Scenario 5: The "Command Center" (Admin)
**Goal**: Show real-time data synchronization.
1.  **Navigate**: Open the `Dashboard`.
2.  **Action**: Perform an "Unknown" attempt on another device.
3.  **Observation**: Watch the **"Unknown Attempts"** counter increase and a new alert appear in the **"System Alerts"** list without refreshing the page (if auto-refresh is on).

## 🎭 Scenario 6: Secure Registration
**Goal**: Show protected administrative actions.
1.  **Navigate**: Log out, then try to access `register.html` directly.
2.  **Result**: The system will kick you back to the **Admin Login** page (Auth Guard).
3.  **Action**: Log in, go to `Register`, and enroll a new student with a fresh face scan.

---

## 💡 Pro-Tips for the Demo:
*   **Lighting**: Ensure your face is well-lit for the CNN model to get a high-quality embedding.
*   **Coordinates**: Double-check your latitude/longitude in `routes.py` before the class starts!
*   **The "Magic" Refresh**: After changing code, the backend auto-reloads. Click **"Refresh"** on the Dashboard to see the new status.
*   **Distance**: If you want to demonstrate a "Failure" in GPS, simply change your hostel's lat/lng to a location in another city (e.g., Karachi or Lahore).
