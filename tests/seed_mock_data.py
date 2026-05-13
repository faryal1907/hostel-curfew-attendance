import json
import numpy as np
from backend.models.database import SessionLocal, User, Base, engine

def seed_mock_students(count=1000):
    print(f"Initializing database seeding for {count} mock students...")
    
    # Ensure tables exist
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    # Clear existing mock data to avoid duplicates if needed, 
    # but usually we just add on top or clear all.
    # db.query(User).delete() 
    
    students = []
    for i in range(count):
        # Generate a random 128-dimensional vector
        mock_embedding = np.random.uniform(-1, 1, 128).tolist()
        
        student = User(
            name=f"Mock Student {i+1}",
            roll_no=f"99{str(i).zfill(4)}", # Mock roll numbers
            hostel_name="ayesha",
            room_no=f"M-{i+1}",
            embedding=json.dumps(mock_embedding)
        )
        students.append(student)
        
        if (i + 1) % 100 == 0:
            print(f"  - Generated {i + 1} students...")

    db.add_all(students)
    db.commit()
    db.close()
    
    print(f"Successfully seeded {count} mock students with 128D embeddings.")

if __name__ == "__main__":
    seed_mock_students(1000)
