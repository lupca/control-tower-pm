"""Schema alignment with v2 design - CRITICAL fixes

Revision ID: 003_schema_alignment
Revises: 002_schema_v2
Create Date: 2026-07-26
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '003_schema_alignment'
down_revision = '002_schema_v2'
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    insp = sa.inspect(bind)

    proj_cols = [c['name'] for c in insp.get_columns('projects')]
    agent_cols = [c['name'] for c in insp.get_columns('agents')]
    task_cols = [c['name'] for c in insp.get_columns('tasks')]

    # === CRITICAL: Projects ===
    if 'repo_root' not in proj_cols:
        op.add_column('projects', sa.Column('repo_root', sa.String(255)))
    if 'task_prefix' not in proj_cols:
        op.add_column('projects', sa.Column('task_prefix', sa.String(10)))

    # === CRITICAL: Agents ===
    if 'type' not in agent_cols:
        op.add_column('agents', sa.Column('type', sa.String(10), nullable=False, server_default='ai'))
    if 'model' not in agent_cols:
        op.add_column('agents', sa.Column('model', sa.String(100)))
    if 'effort' not in agent_cols:
        op.add_column('agents', sa.Column('effort', sa.String(10), server_default='medium'))
    if 'cli' not in agent_cols:
        op.add_column('agents', sa.Column('cli', sa.String(20)))
    if 'total_tasks_executed' not in agent_cols:
        op.add_column('agents', sa.Column('total_tasks_executed', sa.Integer(), server_default='0'))
    if 'total_tasks_reviewed' not in agent_cols:
        op.add_column('agents', sa.Column('total_tasks_reviewed', sa.Integer(), server_default='0'))
    if 'success_rate' not in agent_cols:
        op.add_column('agents', sa.Column('success_rate', sa.Numeric(3, 2), server_default='1.0'))

    # === CRITICAL: Tasks FK ===
    # First ensure all project values exist in projects table
    op.execute("""
        INSERT INTO projects (id, name)
        SELECT DISTINCT project, project 
        FROM tasks 
        WHERE project NOT IN (SELECT id FROM projects)
        ON CONFLICT DO NOTHING
    """)

    fk_names = [fk['name'] for fk in insp.get_foreign_keys('tasks')]
    if 'fk_tasks_project' not in fk_names:
        op.create_foreign_key(
            'fk_tasks_project', 'tasks', 'projects',
            ['project'], ['id']
        )

    if 'in_review_at' not in task_cols:
        op.add_column('tasks', sa.Column('in_review_at', sa.DateTime(timezone=True)))

    # === MODERATE: Agent stats ===
    if 'avg_review_rounds' not in agent_cols:
        op.add_column('agents', sa.Column('avg_review_rounds', sa.Numeric(3, 1), server_default='1.0'))
    if 'strengths' not in agent_cols:
        op.add_column('agents', sa.Column('strengths', postgresql.JSONB, server_default='[]'))
    if 'weaknesses' not in agent_cols:
        op.add_column('agents', sa.Column('weaknesses', postgresql.JSONB, server_default='[]'))
    if 'recent_trend' not in agent_cols:
        op.add_column('agents', sa.Column('recent_trend', sa.String(20)))
    if 'last_active' not in agent_cols:
        op.add_column('agents', sa.Column('last_active', sa.Date()))

    # === MODERATE: Projects graph ===
    if 'graph_status' not in proj_cols:
        op.add_column('projects', sa.Column('graph_status', sa.String(20), server_default='pending'))
    if 'embed_status' not in proj_cols:
        op.add_column('projects', sa.Column('embed_status', sa.String(20), server_default='pending'))
    if 'node_count' not in proj_cols:
        op.add_column('projects', sa.Column('node_count', sa.Integer(), server_default='0'))
    if 'edge_count' not in proj_cols:
        op.add_column('projects', sa.Column('edge_count', sa.Integer(), server_default='0'))


def downgrade():
    bind = op.get_bind()
    insp = sa.inspect(bind)

    proj_cols = [c['name'] for c in insp.get_columns('projects')]
    agent_cols = [c['name'] for c in insp.get_columns('agents')]
    task_cols = [c['name'] for c in insp.get_columns('tasks')]
    fk_names = [fk['name'] for fk in insp.get_foreign_keys('tasks')]

    if 'edge_count' in proj_cols:
        op.drop_column('projects', 'edge_count')
    if 'node_count' in proj_cols:
        op.drop_column('projects', 'node_count')
    if 'embed_status' in proj_cols:
        op.drop_column('projects', 'embed_status')
    if 'graph_status' in proj_cols:
        op.drop_column('projects', 'graph_status')

    if 'last_active' in agent_cols:
        op.drop_column('agents', 'last_active')
    if 'recent_trend' in agent_cols:
        op.drop_column('agents', 'recent_trend')
    if 'weaknesses' in agent_cols:
        op.drop_column('agents', 'weaknesses')
    if 'strengths' in agent_cols:
        op.drop_column('agents', 'strengths')
    if 'avg_review_rounds' in agent_cols:
        op.drop_column('agents', 'avg_review_rounds')

    if 'in_review_at' in task_cols:
        op.drop_column('tasks', 'in_review_at')
    if 'fk_tasks_project' in fk_names:
        op.drop_constraint('fk_tasks_project', 'tasks', type_='foreignkey')

    if 'success_rate' in agent_cols:
        op.drop_column('agents', 'success_rate')
    if 'total_tasks_reviewed' in agent_cols:
        op.drop_column('agents', 'total_tasks_reviewed')
    if 'total_tasks_executed' in agent_cols:
        op.drop_column('agents', 'total_tasks_executed')
    if 'cli' in agent_cols:
        op.drop_column('agents', 'cli')
    if 'effort' in agent_cols:
        op.drop_column('agents', 'effort')
    if 'model' in agent_cols:
        op.drop_column('agents', 'model')
    if 'type' in agent_cols:
        op.drop_column('agents', 'type')

    if 'task_prefix' in proj_cols:
        op.drop_column('projects', 'task_prefix')
    if 'repo_root' in proj_cols:
        op.drop_column('projects', 'repo_root')
