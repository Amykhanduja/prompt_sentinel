from policies.policy_engine import decide_action


def test_low_score():
    assert decide_action(
        {"score": 15, "severity": "low"}
    ) == "ALLOW"


def test_medium_score():
    assert decide_action(
        {"score": 45, "severity": "medium"}
    ) == "MONITOR"


def test_high_score():
    assert decide_action(
        {"score": 105, "severity": "critical"}
    ) == "BLOCK"
