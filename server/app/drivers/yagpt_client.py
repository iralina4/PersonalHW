import os
import httpx
import json
from typing import Dict, Any, Optional, List
import logging
import asyncio

logger = logging.getLogger(__name__)

class YaGPTClient:
    def __init__(self):
        self.api_url = os.getenv("YAGPT_API_URL", "https://llm.api.cloud.yandex.net/foundationModels/v1/completion")
        self.api_key = os.getenv("YAGPT_API_KEY")
        self.model = os.getenv("YAGPT_MODEL", "yandexgpt-lite")
        
        if not self.api_key:
            logger.warning("YAGPT_API_KEY not set, using mock responses")
            self.mock_mode = True
        else:
            self.mock_mode = False
    
    async def generate_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> Optional[str]:
        
        if self.mock_mode:
            return self._mock_completion(messages)
        
        headers = {
            "Authorization": f"Api-Key {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "modelUri": f"gpt://{self.model}",
            "completionOptions": {
                "stream": False,
                "temperature": temperature,
                "maxTokens": max_tokens
            },
            "messages": messages
        }
        
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    self.api_url,
                    headers=headers,
                    json=payload
                )
                
                if response.status_code == 200:
                    result = response.json()
                    return result["result"]["alternatives"][0]["message"]["text"]
                else:
                    logger.error(f"YaGPT API error: {response.status_code} - {response.text}")
                    return self._mock_completion(messages)
                    
        except Exception as e:
            logger.error(f"Error calling YaGPT API: {e}")
            return self._mock_completion(messages)
    
    def _mock_completion(self, messages: List[Dict[str, str]]) -> str:
        user_message = ""
        for msg in messages:
            if msg.get("role") == "user":
                user_message = msg.get("text", "")
                break
        
        if "новый вариант задачи" in user_message.lower():
            return '''```json
{
  "statement_text": "Решите уравнение x² - 7x + 12 = 0",
  "statement_tex": "x^2 - 7x + 12 = 0",
  "answer": "x = 3; x = 4",
  "solution_text": "Найдем дискриминант: D = 49 - 48 = 1. x₁ = (7+1)/2 = 4, x₂ = (7-1)/2 = 3",
  "solution_tex": "D = 49 - 48 = 1, x_1 = \\\\frac{7+1}{2} = 4, x_2 = \\\\frac{7-1}{2} = 3"
}
```'''
        
        if "выбери и отсортируй" in user_message.lower():
            return '''[
  {"task_id": 1, "priority": 0.9, "reason": "Соответствует слабой теме ученика - квадратные уравнения"},
  {"task_id": 2, "priority": 0.8, "reason": "Подходящий уровень сложности для целевого балла"},
  {"task_id": 3, "priority": 0.7, "reason": "Развивает навыки работы с логарифмами"}
]'''
        
        return "Извините, сервис временно недоступен. Используется заглушка."
    
    async def generate_task_variant(
        self,
        original_task: Dict[str, Any],
        student_profile: Dict[str, Any],
        prompt_template: str
    ) -> Optional[Dict[str, Any]]:
        
        messages = [
            {
                "role": "system",
                "text": prompt_template
            },
            {
                "role": "user",
                "text": f"""
Исходная задача:
{json.dumps(original_task, ensure_ascii=False, indent=2)}

Профиль ученика:
{json.dumps(student_profile, ensure_ascii=False, indent=2)}

Создай новый вариант задачи, изменив числовые параметры и контекст под профиль ученика.
Ответ должен быть в формате JSON с полями: statement_text, statement_tex, answer, solution_text, solution_tex.
"""
            }
        ]
        
        try:
            response = await self.generate_completion(messages, temperature=0.8)
            if response:
                response_clean = response.strip()
                if response_clean.startswith("```json"):
                    response_clean = response_clean[7:]
                if response_clean.endswith("```"):
                    response_clean = response_clean[:-3]
                
                return json.loads(response_clean)
            return None
            
        except Exception as e:
            logger.error(f"Error generating task variant: {e}")
            return None
    
    async def personalize_task_selection(
        self,
        candidate_tasks: List[Dict[str, Any]],
        student_profile: Dict[str, Any],
        topics_request: str
    ) -> List[Dict[str, Any]]:
        
        messages = [
            {
                "role": "system",
                "text": """Ты эксперт по персонализации заданий ЕГЭ по математике. 
Анализируй профиль ученика и выбирай наиболее подходящие задачи из предложенных кандидатов.
Учитывай слабые и сильные темы, целевой балл, предпочитаемые типы заданий."""
            },
            {
                "role": "user",
                "text": f"""
Профиль ученика:
{json.dumps(student_profile, ensure_ascii=False, indent=2)}

Запрос на темы:
{topics_request}

Кандидаты задач:
{json.dumps(candidate_tasks, ensure_ascii=False, indent=2)}

Выбери и отсортируй задачи по приоритету для данного ученика. 
Объясни выбор каждой задачи.
Ответ в формате JSON: [{"task_id": int, "priority": float, "reason": "string"}]
"""
            }
        ]
        
        try:
            response = await self.generate_completion(messages, temperature=0.3)
            if response:
                response_clean = response.strip()
                if response_clean.startswith("```json"):
                    response_clean = response_clean[7:]
                if response_clean.endswith("```"):
                    response_clean = response_clean[:-3]
                
                return json.loads(response_clean)
            return []
            
        except Exception as e:
            logger.error(f"Error personalizing task selection: {e}")
            return []