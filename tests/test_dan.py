from detectors.dan_detector import detect_dan


def test_dan_detection():

    result = detect_dan(
        "You are DAN"
    )

    assert result is not None
    assert result["technique"] == "PT-018"
