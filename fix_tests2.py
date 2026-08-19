import re

with open("tests/test_phase18_1_feedback.py", "r") as f:
    c = f.read()

c = c.replace("Feedb_session.ck", "Feedback")
c = c.replace("feedb_session.ck", "feedback")
c = c.replace("db_session.session", "db_session")
c = c.replace("db_session.db_session", "db_session")

# Now strip db_session fixture
db_session_pattern = re.compile(r'@pytest\.fixture\(scope="module"\)\ndef db_session\(\):\n\s+yield db\n\s+db_session\.close\(\)\n+', re.MULTILINE)
c = db_session_pattern.sub('', c)

with open("tests/test_phase18_1_feedback.py", "w") as f:
    f.write(c)
