from backend.models.database import SessionLocal, User, AttendanceLog
from backend.models.curfew import is_curfew_over, CURFEW_START

db = SessionLocal()
users = db.query(User).all()
logs = db.query(AttendanceLog).all()

print(f"Curfew Start: {CURFEW_START}")
print(f"Is Curfew Over? {is_curfew_over()}")

print("\n--- Registered Users ---")
for u in users:
    print(f"ID: {u.id}, Name: {u.name}")

print("\n--- Attendance Logs ---")
for l in logs:
    print(f"User ID: {l.user_id}, Status: {l.status}, Time: {l.timestamp}")

db.close()
