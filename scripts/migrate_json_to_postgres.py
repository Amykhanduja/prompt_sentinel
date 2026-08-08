import os
import sys
import json
import time
import uuid
import logging
from datetime import datetime, UTC
from collections import Counter

# Add project root to Python path
PROJECT_ROOT = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)
sys.path.insert(0, PROJECT_ROOT)

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

from database.connection import SessionLocal
from database.models.models import (
    Scan,
    Detection,
    Alert,
    Statistics,
)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

ALERTS_FILE = os.path.join(PROJECT_ROOT, "logs", "alerts.json")
STATS_FILE = os.path.join(PROJECT_ROOT, "logs", "statistics.json")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)

logger = logging.getLogger("promptsentinel.migration")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def parse_timestamp(value):
    """
    Convert legacy timestamp values into timezone-aware datetime objects.
    """
    if not value:
        return datetime.now(UTC)

    try:
        timestamp = datetime.fromisoformat(str(value))

        if timestamp.tzinfo is None:
            timestamp = timestamp.replace(tzinfo=UTC)

        return timestamp

    except (ValueError, TypeError):
        logger.warning(
            "Invalid timestamp %r. Using current UTC time.",
            value,
        )
        return datetime.now(UTC)


def normalize_action(alert):
    """
    Legacy JSON contains action in several formats:

        "action": "BLOCK"

    or:

        "action": {
            "decision": "BLOCK",
            "reason": "critical_score"
        }

    or:

        "policy_decision": "block"

    or no action at all.
    """

    action = alert.get("action")

    if isinstance(action, str):
        return action.upper()

    if isinstance(action, dict):
        decision = action.get("decision")

        if decision:
            return str(decision).upper()

    policy_decision = alert.get("policy_decision")

    if isinstance(policy_decision, str):
        return policy_decision.upper()

    return "ALLOW"


def normalize_source(alert):
    """
    Preserve the source from legacy JSON.

    Existing legacy values include:
        user
        markdown
        pdf
        missing
    """

    source = alert.get("source")

    if source:
        return str(source)

    return "legacy"


def normalize_risk(alert):
    """
    Extract risk information from both old and new JSON formats.
    """

    risk = alert.get("risk")

    if isinstance(risk, dict):
        return {
            "score": risk.get(
                "score",
                alert.get("risk_score", 0),
            ),
            "severity": risk.get(
                "severity",
                alert.get("severity", "low"),
            ),
            "summary": risk.get("summary"),
            "breakdown": risk.get("breakdown"),
        }

    return {
        "score": alert.get("risk_score", 0),
        "severity": alert.get("severity", "low"),
        "summary": None,
        "breakdown": None,
    }


