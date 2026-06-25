from detectors.engine import run_detectors


def test_benign_prompt():

    prompt = (
        "What are the benefits of Python?"
    )

    detections = run_detectors(prompt)

    assert detections == []
