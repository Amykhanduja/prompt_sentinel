import os
import re

def process_file(filepath):
    with open(filepath, 'r') as f:
        content = f.read()

    # Remove SessionLocal import
    content = re.sub(r'from database\.connection import SessionLocal\n', '', content)
    
    # Remove client fixture
    client_pattern = re.compile(r'@pytest\.fixture\(scope="module"\)\ndef client\(\):\n\s+return TestClient\(app\)\n+', re.MULTILINE)
    content = client_pattern.sub('', content)

    # Remove db_session fixture
    db_session_pattern = re.compile(r'@pytest\.fixture\(scope="module"\)\ndef db_session\(\):\n\s+db = SessionLocal\(\)\n\s+yield db\n\s+db\.close\(\)\n+', re.MULTILINE)
    content = db_session_pattern.sub('', content)

    # Remove db_session function scope variant
    db_session_func_pattern = re.compile(r'@pytest\.fixture\(scope="function"\)\ndef db_session\(\):\n\s+db = SessionLocal\(\)\n\s+yield db\n\s+db\.close\(\)\n+', re.MULTILINE)
    content = db_session_func_pattern.sub('', content)

    # In test_phase18_2_feedback_api.py, there is a manual instantiation:
    content = content.replace('db = SessionLocal()', '')
    content = content.replace('db.add(detection2)', 'db_session.add(detection2)')
    content = content.replace('db.commit()', 'db_session.commit()')
    content = content.replace('db.refresh(detection2)', 'db_session.refresh(detection2)')
    content = content.replace('db.close()', '')

    with open(filepath, 'w') as f:
        f.write(content)

test_files = [
    "tests/test_phase18_2_feedback_api.py",
    "tests/test_phase18_3_feedback_analytics.py",
    "tests/test_phase18_4_learning_candidates.py",
    "tests/test_phase18_5_learning_review.py"
]

for tf in test_files:
    if os.path.exists(tf):
        process_file(tf)
        print(f"Processed {tf}")