def normalize_detection_records(alert):
    """
    Convert every supported legacy JSON format into a common
    detection representation.

    Supported formats:

    1.:
        "detections": ["PT-009", "PT-013"]

    2.:
        "technique": "PT-009",
        "confidence": 0.8,
        "detectors": ["regex"]

    3.:
        "risk": {
            "breakdown": [...]
        }

    4.:
        combination of the above.

    Returns:

        [
            {
                "technique": "...",
                "detector": "...",
                "confidence": ...,
                "severity": "...",
                "evidence": [...]
            }
        ]
    """

    detections = []

    alert_severity = alert.get("severity", "low")

    # ------------------------------------------------------------------
    # Format 1: detections = ["PT-009", "PT-013", ...]
    # ------------------------------------------------------------------

    legacy_detections = alert.get("detections")

    if isinstance(legacy_detections, list):

        for technique in legacy_detections:

            if not isinstance(technique, str):
                continue

            detections.append(
                {
                    "technique": technique,
                    "detector": "legacy",
                    "confidence": 1.0,
                    "severity": alert_severity,
                    "evidence": [],
                }
            )

    # ------------------------------------------------------------------
    # Format 2: technique + confidence + detectors
    # ------------------------------------------------------------------

    technique = alert.get("technique")

    if technique:

        detectors = alert.get("detectors")

        if isinstance(detectors, list) and detectors:

            detector_name = ",".join(
                str(x) for x in detectors
            )

        elif isinstance(detectors, str):

            detector_name = detectors

        else:

            detector_name = "legacy"

        confidence = alert.get(
            "confidence",
            1.0,
        )

        detections.append(
            {
                "technique": technique,
                "detector": detector_name,
                "confidence": confidence,
                "severity": alert_severity,
                "evidence": [],
            }
        )

    # ------------------------------------------------------------------
    # Format 3: risk.breakdown
    # ------------------------------------------------------------------

    risk = alert.get("risk")

    if isinstance(risk, dict):

        breakdown = risk.get("breakdown")

        if isinstance(breakdown, list):

            for item in breakdown:

                if not isinstance(item, dict):
                    continue

                technique = item.get("technique")

                if not technique:
                    continue

                # Avoid duplicating detections already generated
                # from the explicit "detections" or "technique" fields.
                already_exists = any(
                    d["technique"] == technique
                    and d["detector"] == "legacy"
                    for d in detections
                )

                if already_exists:
                    continue

                confidence = item.get(
                    "confidence",
                    alert.get("confidence", 1.0),
                )

                detector = item.get(
                    "detector",
                    "legacy",
                )

                detections.append(
                    {
                        "technique": technique,
                        "detector": detector,
                        "confidence": confidence,
                        "severity": alert_severity,
                        "evidence": [item],
                    }
                )

    return detections


def get_or_create_scan(
    db,
    alert,
    stats,
):
    """
    Create a Scan only if it doesn't already exist.

    The legacy alert_id becomes the PostgreSQL scan UUID so that
    migration remains deterministic and idempotent.
    """

    raw_id = alert.get("alert_id")

    if not raw_id:
        stats["alerts_errors"] += 1

        logger.warning(
            "Skipping record without alert_id."
        )

        return None

    try:
        scan_id = uuid.UUID(str(raw_id))

    except (ValueError, AttributeError, TypeError):

        stats["alerts_errors"] += 1

        logger.warning(
            "Invalid alert_id %r",
            raw_id,
        )

        return None

    existing_scan = db.execute(
        select(Scan).where(
            Scan.id == scan_id
        )
    ).scalar_one_or_none()

    if existing_scan:

        stats["alerts_skipped"] += 1

        return existing_scan

    timestamp = parse_timestamp(
        alert.get("timestamp")
    )

    risk = normalize_risk(alert)

    prompt = alert.get(
        "prompt",
        "",
    )

    if prompt is None:
        prompt = ""

    prompt = str(prompt)

    source = normalize_source(alert)

    action = normalize_action(alert)

    scan = Scan(
        id=scan_id,
        timestamp=timestamp,
        prompt=prompt,
        prompt_length=len(prompt),
        risk_score=int(
            risk.get("score") or 0
        ),
        severity=str(
            risk.get("severity")
            or "low"
        ).lower(),
        action=action,
        source=source,
        risk_summary=risk.get(
            "summary"
        ),
        risk_breakdown=risk.get(
            "breakdown"
        ),
    )

    db.add(scan)

    db.flush()

    return scan


def create_detections(
    db,
    scan,
    alert,
    stats,
):
    """
    Insert all detections associated with a scan.

    Existing detections are checked first so rerunning the migration
    does not duplicate them.
    """

    detection_records = normalize_detection_records(
        alert
    )

    if not detection_records:
        return 0

    existing = db.execute(
        select(Detection).where(
            Detection.scan_id == scan.id
        )
    ).scalars().all()

    existing_keys = {
        (
            d.technique,
            d.detector,
            d.severity,
        )
        for d in existing
    }

    inserted = 0

    for detection_data in detection_records:

        technique = detection_data.get(
            "technique"
        )

        if not technique:
            continue

        detector = detection_data.get(
            "detector",
            "legacy",
        )

        severity = detection_data.get(
            "severity",
            "low",
        )

        key = (
            technique,
            detector,
            severity,
        )

        if key in existing_keys:
            continue

        confidence = detection_data.get(
            "confidence",
            1.0,
        )

        try:
            confidence = float(
                confidence
            )
        except (
            ValueError,
            TypeError,
        ):
            confidence = 1.0

        confidence = max(
            0.0,
            min(1.0, confidence),
        )

        detection = Detection(
            scan_id=scan.id,
            technique=technique,
            detector=detector,
            confidence=confidence,
            severity=severity,
            evidence=detection_data.get(
                "evidence",
                [],
            ),
        )

        db.add(detection)

        existing_keys.add(key)

        inserted += 1

    return inserted


