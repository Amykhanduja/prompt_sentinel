"""initial

Revision ID: 91edaf88eca2
Revises: 
Create Date: 2026-07-30 21:07:03.380046

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '91edaf88eca2'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # scans
    op.create_table('scans',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('timestamp', sa.DateTime(timezone=True), nullable=False),
        sa.Column('prompt', sa.Text(), nullable=False),
        sa.Column('prompt_length', sa.Integer(), nullable=False),
        sa.Column('risk_score', sa.Integer(), nullable=False),
        sa.Column('severity', sa.String(), nullable=False),
        sa.Column('action', sa.String(), nullable=False),
        sa.Column('source', sa.String(), nullable=False),
        sa.Column('preprocessing_flags', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('risk_summary', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('risk_breakdown', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_scans_timestamp'), 'scans', ['timestamp'], unique=False)

    # detections
    op.create_table('detections',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('scan_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('technique', sa.String(), nullable=False),
        sa.Column('detector', sa.String(), nullable=True),
        sa.Column('confidence', sa.Float(), nullable=False),
        sa.Column('severity', sa.String(), nullable=False),
        sa.Column('evidence', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.ForeignKeyConstraint(['scan_id'], ['scans.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_detections_scan_id'), 'detections', ['scan_id'], unique=False)
    op.create_index(op.f('ix_detections_technique'), 'detections', ['technique'], unique=False)

    # alerts
    op.create_table('alerts',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('scan_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('timestamp', sa.DateTime(timezone=True), nullable=False),
        sa.Column('is_read', sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(['scan_id'], ['scans.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('scan_id')
    )
    op.create_index(op.f('ix_alerts_timestamp'), 'alerts', ['timestamp'], unique=False)

    # statistics
    op.create_table('statistics',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('total_alerts', sa.Integer(), nullable=False),
        sa.Column('techniques', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('severities', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

    # api_logs
    op.create_table('api_logs',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('timestamp', sa.DateTime(timezone=True), nullable=False),
        sa.Column('endpoint', sa.String(), nullable=False),
        sa.Column('method', sa.String(), nullable=False),
        sa.Column('response_time', sa.Float(), nullable=True),
        sa.Column('status_code', sa.Integer(), nullable=True),
        sa.Column('client_ip', sa.String(), nullable=True),
        sa.Column('event', sa.String(), nullable=False),
        sa.Column('details', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_api_logs_timestamp'), 'api_logs', ['timestamp'], unique=False)
    op.create_index(op.f('ix_api_logs_endpoint'), 'api_logs', ['endpoint'], unique=False)

    # dashboard_metrics
    op.create_table('dashboard_metrics',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('timestamp', sa.DateTime(timezone=True), nullable=False),
        sa.Column('metric_name', sa.String(), nullable=False),
        sa.Column('metric_value', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_dashboard_metrics_metric_name'), 'dashboard_metrics', ['metric_name'], unique=False)

    # scan_history
    op.create_table('scan_history',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('scan_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('timestamp', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['scan_id'], ['scans.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_scan_history_timestamp'), 'scan_history', ['timestamp'], unique=False)

    # file_metadata
    op.create_table('file_metadata',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('file_path', sa.String(), nullable=False),
        sa.Column('scan_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('metadata_json', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.ForeignKeyConstraint(['scan_id'], ['scans.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # parser_metadata
    op.create_table('parser_metadata',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('parser_name', sa.String(), nullable=False),
        sa.Column('scan_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('metadata_json', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.ForeignKeyConstraint(['scan_id'], ['scans.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # system_status
    op.create_table('system_status',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('last_updated', sa.DateTime(timezone=True), nullable=False),
        sa.Column('status_json', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    op.drop_table('system_status')
    op.drop_table('parser_metadata')
    op.drop_table('file_metadata')
    op.drop_index(op.f('ix_scan_history_timestamp'), table_name='scan_history')
    op.drop_table('scan_history')
    op.drop_index(op.f('ix_dashboard_metrics_metric_name'), table_name='dashboard_metrics')
    op.drop_table('dashboard_metrics')
    op.drop_index(op.f('ix_api_logs_endpoint'), table_name='api_logs')
    op.drop_index(op.f('ix_api_logs_timestamp'), table_name='api_logs')
    op.drop_table('api_logs')
    op.drop_table('statistics')
    op.drop_index(op.f('ix_alerts_timestamp'), table_name='alerts')
    op.drop_table('alerts')
    op.drop_index(op.f('ix_detections_technique'), table_name='detections')
    op.drop_index(op.f('ix_detections_scan_id'), table_name='detections')
    op.drop_table('detections')
    op.drop_index(op.f('ix_scans_timestamp'), table_name='scans')
    op.drop_table('scans')
