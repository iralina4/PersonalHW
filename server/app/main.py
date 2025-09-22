from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .database import create_tables
from .routers import students, assignments, tasks

app = FastAPI(title="EGE Math Tutor API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(students.router)
app.include_router(assignments.router)
app.include_router(tasks.router)

@app.on_event("startup")
async def startup_event():
    create_tables()

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "EGE Math Tutor API", "version": "1.0.0"}

@app.get("/")
async def root():
    return {"message": "Система персонализированных заданий по математике для подготовки к ЕГЭ"}

@app.post("/api/students/")
async def create_student():
    return {"id": 1, "name": "Тестовый ученик", "message": "Студент создан (демо режим)"}

@app.get("/api/students/{student_id}")
async def get_student(student_id: int):
    return {
        "id": student_id,
        "name": f"Ученик {student_id}",
        "profile": {
            "grade": 11,
            "target_score": 80,
            "weak_topics": ["Логарифмы", "Тригонометрия"],
            "strong_topics": ["Алгебра"]
        }
    }

@app.post("/api/assignments/generate")
async def generate_assignment():
    return {
        "assignment_id": 1,
        "download_urls": {
            "student": "/api/assignments/1/download/student",
            "teacher": "/api/assignments/1/download/teacher"
        },
        "message": "Задание создано (демо режим)"
    }

@app.get("/api/assignments/{assignment_id}")
async def get_assignment(assignment_id: int):
    return {
        "id": assignment_id,
        "status": "completed",
        "topics_text": "Алгебра — 3, Геометрия — 2",
        "created_at": "2024-01-01T12:00:00",
        "items": [
            {
                "id": 1,
                "task": {
                    "id": 1,
                    "topic": "Алгебра",
                    "subtopic": "Уравнения",
                    "difficulty": 3,
                    "statement_text": "Решите уравнение x² - 5x + 6 = 0",
                    "answer": "x = 2; x = 3"
                },
                "order_index": 1,
                "selection_reason": "Соответствует слабым темам ученика"
            }
        ]
    }

@app.post("/api/tasks/import")
async def import_tasks():
    return {
        "session_id": 1,
        "message": "Импорт задач запущен (демо режим)",
        "total_tasks": 10
    }

@app.post("/api/rag/test")
async def test_rag():
    """Тестирование RAG системы"""
    try:
        from app.services.rag_service import RAGService
        rag = RAGService()
        
        if not rag.available:
            return {
                "status": "unavailable",
                "message": "RAG сервисы (Qdrant/Meilisearch) не запущены",
                "demo_results": {
                    "query": "квадратное уравнение",
                    "results": [
                        {
                            "task_id": 1,
                            "vector_score": 0.85,
                            "bm25_score": 0.72,
                            "combined_score": 0.798,
                            "topic": "Алгебра",
                            "statement": "Решите уравнение x² - 5x + 6 = 0"
                        }
                    ]
                }
            }
        
        # Тестовые данные
        sample_tasks = [
            {
                "id": 1,
                "topic": "Алгебра",
                "subtopic": "Уравнения", 
                "difficulty": 3,
                "statement_text": "Решите уравнение x² - 5x + 6 = 0",
                "skills": ["квадратные уравнения"],
                "tags": ["квадратное уравнение"]
            },
            {
                "id": 2,
                "topic": "Геометрия",
                "subtopic": "Планиметрия",
                "difficulty": 4,
                "statement_text": "В треугольнике катеты равны 3 и 4. Найдите площадь.",
                "skills": ["площадь треугольника"],
                "tags": ["треугольник", "площадь"]
            }
        ]
        
        # Индексация
        indexed = 0
        for task in sample_tasks:
            if rag.index_task(task):
                indexed += 1
        
        # Поиск
        results = rag.hybrid_search("квадратное уравнение", limit=5)
        
        return {
            "status": "success",
            "indexed_tasks": indexed,
            "collection_info": rag.get_collection_info(),
            "search_results": results
        }
        
    except Exception as e:
        return {
            "status": "error", 
            "message": str(e),
            "demo_mode": True
        }

@app.get("/api/rag/search")
async def rag_search(q: str, topic: str = None, difficulty_min: int = 1, difficulty_max: int = 5):
    """Поиск через RAG систему"""
    try:
        from app.services.rag_service import RAGService
        rag = RAGService()
        
        if not rag.available:
            return {
                "query": q,
                "results": [
                    {
                        "task_id": 1,
                        "combined_score": 0.85,
                        "topic": topic or "Алгебра",
                        "statement": f"Демо результат для запроса '{q}'"
                    }
                ],
                "total": 1,
                "mode": "demo"
            }
        
        difficulty_range = (difficulty_min, difficulty_max) if difficulty_min != difficulty_max else None
        results = rag.hybrid_search(q, topic=topic, difficulty_range=difficulty_range)
        
        return {
            "query": q,
            "results": results,
            "total": len(results),
            "mode": "real"
        }
        
    except Exception as e:
        return {
            "query": q,
            "error": str(e),
            "results": [],
            "total": 0
        }