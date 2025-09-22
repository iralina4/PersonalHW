from celery import Celery
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
import os

from .celery_app import celery_app
from .services.assignment_service import AssignmentService
from .services.task_service import TaskService
from .schemas import TaskCreate

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/ege_tutor")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@celery_app.task(bind=True, max_retries=3)
def generate_assignment_task(self, assignment_id: int):
    db = SessionLocal()
    try:
        assignment_service = AssignmentService(db)
        assignment_service.generate_assignment_async(assignment_id)
    except Exception as e:
        db.rollback()
        raise self.retry(exc=e, countdown=60 * (2 ** self.request.retries))
    finally:
        db.close()

@celery_app.task(bind=True, max_retries=3)
def import_tasks_task(self, session_id: int, file_path: str = None, tasks_data: list = None):
    db = SessionLocal()
    try:
        task_service = TaskService(db)
        
        if tasks_data:
            task_objects = [TaskCreate(**task_dict) for task_dict in tasks_data]
            task_service.import_tasks_from_data(session_id, task_objects)
        elif file_path:
            task_service.import_tasks_from_file(session_id, file_path)
        else:
            data_dir = "/app/data/tasks"
            task_service.import_all_tasks_from_directory(session_id, data_dir)
            
    except Exception as e:
        db.rollback()
        raise self.retry(exc=e, countdown=60 * (2 ** self.request.retries))
    finally:
        db.close()

@celery_app.task
def index_task_in_rag(task_data: dict):
    from .services.rag_service import RAGService
    
    rag_service = RAGService()
    if rag_service.available:
        return rag_service.index_task(task_data)
    return False
