# Migration Report

## JSON Files Overview

### 1. `logs/alerts.json`
*   **Purpose**: Stores a history of prompt scanning alerts and detections, effectively acting as the central "Scan History" and "Alert Log".
*   **Schema**: List of objects containing `alert_id` (UUID), `timestamp`, `prompt`, `technique`, `severity`, `confidence`, `source`, `detectors`, `policy_decision`, and `risk_score`.
*   **Readers**:
    *   `api/dashboard.py` (Reads alerts to calculate KPIs, metrics, and list recent detections for the dashboard)
    *   `logs/alert_logger.py` (Reads existing alerts to append new ones)
*   **Writers**:
    *   `logs/alert_logger.py` (Appends new scan alerts to the JSON file)
*   **Replacement Tables**: `Scan`, `Detection`, `Alert`, `ScanHistory`
*   **Replacement Repository**: `AlertRepository`, `ScanRepository`, `DashboardRepository`

### 2. `logs/statistics.json`
*   **Purpose**: Maintains aggregated metrics over time (total alerts, technique distribution, severity distribution).
*   **Schema**: Object containing `total_alerts` (integer), `techniques` (dictionary mapping technique IDs to counts), and `severities` (dictionary mapping severity levels to counts).
*   **Readers**:
    *   `logs/alert_logger.py` (Reads to update the statistics)
*   **Writers**:
    *   `logs/alert_logger.py` (Writes updated statistics back to the JSON file)
*   **Replacement Table**: `Statistics`
*   **Replacement Repository**: `StatisticsRepository`

### Other Data Logged
*   **API Metrics/Logs**: Currently logged using `logger.info(json.dumps(...))` in `logs/api_logger.py` (e.g., `api_request`, `api_response`, `scan_completed`). This needs to be persisted in PostgreSQL.
    *   **Replacement Table**: `ApiLog`
    *   **Replacement Repository**: `ApiRepository`

## Migration Plan summary
1.  **Database Layer**: Create `database/` package with Base, Session, Models, and Repositories.
2.  **Models**: Create `Scan`, `Detection`, `Alert`, `Statistics`, `DashboardMetrics`, `ApiLog`, `ScanHistory`.
3.  **Alembic**: Initialize Alembic and create initial migration.
4.  **Repositories**: Provide methods for creating/querying this data.
5.  **Migration Script**: Create a script to read `logs/alerts.json` and `logs/statistics.json` and insert them into the DB.
6.  **Update Application**: Replace JSON interactions in `logs/alert_logger.py`, `logs/api_logger.py`, and `api/dashboard.py` with repository calls.
