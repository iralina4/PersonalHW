from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime

class StudentCreate(BaseModel):
    name: str
    email: str

class StudentProfileCreate(BaseModel):
    grade: int = 11
    ege_date: Optional[datetime] = None
    target_score: int = 80
    pace: str = "medium"
    weak_topics: List[str] = []
    strong_topics: List[str] = []
    preferred_task_types: List[str] = []
    past_mistakes: List[str] = []
    profile_data: Dict[str, Any] = {}

class StudentProfileUpdate(BaseModel):
    grade: Optional[int] = None
    ege_date: Optional[datetime] = None
    target_score: Optional[int] = None
    pace: Optional[str] = None
    weak_topics: Optional[List[str]] = None
    strong_topics: Optional[List[str]] = None
    preferred_task_types: Optional[List[str]] = None
    past_mistakes: Optional[List[str]] = None
    profile_data: Optional[Dict[str, Any]] = None

class StudentProfile(BaseModel):
    id: int
    student_id: int
    grade: int
    ege_date: Optional[datetime]
    target_score: int
    pace: str
    weak_topics: List[str]
    strong_topics: List[str]
    preferred_task_types: List[str]
    past_mistakes: List[str]
    profile_data: Dict[str, Any]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class Student(BaseModel):
    id: int
    name: str
    email: str
    created_at: datetime
    updated_at: datetime
    profile: Optional[StudentProfile] = None

    class Config:
        from_attributes = True

class TaskCreate(BaseModel):
    source: Optional[str] = None
    topic: str
    subtopic: Optional[str] = None
    difficulty: int
    skills: List[str] = []
    statement_text: str
    statement_tex: Optional[str] = None
    answer: Optional[str] = None
    solution_text: Optional[str] = None
    solution_tex: Optional[str] = None
    tags: List[str] = []
    time_estimate_sec: Optional[int] = None
    format: str = "standard"

class Task(BaseModel):
    id: int
    source: Optional[str]
    topic: str
    subtopic: Optional[str]
    difficulty: int
    skills: List[str]
    statement_text: str
    statement_tex: Optional[str]
    answer: Optional[str]
    solution_text: Optional[str]
    solution_tex: Optional[str]
    tags: List[str]
    time_estimate_sec: Optional[int]
    format: str
    skeleton_id: Optional[int]
    created_at: datetime

    class Config:
        from_attributes = True

class AssignmentOptions(BaseModel):
    count_total: Optional[int] = None
    include_part2: bool = False
    max_time_min: Optional[int] = None
    make_two_pdfs: bool = True

class AssignmentCreate(BaseModel):
    student_id: int
    topics_text: str
    options: AssignmentOptions = AssignmentOptions()

class AssignmentItemCreate(BaseModel):
    task_id: int
    order_index: int
    selection_reason: Optional[str] = None
    vector_score: Optional[float] = None
    bm25_score: Optional[float] = None
    combined_score: Optional[float] = None

class AssignmentItem(BaseModel):
    id: int
    assignment_id: int
    task_id: int
    order_index: int
    selection_reason: Optional[str]
    vector_score: Optional[float]
    bm25_score: Optional[float]
    combined_score: Optional[float]
    task: Optional[Task] = None

    class Config:
        from_attributes = True

class Assignment(BaseModel):
    id: int
    student_id: int
    topics_text: str
    status: str
    options: Dict[str, Any]
    student_pdf_path: Optional[str]
    teacher_pdf_path: Optional[str]
    created_at: datetime
    completed_at: Optional[datetime]
    items: List[AssignmentItem] = []

    class Config:
        from_attributes = True

class AssignmentResponse(BaseModel):
    assignment_id: int
    download_urls: Dict[str, str]
    message: str

class ImportTasksRequest(BaseModel):
    filename: Optional[str] = None
    tasks: Optional[List[TaskCreate]] = None

class ImportTasksResponse(BaseModel):
    session_id: int
    message: str
    total_tasks: int

class SearchRequest(BaseModel):
    query: str
    topic: Optional[str] = None
    difficulty_min: int = 1
    difficulty_max: int = 5
    limit: int = 20

class SearchResult(BaseModel):
    task_id: int
    vector_score: float
    bm25_score: float
    combined_score: float
    topic: str
    statement: str

class SearchResponse(BaseModel):
    query: str
    results: List[SearchResult]
    total: int
    mode: str
