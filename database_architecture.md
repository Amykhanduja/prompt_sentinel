# PromptSentinel Database Architecture

## Relational Models

```mermaid
erDiagram
    Scan {
        UUID id PK
        DateTime timestamp
        Text prompt
        Integer prompt_length
        Integer risk_score
        String severity
        String action
        String source
        JSONB preprocessing_flags
        JSONB risk_summary
        JSONB risk_breakdown
    }
    
    Detection {
        UUID id PK
        UUID scan_id FK
        String technique
        String detector
        Float confidence
        String severity
        JSONB evidence
    }
    
    Alert {
        UUID id PK
        UUID scan_id FK
        DateTime timestamp
        Boolean is_read
    }
    
    ScanHistory {
        UUID id PK
        UUID scan_id FK
        DateTime timestamp
    }
    
    Statistics {
        Integer id PK
        DateTime updated_at
        Integer total_alerts
        JSONB techniques
        JSONB severities
    }
    
    ApiLog {
        UUID id PK
        DateTime timestamp
        String endpoint
        String method
        Float response_time
        Integer status_code
        String client_ip
        String event
        JSONB details
    }
    
    DashboardMetrics {
        Integer id PK
        DateTime timestamp
        String metric_name
        JSONB metric_value
    }
    
    FileMetadata {
        UUID id PK
        String file_path
        UUID scan_id FK
        JSONB metadata_json
    }
    
    ParserMetadata {
        UUID id PK
        String parser_name
        UUID scan_id FK
        JSONB metadata_json
    }
    
    SystemStatus {
        Integer id PK
        DateTime last_updated
        JSONB status_json
    }

    Scan ||--o{ Detection : "has"
    Scan ||--o| Alert : "generates"
    Scan ||--o| ScanHistory : "logged in"
    Scan ||--o| FileMetadata : "has"
    Scan ||--o| ParserMetadata : "has"
```

## Description
The architecture uses a star-like pattern around the `Scan` entity, which is the core domain model representing a processed prompt. `Detection`, `Alert`, and `FileMetadata` all use foreign keys with cascading deletes mapped to the `Scan.id` primary key.

`Statistics`, `DashboardMetrics`, `SystemStatus`, and `ApiLog` are standalone operational tables used for aggregations and tracking metrics without bloating the primary operational logic.
