from fastapi import FastAPI
from fastapi.responses import Response
from pydantic import BaseModel
from typing import List, Dict, Any
import io

app = FastAPI(title="PDF Generation Service")

class PDFGenerationRequest(BaseModel):
    type: str
    data: Dict[str, Any]

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.post("/generate")
async def generate_pdf(request: PDFGenerationRequest):
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import mm
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from datetime import datetime
    
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    
    try:
        c.setFont("Helvetica", 12)
    except:
        pass
    
    data = request.data
    pdf_type = request.type
    assignment_id = data.get("assignment_id", "unknown")
    student_name = data.get("student", {}).get("name", "Unknown Student")
    topics_text = data.get("topics_text", "")
    tasks = data.get("tasks", [])
    
    c.drawString(50, height - 50, f"Assignment #{assignment_id}")
    c.drawString(50, height - 70, f"Student: {student_name}")
    c.drawString(50, height - 90, f"Topics: {topics_text}")
    c.drawString(50, height - 110, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    c.drawString(50, height - 130, f"Type: {pdf_type.title()} Version")
    
    y_position = height - 170
    
    for i, task in enumerate(tasks, 1):
        if y_position < 150:
            c.showPage()
            y_position = height - 50
        
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, y_position, f"Task {i}.")
        y_position -= 20
        
        c.setFont("Helvetica", 11)
        statement = task.get("statement_text", "No statement")
        
        lines = []
        words = statement.split()
        current_line = ""
        
        for word in words:
            test_line = current_line + " " + word if current_line else word
            if len(test_line) > 80:
                if current_line:
                    lines.append(current_line)
                    current_line = word
                else:
                    lines.append(word)
            else:
                current_line = test_line
        
        if current_line:
            lines.append(current_line)
        
        for line in lines:
            c.drawString(70, y_position, line)
            y_position -= 15
        
        if pdf_type == "teacher":
            y_position -= 10
            if task.get("answer"):
                c.setFont("Helvetica-Bold", 10)
                c.drawString(70, y_position, f"Answer: {task.get('answer', '')}")
                y_position -= 15
            
            if task.get("solution_text"):
                c.setFont("Helvetica", 10)
                solution_lines = task.get("solution_text", "").split('\n')
                for sol_line in solution_lines[:3]:
                    c.drawString(70, y_position, f"Solution: {sol_line}")
                    y_position -= 12
        else:
            y_position -= 30
        
        y_position -= 20
    
    c.save()
    buffer.seek(0)
    pdf_content = buffer.read()
    buffer.close()
    
    filename = f"assignment_{assignment_id}_{pdf_type}.pdf"
    return Response(
        content=pdf_content,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

