from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Header, Depends
from sqlalchemy.orm import Session
import json
import datetime
import base64
import math
import hashlib
from backend.models.database import SessionLocal, User, AttendanceLog, Admin
from backend.models.face_model import base64_to_image, get_embedding, compare_faces
from backend.models.curfew import is_within_curfew, is_curfew_over, CURFEW_START

router = APIRouter()

def get_password_hash(password: str):
    return hashlib.sha256(password.encode()).hexdigest()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def verify_admin(x_admin_token: str = Header(None, alias="X-Admin-Token")):
    if not x_admin_token or not x_admin_token.startswith("session_"):
        print(f"Auth Failed: Header is {x_admin_token}") # Debug print
        raise HTTPException(status_code=401, detail="Admin access required")
    return x_admin_token


@router.post("/admin/login")
async def admin_login(username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    admin = db.query(Admin).filter(Admin.username == username).first()
    if not admin or admin.password_hash != get_password_hash(password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token = f"session_{admin.username}"
    return {"token": token, "username": admin.username}



# IMPORTANT: For your demo, change "ayesha" (or whichever you register as) to your EXACT classroom coordinates!
# You can get your classroom coordinates from Google Maps (right click on the map -> copy coordinates).
HOSTEL_LOCATIONS = {
    "amna": {"lat": 33.6255, "lng": 72.9516}, 
    "ayesha": {"lat": 33.64440, "lng": 72.99218}, # NLS coordinates
    "khadija": {"lat": 33.62, "lng": 72.96},
    "zainab": {"lat": 33.64557, "lng": 72.99406},
}

def haversine(lat1, lon1, lat2, lon2):
    """Calculate distance between two GPS points in meters"""
    R = 6371000 # Earth radius in meters
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = math.sin(delta_phi / 2.0) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    distance = R * c
    return distance


# REGISTER USER
@router.post("/register")
async def register(
    name: str = Form(...), 
    roll_no: str = Form(...), 
    hostel_name: str = Form(...),
    room_no: str = Form(...), 
    image: UploadFile = File(...),
    admin: str = Depends(verify_admin),
    db: Session = Depends(get_db)
):
    if not roll_no.isdigit() or len(roll_no) != 6:
        raise HTTPException(status_code=400, detail="CMS ID must be exactly a 6-digit number")
        
    valid_hostels = ["amna", "ayesha", "khadija", "zainab"]
    if hostel_name.lower() not in valid_hostels:
        raise HTTPException(status_code=400, detail="Invalid hostel name")

    img_bytes = await image.read()
    img_str = "data:image/jpeg;base64," + base64.b64encode(img_bytes).decode()

    image = base64_to_image(img_str)
    embedding = get_embedding(image)

    if embedding is None:
        raise HTTPException(status_code=400, detail="No face detected in the provided image")

    user = User(
        name=name,
        roll_no=roll_no,
        hostel_name=hostel_name,
        room_no=room_no,
        embedding=json.dumps(embedding.tolist())
    )

    db.add(user)
    db.commit()

    return {"message": "User registered"}


# ATTENDANCE
@router.post("/attendance")
async def mark_attendance(image: UploadFile = File(...), db: Session = Depends(get_db)):

    img_bytes = await image.read()
    img_str = "data:image/jpeg;base64," + base64.b64encode(img_bytes).decode()

    image = base64_to_image(img_str)
    new_embedding = get_embedding(image)

    if new_embedding is None:
        # Log failure to detect face
        log = AttendanceLog(user_id=None, status="Unknown")
        db.add(log)
        db.commit()
        return {"status": "No face detected"}

    # [SECURITY] CURFEW CHECK
    if not is_within_curfew():
        # Log unauthorized attempt outside curfew
        log = AttendanceLog(user_id=None, status="Unknown")
        db.add(log)
        db.commit()
        return {"status": "Outside curfew window"}

    users = db.query(User).all()

    if len(users) == 0:
        return {"status": "No users registered"}

    known_embeddings = [json.loads(u.embedding) for u in users]

    dist, idx = compare_faces(known_embeddings, new_embedding)

    THRESHOLD = 0.6

    if dist < THRESHOLD:
        user = users[idx]

        log = AttendanceLog(
            user_id=user.id,
            status="Present"
        )
        db.add(log)
        db.commit()

        return {"status": "Present", "name": user.name}

    else:
        log = AttendanceLog(
            user_id=None,
            status="Unknown"
        )
        db.add(log)
        db.commit()

        return {"status": "Unknown"}


@router.post("/mobile-attendance")
async def mobile_attendance(
    roll_no: str = Form(...), 
    lat: float = Form(...), 
    lng: float = Form(...),
    image: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    if not is_within_curfew():
        # Log unauthorized attempt outside curfew
        log = AttendanceLog(user_id=None, status="Unknown")
        db.add(log)
        db.commit()
        return {"status": "error", "message": "Outside curfew window"}

    # db = SessionLocal() already called at the top
    user = db.query(User).filter(User.roll_no == roll_no).first()

    if not user:
        # Log unknown CMS attempt
        log = AttendanceLog(user_id=None, status="Unknown")
        db.add(log)
        db.commit()
        return {"status": "error", "message": "Student not found"}

    # 1. Face Verification
    img_bytes = await image.read()
    img_str = "data:image/jpeg;base64," + base64.b64encode(img_bytes).decode()
    image_obj = base64_to_image(img_str)
    new_embedding = get_embedding(image_obj)

    if new_embedding is None:
        return {"status": "error", "message": "No face detected in selfie"}

    stored_embedding = json.loads(user.embedding)
    # Compare selfie with the specific user's stored face
    dist, _ = compare_faces([stored_embedding], new_embedding)
    
    THRESHOLD = 0.6
    if dist >= THRESHOLD:
        # Log face mismatch
        log = AttendanceLog(user_id=None, status="Unknown")
        db.add(log)
        db.commit()
        return {"status": "error", "message": "Face does not match registered student"}

    # 2. Location Verification
    hostel = user.hostel_name.lower() if user.hostel_name else ""
    if hostel not in HOSTEL_LOCATIONS:
        return {"status": "error", "message": f"Hostel '{hostel}' location not configured"}

    target_lat = HOSTEL_LOCATIONS[hostel]["lat"]
    target_lng = HOSTEL_LOCATIONS[hostel]["lng"]

    distance = haversine(lat, lng, target_lat, target_lng)

    if distance <= 100:
        log = AttendanceLog(
            user_id=user.id,
            status="Present"
        )
        db.add(log)
        db.commit()
        return {"status": "success", "message": f"Verified! Present at {hostel.capitalize()}", "distance_m": round(distance, 1)}
    else:
        # Log location mismatch as unknown/unauthorized attempt
        log = AttendanceLog(user_id=None, status="Unknown")
        db.add(log)
        db.commit()
        return {"status": "error", "message": f"Location mismatch: You are {round(distance, 1)}m away from {hostel.capitalize()} hostel. Must be within 1000m."}


@router.get("/users")
def get_users(admin: str = Depends(verify_admin), db: Session = Depends(get_db)):
    users = db.query(User).all()
    return [{"id": u.id, "name": u.name, "roll_no": u.roll_no, "room_no": u.room_no, "hostel": u.hostel_name} for u in users]


@router.delete("/users/{user_id}")
def delete_user(user_id: int, admin: str = Depends(verify_admin), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Also delete associated logs to maintain referential integrity if needed, 
    # though with user_id as nullable in logs, they will just become None-linked.
    db.delete(user)
    db.commit()
    return {"message": "User deleted successfully"}


@router.get("/generate_absentees")
def generate_absentees():
    db = SessionLocal()

    if not is_curfew_over():
        return {"message": "Curfew still active"}

    users = db.query(User).all()
    logs = db.query(AttendanceLog).all()

    present_ids = {log.user_id for log in logs if log.user_id is not None}

    absentees = [
        user.name for user in users if user.id not in present_ids
    ]

    return {
        "absentees": absentees,
        "count": len(absentees)
    }

@router.get("/dashboard-stats")
def get_dashboard_stats(admin: str = Depends(verify_admin), db: Session = Depends(get_db)):
    users = db.query(User).all()
    logs = db.query(AttendanceLog).order_by(AttendanceLog.timestamp.desc()).all()

    total_students = len(users)
    present_ids = {log.user_id for log in logs if log.user_id is not None and log.status == "Present"}
    present_count = len(present_ids)
    
    absent_count = total_students - present_count

    unknown_attempts = [log for log in logs if log.status == "Unknown"]
    unknown_count = len(unknown_attempts)

    recent_activity = []
    user_dict = {u.id: u.name for u in users}
    
    for log in logs[:10]:
        name = user_dict.get(log.user_id, "Unknown Person") if log.user_id else "Unknown Person"
        recent_activity.append({
            "name": name,
            "status": log.status,
            "time": log.timestamp.strftime("%I:%M %p")
        })

    alerts = []
    if is_curfew_over():
        absentees = [u.name for u in users if u.id not in present_ids]
        for a in absentees:
            alerts.append(f"Absentee detected: {a}")
            
    for log in unknown_attempts[:5]:
        alerts.append(f"Unknown person detected at {log.timestamp.strftime('%I:%M %p')}")

    return {
        "total_students": total_students,
        "present": present_count,
        "absent": absent_count,
        "unknown_attempts": unknown_count,
        "recent_activity": recent_activity,
        "alerts": alerts,
        "curfew_active": is_within_curfew()
    }