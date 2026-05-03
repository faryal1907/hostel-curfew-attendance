from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.models.database import Base, engine
from backend.app.routes import router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

import hashlib

def get_password_hash(password: str):
    return hashlib.sha256(password.encode()).hexdigest()

Base.metadata.create_all(bind=engine)

# Seed default admin
from backend.models.database import SessionLocal, Admin
db = SessionLocal()
if not db.query(Admin).filter(Admin.username == "admin").first():
    admin = Admin(
        username="admin",
        email="manager@nust.edu.pk",
        password_hash=get_password_hash("admin123")
    )
    db.add(admin)
    db.commit()
db.close()

app.include_router(router)