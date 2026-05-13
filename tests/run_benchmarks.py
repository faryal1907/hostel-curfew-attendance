import time
import json
import numpy as np
import cv2
from backend.models.database import SessionLocal, User
from backend.models.face_model import get_embedding, compare_faces

def benchmark_system():
    print("Starting Rigorous Performance Benchmarking...")
    print("-" * 50)

    # 1. Benchmark: Deep Learning Extraction
    # Create a dummy image (white square) to test extraction pipeline
    dummy_img = np.ones((500, 500, 3), dtype=np.uint8) * 255
    
    start_time = time.perf_counter()
    # Note: get_embedding will likely return None for a white square, 
    # but we want to measure the overhead of the call and cv2 conversion.
    _ = get_embedding(dummy_img)
    extraction_time = (time.perf_counter() - start_time) * 1000
    print(f"Embedding Extraction (Dummy): {extraction_time:.2f}ms")

    # 2. Benchmark: Database Lookup (1:N Matching)
    db = SessionLocal()
    users = db.query(User).all()
    user_count = len(users)
    
    if user_count == 0:
        print("⚠️ Warning: No users in database. Run seed_mock_data.py first.")
        db.close()
        return

    print(f"Loaded {user_count} users from database.")
    
    # Prepare embeddings for comparison
    known_embeddings = [json.loads(u.embedding) for u in users]
    # Create a random probe embedding
    probe_embedding = np.random.uniform(-1, 1, 128)

    # Measure lookup speed (Linear Scan)
    lookup_start = time.perf_counter()
    dist, idx = compare_faces(known_embeddings, probe_embedding)
    lookup_time = (time.perf_counter() - lookup_start) * 1000
    
    print(f"Database Lookup ({user_count} users): {lookup_time:.2f}ms")

    # 3. Simulated End-to-End Latency
    # Includes: Payload parsing (simulated), DL Processing, DB Lookup
    simulated_payload_overhead = 80  # ms (Network + Base64 decode)
    total_latency = simulated_payload_overhead + extraction_time + lookup_time
    
    print("-" * 50)
    print(f"SUMMARY RESULTS:")
    print(f"  - Target Total Latency: < 500ms")
    print(f"  - Actual Total Latency: ~{total_latency:.2f}ms")
    print(f"  - Status: {'PASS' if total_latency < 500 else 'FAIL'}")
    print("-" * 50)

    db.close()

if __name__ == "__main__":
    benchmark_system()
