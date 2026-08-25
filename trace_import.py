import sys

class TraceImporter:
    def find_spec(self, fullname, path, target=None):
        print(f"Importing: {fullname}")
        return None

sys.meta_path.insert(0, TraceImporter())

import app
