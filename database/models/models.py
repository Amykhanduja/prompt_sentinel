import uuid
from datetime import datetime, UTC
from typing import List, Optional
from sqlalchemy import String, Integer, Float, DateTime, ForeignKey, JSON, Text, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID as PGUUID, JSONB
from database.base import Base

class Scan(Base):
    __tablename__ = "scans"

    id: Mapped[uuid.UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC), index=True)
    prompt: Mapped[str] = mapped_column(Text, nullable=False)
    prompt_length: Mapped[int] = mapped_column(Integer, nullable=False)
    risk_score: Mapped[int] = mapped_column(Integer, default=0)
    severity: Mapped[str] = mapped_column(String, default="low")
    action: Mapped[str] = mapped_column(String, default="ALLOW")
    source: Mapped[str] = mapped_column(String, default="User")
    preprocessing_flags: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    risk_summary: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    risk_breakdown: Mapped[Optional[list]] = mapped_column(JSONB, nullable=True)

    detections: Mapped[List["Detection"]] = relationship("Detection", back_populates="scan", cascade="all, delete-orphan")
    alert: Mapped[Optional["Alert"]] = relationship("Alert", back_populates="scan", cascade="all, delete-orphan", uselist=False)

class Detection(Base):
    __tablename__ = "detections"

    id: Mapped[uuid.UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    scan_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("scans.id", ondelete="CASCADE"), nullable=False, index=True)
    technique: Mapped[str] = mapped_column(String, nullable=False, index=True)
    detector: Mapped[Optional[str]] = mapped_column(String)
    confidence: Mapped[float] = mapped_column(Float, default=1.0)
    severity: Mapped[str] = mapped_column(String, default="low")
    evidence: Mapped[Optional[list]] = mapped_column(JSONB, nullable=True) # Evidence details
    
    scan: Mapped["Scan"] = relationship("Scan", back_populates="detections")

class Alert(Base):
    __tablename__ = "alerts"

    id: Mapped[uuid.UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    scan_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("scans.id", ondelete="CASCADE"), nullable=False, unique=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC), index=True)
    is_read: Mapped[bool] = mapped_column(Boolean, default=False)
    
    scan: Mapped["Scan"] = relationship("Scan", back_populates="alert")

class Statistics(Base):
    __tablename__ = "statistics"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC))
    total_alerts: Mapped[int] = mapped_column(Integer, default=0)
    techniques: Mapped[dict] = mapped_column(JSONB, default=dict)
    severities: Mapped[dict] = mapped_column(JSONB, default=dict)

class ApiLog(Base):
    __tablename__ = "api_logs"

    id: Mapped[uuid.UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC), index=True)
    endpoint: Mapped[str] = mapped_column(String, nullable=False, index=True)
    method: Mapped[str] = mapped_column(String, nullable=False, default="GET")
    response_time: Mapped[Optional[float]] = mapped_column(Float)
    status_code: Mapped[Optional[int]] = mapped_column(Integer)
    client_ip: Mapped[Optional[str]] = mapped_column(String)
    event: Mapped[str] = mapped_column(String)
    details: Mapped[Optional[dict]] = mapped_column(JSONB)

class DashboardMetrics(Base):
    __tablename__ = "dashboard_metrics"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))
    metric_name: Mapped[str] = mapped_column(String, nullable=False, index=True)
    metric_value: Mapped[dict] = mapped_column(JSONB, nullable=False)

class ScanHistory(Base):
    __tablename__ = "scan_history"

    id: Mapped[uuid.UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    scan_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("scans.id", ondelete="CASCADE"), nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC), index=True)

class FileMetadata(Base):
    __tablename__ = "file_metadata"

    id: Mapped[uuid.UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    file_path: Mapped[str] = mapped_column(String, nullable=False)
    scan_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("scans.id", ondelete="CASCADE"), nullable=False)
    metadata_json: Mapped[dict] = mapped_column(JSONB)

class ParserMetadata(Base):
    __tablename__ = "parser_metadata"

    id: Mapped[uuid.UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    parser_name: Mapped[str] = mapped_column(String, nullable=False)
    scan_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("scans.id", ondelete="CASCADE"), nullable=False)
    metadata_json: Mapped[dict] = mapped_column(JSONB)

class SystemStatus(Base):
    __tablename__ = "system_status"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    last_updated: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC))
    status_json: Mapped[dict] = mapped_column(JSONB)

class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    email: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC))
