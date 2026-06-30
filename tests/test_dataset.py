import csv

from detectors.engine import run_detectors


def test_dataset():

    with open(
        "data/dataset.csv",
        newline="",
        encoding="utf-8"
    ) as file:

        reader = csv.DictReader(file)
        print(reader.fieldnames)
        for row in reader:

            payload = row["payload"]
            technique = row["technique"]
            expected = row["expected_action"]

            detections = run_detectors(payload)

            if expected == "allow":

                assert detections == [], (
                    f"Expected allow but detected: {payload}"
                )

            else:

                assert detections != [], (
                    f"No detection for: {payload}"
                )

                techniques = {
                    d["technique"]
                    for d in detections
                }
                print(payload)
                print(detections)
                assert technique in techniques, (
                    f"Expected {technique}, got {techniques}"
                )
