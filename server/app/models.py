from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, Float, ForeignKey, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class Student(Base):
    __tablename__ = "students"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    profile = relationship("StudentProfile", back_populates="student", uselist=False)
    assignments = relationship("Assignment", back_populates="student")

class StudentProfile(Base):
    __tablename__ = "student_profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), unique=True)
    grade = Column(Integer, default=11)
    ege_date = Column(DateTime)
    target_score = Column(Integer, default=80)
    pace = Column(String(50), default="medium")
    weak_topics = Column(JSON, default=list)
    strong_topics = Column(JSON, default=list)
    preferred_task_types = Column(JSON, default=list)
    past_mistakes = Column(JSON, default=list)
    profile_data = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    student = relationship("Student", back_populates="profile")

class Assignment(Base):
    __tablename__ = "assignments"
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"))
    topics_text = Column(Text, nullable=False)
    status = Column(String(50), default="pending")
    options = Column(JSON, default=dict)
    student_pdf_path = Column(String(500))
    teacher_pdf_path = Column(String(500))
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    
    student = relationship("Student", back_populates="assignments")
    items = relationship("AssignmentItem", back_populates="assignment")

class AssignmentItem(Base):
    __tablename__ = "assignment_items"
    
    id = Column(Integer, primary_key=True, index=True)
    assignment_id = Column(Integer, ForeignKey("assignments.id"))
    task_id = Column(Integer, ForeignKey("tasks.id"))
    order_index = Column(Integer, nullable=False)
    selection_reason = Column(Text)
    vector_score = Column(Float)
    bm25_score = Column(Float)
    combined_score = Column(Float)
    
    assignment = relationship("Assignment", back_populates="items")
    task = relationship("Task", back_populates="assignment_items")

class Task(Base):
    __tablename__ = "tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    source = Column(String(255))
    topic = Column(String(255), nullable=False, index=True)
    subtopic = Column(String(255), index=True)
    difficulty = Column(Integer, nullable=False, index=True)
    skills = Column(JSON, default=list)
    statement_text = Column(Text, nullable=False)
    statement_tex = Column(Text)
    answer = Column(Text)
    solution_text = Column(Text)
    solution_tex = Column(Text)
    tags = Column(JSON, default=list)
    time_estimate_sec = Column(Integer)
    format = Column(String(50), default="standard")
    skeleton_id = Column(Integer, ForeignKey("task_skeletons.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    skeleton = relationship("TaskSkeleton", back_populates="tasks")
    assignment_items = relationship("AssignmentItem", back_populates="task")

class TaskSkeleton(Base):
    __tablename__ = "task_skeletons"
    
    id = Column(Integer, primary_key=True, index=True)
    skeleton_text = Column(Text, nullable=False, unique=True)
    skeleton_hash = Column(String(32), nullable=False, unique=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    tasks = relationship("Task", back_populates="skeleton")

class ImportSession(Base):
    __tablename__ = "import_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(500), nullable=False)
    status = Column(String(50), default="pending")
    total_tasks = Column(Integer, default=0)
    imported_tasks = Column(Integer, default=0)
    errors = Column(JSON, default=list)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)

class LogEntry(Base):
    __tablename__ = "logs"
    
    id = Column(Integer, primary_key=True, index=True)
    level = Column(String(20), nullable=False, index=True)
    message = Column(Text, nullable=False)
    context = Column(JSON, default=dict)
    assignment_id = Column(Integer, ForeignKey("assignments.id"))
    student_id = Column(Integer, ForeignKey("students.id"))
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
