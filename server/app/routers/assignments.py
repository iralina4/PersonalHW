from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List
import os

from ..database import get_db
from ..models import Assignment, Student, AssignmentItem
from ..schemas import Assignment as AssignmentSchema, AssignmentCreate, AssignmentResponse
from ..services.assignment_service import AssignmentService

router = APIRouter(prefix="/api/assignments", tags=["assignments"])

@router.post("/generate", response_model=AssignmentResponse)
async def generate_assignment(
    assignment_data: AssignmentCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    student = db.query(Student).filter(Student.id == assignment_data.student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    db_assignment = Assignment(
        student_id=assignment_data.student_id,
        topics_text=assignment_data.topics_text,
        options=assignment_data.options.dict(),
        status="pending"
    )
    db.add(db_assignment)
    db.commit()
    db.refresh(db_assignment)
    
    assignment_service = AssignmentService(db)
    try:
        assignment_service.generate_assignment_async(db_assignment.id)
    except Exception as e:
        db_assignment.status = "failed"
        db.commit()
        raise HTTPException(status_code=500, detail=f"Assignment generation failed: {str(e)}")
    
    return AssignmentResponse(
        assignment_id=db_assignment.id,
        download_urls={
            "student": f"/api/assignments/{db_assignment.id}/download/student",
            "teacher": f"/api/assignments/{db_assignment.id}/download/teacher"
        },
        message="Задание успешно создано"
    )

@router.get("/{assignment_id}", response_model=AssignmentSchema)
async def get_assignment(assignment_id: int, db: Session = Depends(get_db)):
    assignment = db.query(Assignment).filter(Assignment.id == assignment_id).first()
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    return assignment

@router.get("/", response_model=List[AssignmentSchema])
async def list_assignments(
    student_id: int = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    query = db.query(Assignment)
    if student_id:
        query = query.filter(Assignment.student_id == student_id)
    assignments = query.offset(skip).limit(limit).all()
    return assignments

@router.get("/{assignment_id}/download/{pdf_type}")
async def download_pdf(assignment_id: int, pdf_type: str, db: Session = Depends(get_db)):
    if pdf_type not in ["student", "teacher"]:
        raise HTTPException(status_code=400, detail="Invalid PDF type")
    
    assignment = db.query(Assignment).filter(Assignment.id == assignment_id).first()
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    
    if assignment.status != "completed":
        raise HTTPException(status_code=400, detail="Assignment not ready")
    
    pdf_path = assignment.student_pdf_path if pdf_type == "student" else assignment.teacher_pdf_path
    if not pdf_path or not os.path.exists(pdf_path):
        raise HTTPException(status_code=404, detail="PDF file not found")
    
    filename = f"assignment_{assignment_id}_{pdf_type}.pdf"
    return FileResponse(pdf_path, filename=filename, media_type="application/pdf")