def create_alert(
    db,
    scan,
    alert,
):
    """
    Create the Alert row if it does not already exist.
    """

    existing_alert = db.execute(
        select(Alert).where(
            Alert.scan_id == scan.id
        )
    ).scalar_one_or_none()

    if existing_alert:
        return False

    timestamp = parse_timestamp(
        alert.get("timestamp")
    )

    alert_row = Alert(
        scan_id=scan.id,
        timestamp=timestamp,
        is_read=False,
    )

    db.add(alert_row)

    return True


# ---------------------------------------------------------------------------
# Alerts migration
# ---------------------------------------------------------------------------

def migrate_alerts(db, stats):

    if not os.path.exists(ALERTS_FILE):

        logger.warning(
            "%s not found. Skipping.",
            ALERTS_FILE,
        )

        return

    logger.info(
        "Loading %s",
        ALERTS_FILE,
    )

    with open(
        ALERTS_FILE,
        "r",
        encoding="utf-8",
    ) as f:

        alerts_data = json.load(f)

    if not isinstance(alerts_data, list):

        raise ValueError(
            "alerts.json must contain a JSON list"
        )

    stats["json_records"] = len(
        alerts_data
    )

    logger.info(
        "Found %d legacy alert records",
        len(alerts_data),
    )

    for index, alert_json in enumerate(
        alerts_data,
        start=1,
    ):

        try:

            scan = get_or_create_scan(
                db,
                alert_json,
                stats,
            )

            if scan is None:
                continue

            # Only create missing detections.
            detection_count = create_detections(
                db,
                scan,
                alert_json,
                stats,
            )

            # Create corresponding alert.
            alert_created = create_alert(
                db,
                scan,
                alert_json,
            )

            db.commit()

            if detection_count:
                stats[
                    "detections_imported"
                ] += detection_count

            if alert_created:
                stats[
                    "alerts_imported"
                ] += 1

            if index % 25 == 0:
                logger.info(
                    "Processed %d/%d records",
                    index,
                    len(alerts_data),
                )

        except SQLAlchemyError as e:

            db.rollback()

            stats[
                "alerts_errors"
            ] += 1

            logger.error(
                "Database error for record %d: %s",
                index,
                e,
            )

        except Exception as e:

            db.rollback()

            stats[
                "alerts_errors"
            ] += 1

            logger.error(
                "Error processing record %d: %s",
                index,
                e,
            )


# ---------------------------------------------------------------------------
# Statistics migration
# ---------------------------------------------------------------------------

def migrate_statistics(
    db,
    stats,
):

    if not os.path.exists(STATS_FILE):

        logger.warning(
            "%s not found. Skipping.",
            STATS_FILE,
        )

        return

    logger.info(
        "Loading %s",
        STATS_FILE,
    )

    with open(
        STATS_FILE,
        "r",
        encoding="utf-8",
    ) as f:

        stats_data = json.load(f)

    if not isinstance(
        stats_data,
        dict,
    ):

        raise ValueError(
            "statistics.json must contain a JSON object"
        )

    existing_stats = db.execute(
        select(Statistics)
    ).scalars().first()

    if existing_stats:

        logger.info(
            "Statistics row already exists. Updating it from legacy JSON."
        )

        existing_stats.total_alerts = (
            stats_data.get(
                "total_alerts",
                existing_stats.total_alerts,
            )
        )

        existing_stats.techniques = (
            stats_data.get(
                "techniques",
                existing_stats.techniques or {},
            )
        )

        existing_stats.severities = (
            stats_data.get(
                "severities",
                existing_stats.severities or {},
            )
        )

        db.commit()

        stats[
            "statistics_updated"
        ] += 1

        return

    statistics = Statistics(
        total_alerts=stats_data.get(
            "total_alerts",
            0,
        ),
        techniques=stats_data.get(
            "techniques",
            {},
        ),
        severities=stats_data.get(
            "severities",
            {},
        ),
    )

    db.add(statistics)

    db.commit()

    stats[
        "statistics_imported"
    ] += 1


