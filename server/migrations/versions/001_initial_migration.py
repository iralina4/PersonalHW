"""Initial migration

Revision ID: 001
Revises: 
Create Date: 2024-01-01 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table('students',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.Column('email', sa.String(length=255), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_students_email'), 'students', ['email'], unique=True)
    op.create_index(op.f('ix_students_id'), 'students', ['id'], unique=False)
    
    op.create_table('task_skeletons',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('skeleton_text', sa.Text(), nullable=False),
    sa.Column('skeleton_hash', sa.String(length=32), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_task_skeletons_skeleton_hash'), 'task_skeletons', ['skeleton_hash'], unique=True)
    
    op.create_table('import_sessions',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('filename', sa.String(length=500), nullable=False),
    sa.Column('status', sa.String(length=50), nullable=True),
    sa.Column('total_tasks', sa.Integer(), nullable=True),
    sa.Column('imported_tasks', sa.Integer(), nullable=True),
    sa.Column('errors', sa.JSON(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('completed_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    
    op.create_table('assignments',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('student_id', sa.Integer(), nullable=True),
    sa.Column('topics_text', sa.Text(), nullable=False),
    sa.Column('status', sa.String(length=50), nullable=True),
    sa.Column('options', sa.JSON(), nullable=True),
    sa.Column('student_pdf_path', sa.String(length=500), nullable=True),
    sa.Column('teacher_pdf_path', sa.String(length=500), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('completed_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['student_id'], ['students.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    
    op.create_table('student_profiles',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('student_id', sa.Integer(), nullable=True),
    sa.Column('grade', sa.Integer(), nullable=True),
    sa.Column('ege_date', sa.DateTime(), nullable=True),
    sa.Column('target_score', sa.Integer(), nullable=True),
    sa.Column('pace', sa.String(length=50), nullable=True),
    sa.Column('weak_topics', sa.JSON(), nullable=True),
    sa.Column('strong_topics', sa.JSON(), nullable=True),
    sa.Column('preferred_task_types', sa.JSON(), nullable=True),
    sa.Column('past_mistakes', sa.JSON(), nullable=True),
    sa.Column('profile_data', sa.JSON(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['student_id'], ['students.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('student_id')
    )
    
    op.create_table('tasks',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('source', sa.String(length=255), nullable=True),
    sa.Column('topic', sa.String(length=255), nullable=False),
    sa.Column('subtopic', sa.String(length=255), nullable=True),
    sa.Column('difficulty', sa.Integer(), nullable=False),
    sa.Column('skills', sa.JSON(), nullable=True),
    sa.Column('statement_text', sa.Text(), nullable=False),
    sa.Column('statement_tex', sa.Text(), nullable=True),
    sa.Column('answer', sa.Text(), nullable=True),
    sa.Column('solution_text', sa.Text(), nullable=True),
    sa.Column('solution_tex', sa.Text(), nullable=True),
    sa.Column('tags', sa.JSON(), nullable=True),
    sa.Column('time_estimate_sec', sa.Integer(), nullable=True),
    sa.Column('format', sa.String(length=50), nullable=True),
    sa.Column('skeleton_id', sa.Integer(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['skeleton_id'], ['task_skeletons.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_tasks_difficulty'), 'tasks', ['difficulty'], unique=False)
    op.create_index(op.f('ix_tasks_subtopic'), 'tasks', ['subtopic'], unique=False)
    op.create_index(op.f('ix_tasks_topic'), 'tasks', ['topic'], unique=False)
    
    op.create_table('logs',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('level', sa.String(length=20), nullable=False),
    sa.Column('message', sa.Text(), nullable=False),
    sa.Column('context', sa.JSON(), nullable=True),
    sa.Column('assignment_id', sa.Integer(), nullable=True),
    sa.Column('student_id', sa.Integer(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['assignment_id'], ['assignments.id'], ),
    sa.ForeignKeyConstraint(['student_id'], ['students.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_logs_created_at'), 'logs', ['created_at'], unique=False)
    op.create_index(op.f('ix_logs_level'), 'logs', ['level'], unique=False)
    
    op.create_table('assignment_items',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('assignment_id', sa.Integer(), nullable=True),
    sa.Column('task_id', sa.Integer(), nullable=True),
    sa.Column('order_index', sa.Integer(), nullable=False),
    sa.Column('selection_reason', sa.Text(), nullable=True),
    sa.Column('vector_score', sa.Float(), nullable=True),
    sa.Column('bm25_score', sa.Float(), nullable=True),
    sa.Column('combined_score', sa.Float(), nullable=True),
    sa.ForeignKeyConstraint(['assignment_id'], ['assignments.id'], ),
    sa.ForeignKeyConstraint(['task_id'], ['tasks.id'], ),
    sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    op.drop_table('assignment_items')
    op.drop_index(op.f('ix_logs_level'), table_name='logs')
    op.drop_index(op.f('ix_logs_created_at'), table_name='logs')
    op.drop_table('logs')
    op.drop_index(op.f('ix_tasks_topic'), table_name='tasks')
    op.drop_index(op.f('ix_tasks_subtopic'), table_name='tasks')
    op.drop_index(op.f('ix_tasks_difficulty'), table_name='tasks')
    op.drop_table('tasks')
    op.drop_table('student_profiles')
    op.drop_table('assignments')
    op.drop_table('import_sessions')
    op.drop_index(op.f('ix_task_skeletons_skeleton_hash'), table_name='task_skeletons')
    op.drop_table('task_skeletons')
    op.drop_index(op.f('ix_students_id'), table_name='students')
    op.drop_index(op.f('ix_students_email'), table_name='students')
    op.drop_table('students')
