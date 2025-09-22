from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from ..database import get_db
from ..models import Student, StudentProfile
from ..schemas import Student as StudentSchema, StudentCreate, StudentProfile as StudentProfileSchema, StudentProfileCreate, StudentProfileUpdate

router = APIRouter(prefix="/api/students", tags=["students"])

@router.post("/", response_model=StudentSchema)
async def create_student(student_data: StudentCreate, db: Session = Depends(get_db)):
    db_student = Student(name=student_data.name, email=student_data.email)
    db.add(db_student)
    db.commit()
    db.refresh(db_student)
    return db_student

@router.get("/{student_id}", response_model=StudentSchema)
async def get_student(student_id: int, db: Session = Depends(get_db)):
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return student

@router.get("/", response_model=List[StudentSchema])
async def list_students(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    students = db.query(Student).offset(skip).limit(limit).all()
    return students

@router.post("/{student_id}/profile", response_model=StudentProfileSchema)
async def create_student_profile(student_id: int, profile_data: StudentProfileCreate, db: Session = Depends(get_db)):
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    existing_profile = db.query(StudentProfile).filter(StudentProfile.student_id == student_id).first()
    if existing_profile:
        raise HTTPException(status_code=400, detail="Profile already exists")
    
    db_profile = StudentProfile(student_id=student_id, **profile_data.dict())
    db.add(db_profile)
    db.commit()
    db.refresh(db_profile)
    return db_profile

@router.put("/{student_id}/profile", response_model=StudentProfileSchema)
async def update_student_profile(student_id: int, profile_data: StudentProfileUpdate, db: Session = Depends(get_db)):
    profile = db.query(StudentProfile).filter(StudentProfile.student_id == student_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    update_data = profile_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(profile, field, value)
    
    db.commit()
    db.refresh(profile)
    return profile

@router.get("/{student_id}/profile", response_model=StudentProfileSchema)
async def get_student_profile(student_id: int, db: Session = Depends(get_db)):
    profile = db.query(StudentProfile).filter(StudentProfile.student_id == student_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile
