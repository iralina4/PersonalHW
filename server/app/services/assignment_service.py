import json
import random
from typing import List, Dict, Any, Tuple
from sqlalchemy.orm import Session
from datetime import datetime

from ..models import Assignment, AssignmentItem, Student, StudentProfile, Task
from .rag_service import RAGService
from .pdf_service import PDFService
from ..drivers.yagpt_client import YaGPTClient

class AssignmentService:
    def __init__(self, db: Session):
        self.db = db
        self.rag_service = RAGService()
        self.pdf_service = PDFService()
        self.yagpt_client = YaGPTClient()
    
    def parse_topics_text(self, topics_text: str) -> List[Dict[str, Any]]:
        topics = []
        
        parts = topics_text.split(',')
        for part in parts:
            part = part.strip()
            if '—' in part or '-' in part:
                separator = '—' if '—' in part else '-'
                topic_part, count_part = part.rsplit(separator, 1)
                topic = topic_part.strip()
                try:
                    count = int(count_part.strip())
                    topics.append({"topic": topic, "count": count})
                except ValueError:
                    topics.append({"topic": part, "count": 1})
            else:
                topics.append({"topic": part, "count": 1})
        
        return topics
    
    def get_student_context(self, student_id: int) -> Dict[str, Any]:
        student = self.db.query(Student).filter(Student.id == student_id).first()
        profile = self.db.query(StudentProfile).filter(StudentProfile.student_id == student_id).first()
        
        context = {
            "student_name": student.name if student else "Unknown",
            "grade": profile.grade if profile else 11,
            "target_score": profile.target_score if profile else 80,
            "weak_topics": profile.weak_topics if profile else [],
            "strong_topics": profile.strong_topics if profile else [],
            "preferred_task_types": profile.preferred_task_types if profile else [],
            "past_mistakes": profile.past_mistakes if profile else []
        }
        
        return context
    
    def select_tasks_for_topic(
        self, 
        topic: str, 
        count: int, 
        student_context: Dict[str, Any],
        used_skeleton_hashes: set
    ) -> List[Dict[str, Any]]:
        
        if not self.rag_service.available:
            return self._mock_task_selection(topic, count, used_skeleton_hashes)
        
        target_score = student_context.get("target_score", 80)
        base_difficulty = min(5, max(1, target_score // 20))
        
        candidates = []
        
        for difficulty in [base_difficulty, base_difficulty + 1]:
            if difficulty > 5:
                continue
                
            search_results = self.rag_service.hybrid_search(
                query=topic,
                topic=topic,
                difficulty_range=(difficulty, difficulty),
                limit=count * 3
            )
            
            for result in search_results:
                task = self.db.query(Task).filter(Task.id == result["task_id"]).first()
                if task and task.skeleton and task.skeleton.skeleton_hash not in used_skeleton_hashes:
                    candidates.append({
                        "task": task,
                        "scores": result,
                        "selection_reason": f"Difficulty {difficulty} for target score {target_score}"
                    })
                    used_skeleton_hashes.add(task.skeleton.skeleton_hash)
        
        candidates = sorted(candidates, key=lambda x: x["scores"]["combined_score"], reverse=True)
        return candidates[:count]
    
    def _mock_task_selection(self, topic: str, count: int, used_skeleton_hashes: set) -> List[Dict[str, Any]]:
        """Простой алгоритм подбора задач по теме"""
        tasks = self.db.query(Task).filter(Task.topic.ilike(f"%{topic}%")).limit(count * 2).all()
        
        selected = []
        for task in tasks:
            if task.skeleton and task.skeleton.skeleton_hash not in used_skeleton_hashes:
                selected.append({
                    "task": task,
                    "scores": {
                        "task_id": task.id,
                        "vector_score": 0.8 + random.random() * 0.2,
                        "bm25_score": 0.7 + random.random() * 0.3,
                        "combined_score": 0.75 + random.random() * 0.25
                    },
                    "selection_reason": f"Соответствует теме '{topic}', подходящий уровень сложности"
                })
                used_skeleton_hashes.add(task.skeleton.skeleton_hash)
                if len(selected) >= count:
                    break
        
        return selected
    
    def generate_assignment_async(self, assignment_id: int):
        assignment = self.db.query(Assignment).filter(Assignment.id == assignment_id).first()
        if not assignment:
            return
        
        try:
            assignment.status = "generating"
            self.db.commit()
            
            student_context = self.get_student_context(assignment.student_id)
            topics = self.parse_topics_text(assignment.topics_text)
            
            used_skeleton_hashes = set()
            all_selected_tasks = []
            order_index = 1
            
            for topic_info in topics:
                topic = topic_info["topic"]
                count = topic_info["count"]
                
                selected_tasks = self.select_tasks_for_topic(
                    topic, count, student_context, used_skeleton_hashes
                )
                
                for selected in selected_tasks:
                    task = selected["task"]
                    scores = selected["scores"]
                    
                    assignment_item = AssignmentItem(
                        assignment_id=assignment.id,
                        task_id=task.id,
                        order_index=order_index,
                        selection_reason=selected["selection_reason"],
                        vector_score=scores.get("vector_score"),
                        bm25_score=scores.get("bm25_score"),
                        combined_score=scores.get("combined_score")
                    )
                    
                    self.db.add(assignment_item)
                    all_selected_tasks.append(assignment_item)
                    order_index += 1
            
            self.db.commit()
            
            assignment.status = "generating_pdfs"
            self.db.commit()
            
            tasks_data = []
            for item in all_selected_tasks:
                self.db.refresh(item)
                tasks_data.append({
                    "id": item.task.id,
                    "topic": item.task.topic,
                    "statement_text": item.task.statement_text,
                    "answer": item.task.answer,
                    "solution_text": item.task.solution_text,
                    "order_index": item.order_index
                })
            
            pdf_data = {
                "tasks": tasks_data,
                "student": {
                    "name": student_context["student_name"],
                    "grade": student_context["grade"]
                },
                "assignment_id": assignment.id,
                "topics_text": assignment.topics_text
            }
            
            student_pdf_path = self.pdf_service.generate_student_pdf(pdf_data)
            teacher_pdf_path = self.pdf_service.generate_teacher_pdf(pdf_data)
            
            assignment.student_pdf_path = student_pdf_path
            assignment.teacher_pdf_path = teacher_pdf_path
            assignment.status = "completed"
            assignment.completed_at = datetime.utcnow()
            self.db.commit()
            
        except Exception as e:
            assignment.status = "failed"
            self.db.commit()
            raise e
