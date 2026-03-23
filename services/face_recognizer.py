import cv2
import numpy as np
import pickle
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from deepface import DeepFace
from scipy.spatial.distance import cosine
from db.db_manager import DatabaseManager
from config import FACE_MODEL, FACE_DETECTOR, SIMILARITY_THRESHOLD

class FaceRecognizer:
    def __init__(self):
        self.db = DatabaseManager()
        self.known_embeddings = []
        self.load_embeddings_from_db()

    def load_embeddings_from_db(self):
        rows = self.db.fetch_all('SELECT * FROM face_embeddings')
        self.known_embeddings = []
        for row in rows:
            emb = pickle.loads(row['embedding'])
            self.known_embeddings.append({
                'person_type': row['person_type'],
                'person_id': row['person_id'],
                'embedding': emb
            })
        print(f'[FaceRecognizer] Loaded {len(self.known_embeddings)} embeddings.')

    def extract_embedding(self, face_img):
        try:
            # Resize large images
            if isinstance(face_img, np.ndarray):
                h, w = face_img.shape[:2]
                if h > 640 or w > 640:
                    scale = 640 / max(h, w)
                    face_img = cv2.resize(face_img, (int(w * scale), int(h * scale)))

            result = DeepFace.represent(
                img_path=face_img,
                model_name=FACE_MODEL,
                detector_backend=FACE_DETECTOR,
                enforce_detection=False
            )

            # DeepFace 0.0.75 returns flat list of floats directly
            if isinstance(result, list) and len(result) > 0:
                if isinstance(result[0], float):
                    return np.array(result)          # flat list — use directly
                if isinstance(result[0], dict) and 'embedding' in result[0]:
                    return np.array(result[0]['embedding'])  # newer format

            return None

        except Exception as e:
            print(f'[FaceRecognizer] Embedding error: {e}')
            return None

    def recognize(self, face_img):
        query_emb = self.extract_embedding(face_img)
        if query_emb is None or not self.known_embeddings:
            return {'person_type': 'unknown', 'person_id': None, 'confidence': 0.0}
        best_match, min_dist = None, float('inf')
        for record in self.known_embeddings:
            dist = cosine(query_emb, record['embedding'])
            if dist < min_dist:
                min_dist = dist
                best_match = record
        confidence = round(1.0 - min_dist, 4)
        if min_dist <= SIMILARITY_THRESHOLD and best_match:
            return {'person_type': best_match['person_type'], 'person_id': best_match['person_id'], 'confidence': confidence}
        return {'person_type': 'unknown', 'person_id': None, 'confidence': confidence}

    def add_face(self, person_type, person_id, image_path):
        emb = self.extract_embedding(image_path)
        if emb is None:
            raise ValueError('No face detected.')
        self.db.execute(
            'INSERT INTO face_embeddings (person_type, person_id, image_path, embedding, model_used) VALUES (?,?,?,?,?)',
            (person_type, person_id, image_path, pickle.dumps(emb), FACE_MODEL)
        )
        self.load_embeddings_from_db()
        print(f'[FaceRecognizer] Face added: {person_type} id={person_id}')
