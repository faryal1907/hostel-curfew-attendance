from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from sqlalchemy.orm import Session
from backend.models.database import SessionLocal, User, AttendanceLog
from backend.models.face_model import base64_to_image, get_embedding, compare_faces
import json
import datetime
from backend.models.curfew import is_within_curfew, is_curfew_over, CURFEW_START
import base64

router = APIRouter()


# REGISTER USER
@router.post("/register")
async def register(name: str = Form(...), roll_no: str = Form(...), room_no: str = Form(...), image: UploadFile = File(...)):
    db: Session = SessionLocal()

    img_bytes = await image.read()
    img_str = "data:image/jpeg;base64," + base64.b64encode(img_bytes).decode()

    image = base64_to_image(img_str)
    embedding = get_embedding(image)

    if embedding is None:
        raise HTTPException(status_code=400, detail="No face detected in the provided image")

    user = User(
        name=name,
        roll_no=roll_no,
        room_no=room_no,
        embedding=json.dumps(embedding.tolist())
    )

    db.add(user)
    db.commit()

    return {"message": "User registered"}


# ATTENDANCE
@router.post("/attendance")
async def mark_attendance(image: UploadFile = File(...)):
    db = SessionLocal()

    img_bytes = await image.read()
    img_str = "data:image/jpeg;base64," + base64.b64encode(img_bytes).decode()

    image = base64_to_image(img_str)
    new_embedding = get_embedding(image)

    if new_embedding is None:
        return {"status": "No face detected"}

    # ❗ CURFEW CHECK
    if not is_within_curfew():
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


@router.get("/users")
def get_users():
    db = SessionLocal()
    users = db.query(User).all()
    return [{"id": u.id, "name": u.name, "roll_no": u.roll_no, "room_no": u.room_no} for u in users]


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