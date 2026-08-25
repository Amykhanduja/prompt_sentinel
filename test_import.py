import sys
import time

print("Importing app...")
try:
    import app
    print("Successfully imported app.")
except Exception as e:
    print(f"Failed to import app: {e}")

