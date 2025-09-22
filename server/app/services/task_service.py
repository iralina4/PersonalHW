import json
import pandas as pd
import hashlib
import re
from typing import List, Dict, Any
from sqlalchemy.orm import Session

from ..models import Task, TaskSkeleton, ImportSession
from ..schemas import TaskCreate
from .rag_service import RAGService

class TaskService:
    def __init__(self, db: Session):
        self.db = db
        self.rag_service = RAGService()
    
    def normalize_text(self, text: str) -> str:
        text = re.sub(r'\s+', ' ', text.strip())
        text = re.sub(r'[^\w\s\+\-\*\/\=\(\)\[\]\{\}\^\.\,\;\:\!\?]', '', text)
        return text.lower()
    
    def extract_skeleton(self, text: str) -> str:
        skeleton = re.sub(r'\d+(?:\.\d+)?', 'N', text)
        skeleton = re.sub(r'[а-яё]+(?:\s+[а-яё]+)*(?=\s+[A-Z])', 'NAME', skeleton, flags=re.IGNORECASE)
        skeleton = re.sub(r'\b[A-Z]\b', 'VAR', skeleton)
        return self.normalize_text(skeleton)
    
    def compute_skeleton_hash(self, skeleton: str) -> str:
        return hashlib.md5(skeleton.encode('utf-8')).hexdigest()
    
    def create_task(self, task_data: TaskCreate) -> Task:
        normalized_text = self.normalize_text(task_data.statement_text)
        skeleton = self.extract_skeleton(normalized_text)
        skeleton_hash = self.compute_skeleton_hash(skeleton)
        
        db_skeleton = self.db.query(TaskSkeleton).filter(
            TaskSkeleton.skeleton_hash == skeleton_hash
        ).first()
        
        if not db_skeleton:
            db_skeleton = TaskSkeleton(
                skeleton_text=skeleton,
                skeleton_hash=skeleton_hash
            )
            self.db.add(db_skeleton)
            self.db.commit()
            self.db.refresh(db_skeleton)
        
        db_task = Task(
            **task_data.dict(),
            skeleton_id=db_skeleton.id
        )
        self.db.add(db_task)
        self.db.commit()
        self.db.refresh(db_task)
        
        if self.rag_service.available:
            task_dict = {
                "id": db_task.id,
                "topic": db_task.topic,
                "subtopic": db_task.subtopic or "",
                "difficulty": db_task.difficulty,
                "statement_text": db_task.statement_text,
                "skills": db_task.skills or [],
                "tags": db_task.tags or []
            }
            self.rag_service.index_task(task_dict)
        
        return db_task
    
    def import_tasks_from_data(self, session_id: int, tasks_data: List[TaskCreate]):
        session = self.db.query(ImportSession).filter(ImportSession.id == session_id).first()
        if not session:
            return
        
        session.status = "processing"
        session.total_tasks = len(tasks_data)
        self.db.commit()
        
        imported = 0
        errors = []
        
        for task_data in tasks_data:
            try:
                self.create_task(task_data)
                imported += 1
            except Exception as e:
                errors.append(str(e))
        
        session.imported_tasks = imported
        session.errors = errors
        session.status = "completed"
        self.db.commit()
    
    def import_tasks_from_file(self, session_id: int, file_path: str):
        session = self.db.query(ImportSession).filter(ImportSession.id == session_id).first()
        if not session:
            return
        
        session.status = "processing"
        self.db.commit()
        
        tasks_data = []
        errors = []
        
        try:
            if file_path.endswith('.jsonl'):
                with open(file_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        if line.strip():
                            task_dict = json.loads(line)
                            tasks_data.append(TaskCreate(**task_dict))
            
            elif file_path.endswith('.csv'):
                df = pd.read_csv(file_path)
                for _, row in df.iterrows():
                    task_dict = row.to_dict()
                    if 'skills' in task_dict and isinstance(task_dict['skills'], str):
                        task_dict['skills'] = json.loads(task_dict['skills'])
                    if 'tags' in task_dict and isinstance(task_dict['tags'], str):
                        task_dict['tags'] = json.loads(task_dict['tags'])
                    tasks_data.append(TaskCreate(**task_dict))
            
            session.total_tasks = len(tasks_data)
            self.db.commit()
            
            imported = 0
            for task_data in tasks_data:
                try:
                    self.create_task(task_data)
                    imported += 1
                except Exception as e:
                    errors.append(str(e))
            
            session.imported_tasks = imported
            session.errors = errors
            session.status = "completed"
            
        except Exception as e:
            session.status = "failed"
            session.errors = [str(e)]
        
        self.db.commit()
    
    def import_all_tasks_from_directory(self, session_id: int, directory_path: str):
        import os
        
        session = self.db.query(ImportSession).filter(ImportSession.id == session_id).first()
        if not session:
            return
        
        session.status = "processing"
        self.db.commit()
        
        total_imported = 0
        all_errors = []
        
        for filename in os.listdir(directory_path):
            if filename.endswith(('.jsonl', '.csv')):
                file_path = os.path.join(directory_path, filename)
                
                file_session = ImportSession(
                    filename=filename,
                    status="pending"
                )
                self.db.add(file_session)
                self.db.commit()
                self.db.refresh(file_session)
                
                self.import_tasks_from_file(file_session.id, file_path)
                
                self.db.refresh(file_session)
                total_imported += file_session.imported_tasks or 0
                if file_session.errors:
                    all_errors.extend(file_session.errors)
        
        session.imported_tasks = total_imported
        session.errors = all_errors
        session.status = "completed"
        self.db.commit()
