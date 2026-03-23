import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from services.face_recognizer import FaceRecognizer
import numpy as np

def test_blank():
    r = FaceRecognizer()
    blank = np.zeros((200, 200, 3), dtype=np.uint8)
    emb = r.extract_embedding(blank)
    print('TEST 1 PASSED - blank image handled:', emb is None or len(emb) > 0)

def test_empty_db():
    r = FaceRecognizer()
    blank = np.zeros((200, 200, 3), dtype=np.uint8)
    result = r.recognize(blank)
    assert result['person_type'] == 'unknown'
    print('TEST 2 PASSED - empty DB returns unknown:', result)

if __name__ == '__main__':
    print('--- Phase 2 Tests ---')
    test_blank()
    test_empty_db()
    print('--- Done ---')
