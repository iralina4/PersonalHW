import httpx
import os
import tempfile
from typing import Dict, Any

class PDFService:
    def __init__(self):
        self.pdf_service_url = os.getenv("PDF_SERVICE_URL", "http://localhost:8001")
    
    def generate_student_pdf(self, data: Dict[str, Any]) -> str:
        try:
            with httpx.Client() as client:
                response = client.post(
                    f"{self.pdf_service_url}/generate",
                    json={
                        "type": "student",
                        "data": data
                    },
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    assignment_id = data.get("assignment_id", "unknown")
                    filename = f"assignment_{assignment_id}_student.pdf"
                    filepath = os.path.join(tempfile.gettempdir(), filename)
                    
                    with open(filepath, "wb") as f:
                        f.write(response.content)
                    
                    return filepath
                else:
                    raise Exception(f"PDF service error: {response.status_code}")
        
        except Exception as e:
            return self._generate_fallback_pdf(data, "student")
    
    def generate_teacher_pdf(self, data: Dict[str, Any]) -> str:
        try:
            with httpx.Client() as client:
                response = client.post(
                    f"{self.pdf_service_url}/generate",
                    json={
                        "type": "teacher",
                        "data": data
                    },
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    assignment_id = data.get("assignment_id", "unknown")
                    filename = f"assignment_{assignment_id}_teacher.pdf"
                    filepath = os.path.join(tempfile.gettempdir(), filename)
                    
                    with open(filepath, "wb") as f:
                        f.write(response.content)
                    
                    return filepath
                else:
                    raise Exception(f"PDF service error: {response.status_code}")
        
        except Exception as e:
            return self._generate_fallback_pdf(data, "teacher")
    
    def _generate_fallback_pdf(self, data: Dict[str, Any], pdf_type: str) -> str:
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import A4
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont
        from reportlab.lib.units import mm
        
        assignment_id = data.get("assignment_id", "unknown")
        filename = f"assignment_{assignment_id}_{pdf_type}.pdf"
        filepath = os.path.join(tempfile.gettempdir(), filename)
        
        c = canvas.Canvas(filepath, pagesize=A4)
        width, height = A4
        
        try:
            pdfmetrics.registerFont(TTFont('DejaVuSans', '/System/Library/Fonts/Arial.ttf'))
            c.setFont("DejaVuSans", 12)
        except:
            c.setFont("Helvetica", 12)
        
        c.drawString(50, height - 50, f"Assignment #{assignment_id}")
        c.drawString(50, height - 70, f"Student: {data.get('student', {}).get('name', 'Unknown')}")
        c.drawString(50, height - 90, f"Topics: {data.get('topics_text', '')}")
        c.drawString(50, height - 110, f"Type: {pdf_type.title()}")
        
        y_position = height - 150
        
        for i, task in enumerate(data.get("tasks", []), 1):
            if y_position < 100:
                c.showPage()
                y_position = height - 50
            
            c.drawString(50, y_position, f"{i}. {task.get('statement_text', '')[:100]}...")
            y_position -= 30
            
            if pdf_type == "teacher" and task.get('answer'):
                c.drawString(70, y_position, f"Answer: {task.get('answer', '')}")
                y_position -= 20
        
        c.save()
        return filepath
