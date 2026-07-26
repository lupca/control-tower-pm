"""schema v2 migration

Revision ID: 002_schema_v2
Revises: 001_initial
Create Date: 2026-07-26
"""
from alembic import op
import sqlalchemy as sa

revision = '002_schema_v2'
down_revision = '001_initial'
branch_labels = None
depends_on = None


def upgrade():
    # Drop legacy check constraint if exists to allow historical task import
    op.execute("ALTER TABLE tasks DROP CONSTRAINT IF EXISTS ck_tasks_four_eyes")

    # Alter existing columns to handle longer text values
    op.alter_column('audit_log', 'action', type_=sa.String(length=255))
    op.alter_column('audit_log', 'actor', type_=sa.String(length=255))
    op.alter_column('audit_log', 'task_id', type_=sa.String(length=255))

    op.alter_column('tasks', 'result_ref', type_=sa.String(length=255))
    op.alter_column('tasks', 'verdict', type_=sa.String(length=50))
    op.alter_column('tasks', 'predicted_success', type_=sa.String(length=50))
    op.alter_column('tasks', 'priority', type_=sa.String(length=50))
    op.alter_column('tasks', 'risk', type_=sa.String(length=50))

    # Projects table
    op.create_table(
        'projects',
        sa.Column('id', sa.String(length=50), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('repo_root', sa.String(length=255), nullable=True),
        sa.Column('task_prefix', sa.String(length=10), nullable=True),
        sa.Column('task_dir', sa.String(length=255), nullable=True),
        sa.Column('graph_status', sa.Text(), nullable=True),
        sa.Column('embed_status', sa.String(length=50), server_default='pending'),
        sa.Column('graph_embedded', sa.Text(), nullable=True),
        sa.Column('daemon_status', sa.String(length=50), server_default='stopped'),
        sa.Column('daemon_watch', sa.Text(), nullable=True),
        sa.Column('node_count', sa.Integer(), server_default='0'),
        sa.Column('edge_count', sa.Integer(), server_default='0'),
        sa.Column('patterns_exportable', sa.Boolean(), server_default='false'),
        sa.Column('status', sa.String(length=20), server_default='active'),
        sa.Column('done_count', sa.Integer(), server_default='0'),
        sa.Column('total_count', sa.Integer(), server_default='0'),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

    # Agents table
    op.create_table(
        'agents',
        sa.Column('id', sa.String(length=50), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=True),
        sa.Column('role', sa.Text(), nullable=True),
        sa.Column('type', sa.String(length=20), server_default='ai', nullable=False),
        sa.Column('status', sa.String(length=20), server_default='active'),
        sa.Column('model', sa.String(length=100), nullable=True),
        sa.Column('effort', sa.String(length=10), nullable=True),
        sa.Column('cli', sa.String(length=20), nullable=True),
        sa.Column('total_tasks_executed', sa.Integer(), server_default='0'),
        sa.Column('total_tasks_reviewed', sa.Integer(), server_default='0'),
        sa.Column('success_rate', sa.Float(), server_default='1.0'),
        sa.Column('avg_review_rounds', sa.Float(), server_default='1.0'),
        sa.Column('strengths', sa.JSON(), nullable=True),
        sa.Column('weaknesses', sa.JSON(), nullable=True),
        sa.Column('recent_trend', sa.String(length=20), nullable=True),
        sa.Column('superseded_by', sa.JSON(), nullable=True),
        sa.Column('last_active', sa.Date(), nullable=True),
        sa.Column('system_prompt', sa.Text(), nullable=True),
        sa.Column('file_path', sa.String(length=255), nullable=True),
        sa.Column('stats', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

    # Knowledge table
    op.create_table(
        'knowledge',
        sa.Column('id', sa.String(length=255), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=True),
        sa.Column('category', sa.String(length=50), nullable=True),
        sa.Column('path', sa.String(length=255), nullable=False),
        sa.Column('content', sa.Text(), nullable=True),
        sa.Column('metadata_info', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_knowledge_category', 'knowledge', ['category'])

    # Add columns to tasks table
    op.add_column('tasks', sa.Column('in_review_at', sa.DateTime(), nullable=True))
    op.add_column('tasks', sa.Column('done_at', sa.DateTime(), nullable=True))
    op.add_column('tasks', sa.Column('body', sa.Text(), nullable=True))
    op.add_column('tasks', sa.Column('file_path', sa.String(length=255), nullable=True))
    op.add_column('tasks', sa.Column('depends_on', sa.JSON(), nullable=True))

    # Add columns to sessions table
    op.add_column('sessions', sa.Column('mode', sa.String(length=20), nullable=True))
    op.add_column('sessions', sa.Column('state', sa.JSON(), nullable=True))


def downgrade():
    op.drop_column('sessions', 'state')
    op.drop_column('sessions', 'mode')
    op.drop_column('tasks', 'depends_on')
    op.drop_column('tasks', 'file_path')
    op.drop_column('tasks', 'body')
    op.drop_column('tasks', 'done_at')
    op.drop_column('tasks', 'in_review_at')
    op.drop_index('idx_knowledge_category', table_name='knowledge')
    op.drop_table('knowledge')
    op.drop_table('agents')
    op.drop_table('projects')
