from scoring.risk_engine import calculate_risk


def test_single_detection_risk():

    detections = [
        {
            "technique": "PT-009"
        }
    ]

    risk = calculate_risk(detections)

    assert risk["score"] == 30
    assert risk["severity"] == "medium"


def test_multiple_detection_risk():

    detections = [
        {"technique": "PT-009"},
        {"technique": "PT-013"}
    ]

    risk = calculate_risk(detections)

    assert risk["score"] == 70
    assert risk["severity"] == "high"
