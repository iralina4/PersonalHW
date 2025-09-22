from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
import json
import os

from ..database import get_db
from ..models import Task, ImportSession
from ..schemas import Task as TaskSchema, TaskCreate, ImportTasksRequest, ImportTasksResponse, SearchRequest, SearchResponse
from ..services.task_service import TaskService
from ..services.rag_service import RAGService

router = APIRouter(prefix="/api/tasks", tags=["tasks"])

@router.post("/import", response_model=ImportTasksResponse)
async def import_tasks(
    import_data: ImportTasksRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    session = ImportSession(
        filename=import_data.filename or "api_import",
        status="pending"
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    
    task_service = TaskService(db)
    
    if import_data.tasks:
        background_tasks.add_task(
            task_service.import_tasks_from_data,
            session.id,
            import_data.tasks
        )
        total_tasks = len(import_data.tasks)
    elif import_data.filename:
        file_path = f"/app/data/tasks/{import_data.filename}"
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="File not found")
        
        background_tasks.add_task(
            task_service.import_tasks_from_file,
            session.id,
            file_path
        )
        total_tasks = 0
    else:
        data_dir = "/app/data/tasks"
        if os.path.exists(data_dir):
            background_tasks.add_task(
                task_service.import_all_tasks_from_directory,
                session.id,
                data_dir
            )
            total_tasks = 0
        else:
            raise HTTPException(status_code=404, detail="No data directory found")
    
    session.total_tasks = total_tasks
    db.commit()
    
    return ImportTasksResponse(
        session_id=session.id,
        message="Import started",
        total_tasks=total_tasks
    )

@router.get("/", response_model=List[TaskSchema])
async def list_tasks(
    topic: str = None,
    difficulty: int = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    query = db.query(Task)
    if topic:
        query = query.filter(Task.topic == topic)
    if difficulty:
        query = query.filter(Task.difficulty == difficulty)
    
    tasks = query.offset(skip).limit(limit).all()
    return tasks

@router.get("/{task_id}", response_model=TaskSchema)
async def get_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@router.post("/", response_model=TaskSchema)
async def create_task(task_data: TaskCreate, db: Session = Depends(get_db)):
    task_service = TaskService(db)
    task = task_service.create_task(task_data)
    return task

@router.get("/search", response_model=SearchResponse)
async def search_tasks(q: str, topic: str = None, difficulty_min: int = 1, difficulty_max: int = 5):
    rag_service = RAGService()
    
    if not rag_service.available:
        return SearchResponse(
            query=q,
            results=[],
            total=0,
            mode="unavailable"
        )
    
    difficulty_range = (difficulty_min, difficulty_max) if difficulty_min != difficulty_max else None
    results = rag_service.hybrid_search(q, topic=topic, difficulty_range=difficulty_range)
    
    search_results = []
    for result in results:
        search_results.append({
            "task_id": result["task_id"],
            "vector_score": result["vector_score"],
            "bm25_score": result["bm25_score"],
            "combined_score": result["combined_score"],
            "topic": topic or "Unknown",
            "statement": f"Task {result['task_id']}"
        })
    
    return SearchResponse(
        query=q,
        results=search_results,
        total=len(search_results),
        mode="real"
    )
