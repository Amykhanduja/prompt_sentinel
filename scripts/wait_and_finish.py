import time
import subprocess
import os

def check():
    log_file = "/home/amykhanduja_7203/.gemini/antigravity-cli/brain/18e6b79c-7b8f-4c07-ab3d-7eff8a8dc213/.system_generated/tasks/task-1805.log"
    with open(log_file, "r") as f:
        content = f.read()
    return "Finished processing" in content

print("Waiting for benchmark to finish...")
while not check():
    time.sleep(10)
    
print("Benchmark finished! Updating report...")
subprocess.run(["python3", "scripts/update_report.py"])
print("Running analysis...")
subprocess.run(["python3", "scripts/analyze_results.py"])