# ---------------------------------------------------------------------------
# Verification
# ---------------------------------------------------------------------------

def verify_database(db):

    scan_count = db.execute(
        select(Scan)
    ).scalars().all()

    detection_count = db.execute(
        select(Detection)
    ).scalars().all()

    alert_count = db.execute(
        select(Alert)
    ).scalars().all()

    statistics = db.execute(
        select(Statistics)
    ).scalars().all()

    print("\n==============================")
    print("POSTGRESQL VERIFICATION")
    print("==============================")

    print(
        f"Scans:       {len(scan_count)}"
    )

    print(
        f"Detections:  {len(detection_count)}"
    )

    print(
        f"Alerts:      {len(alert_count)}"
    )

    print(
        f"Statistics:  {len(statistics)}"
    )

    # Detection breakdown
    technique_counts = Counter(
        d.technique
        for d in detection_count
        if d.technique
    )

    print(
        "\nDetection techniques:"
    )

    for technique, count in (
        technique_counts.most_common()
    ):

        print(
            f"  {technique}: {count}"
        )

    # Detector breakdown
    detector_counts = Counter(
        (
            d.technique,
            d.detector,
            d.severity,
        )
        for d in detection_count
    )

    print(
        "\nTechnique / detector / severity:"
    )

    for (
        technique,
        detector,
        severity,
    ), count in detector_counts.most_common():

        print(
            f"  {technique:8} | "
            f"{str(detector):14} | "
            f"{str(severity):8} | "
            f"{count}"
        )

    print(
        "=============================="
    )


# ---------------------------------------------------------------------------
# Main migration
# ---------------------------------------------------------------------------

def migrate():

    print(
        "\n========================================"
    )
    print(
        " PromptSentinel JSON → PostgreSQL"
    )
    print(
        "========================================\n"
    )

    start_time = time.time()

    stats = {
        "json_records": 0,
        "alerts_imported": 0,
        "alerts_skipped": 0,
        "alerts_errors": 0,
        "detections_imported": 0,
        "statistics_imported": 0,
        "statistics_updated": 0,
    }

    db = SessionLocal()

    try:

        migrate_alerts(
            db,
            stats,
        )

        migrate_statistics(
            db,
            stats,
        )

        verify_database(db)

    except Exception as e:

        db.rollback()

        logger.exception(
            "Migration failed: %s",
            e,
        )

        raise

    finally:

        db.close()

    execution_time = (
        time.time() - start_time
    )

    print(
        "\n========================================"
    )
    print(
        " MIGRATION SUMMARY"
    )
    print(
        "========================================"
    )

    print(
        f"JSON records:          "
        f"{stats['json_records']}"
    )

    print(
        f"Alerts imported:       "
        f"{stats['alerts_imported']}"
    )

    print(
        f"Alerts skipped:        "
        f"{stats['alerts_skipped']}"
    )

    print(
        f"Alert errors:          "
        f"{stats['alerts_errors']}"
    )

    print(
        f"Detections imported:   "
        f"{stats['detections_imported']}"
    )

    print(
        f"Statistics imported:   "
        f"{stats['statistics_imported']}"
    )

    print(
        f"Statistics updated:    "
        f"{stats['statistics_updated']}"
    )

    print(
        f"Execution time:        "
        f"{execution_time:.2f}s"
    )

    print(
        "========================================"
    )

    print(
        "\nMigration complete."
    )


if __name__ == "__main__":
    migrate()
