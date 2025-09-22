import os
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from qdrant_client import QdrantClient
from qdrant_client.http import models
import meilisearch
import logging
import hashlib
import re

try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False

logger = logging.getLogger(__name__)

class RAGService:
    def __init__(self):
        self.qdrant_url = os.getenv("QDRANT_URL", "http://localhost:6333")
        self.meili_url = os.getenv("MEILI_URL", "http://localhost:7700")
        self.meili_key = os.getenv("MEILI_MASTER_KEY", "A0TtmeQyFUGBM3We9fbThjuaT3Zq8U72FQh6AO3F2-s")
        
        # Инициализация модели эмбеддингов
        self.embedding_model = None
        if SENTENCE_TRANSFORMERS_AVAILABLE:
            try:
                self.embedding_model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
                logger.info("Sentence transformer model loaded")
            except Exception as e:
                logger.warning(f"Could not load embedding model: {e}")
        
        try:
            self.qdrant_client = QdrantClient(url=self.qdrant_url)
            self.meili_client = meilisearch.Client(self.meili_url, self.meili_key)
            self.collection_name = "tasks"
            self.index_name = "tasks"
            self._ensure_collections()
            self.available = True
            logger.info("RAG Service initialized successfully")
        except Exception as e:
            logger.warning(f"RAG Service not available: {e}")
            self.available = False
    
    def _ensure_collections(self):
        try:
            collections = self.qdrant_client.get_collections().collections
            collection_names = [c.name for c in collections]
            
            if self.collection_name not in collection_names:
                self.qdrant_client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=models.VectorParams(
                        size=384,
                        distance=models.Distance.COSINE
                    )
                )
                logger.info(f"Created Qdrant collection: {self.collection_name}")
        except Exception as e:
            logger.error(f"Error creating Qdrant collection: {e}")
        
        try:
            try:
                self.meili_client.get_index(self.index_name)
            except:
                self.meili_client.create_index(self.index_name, {'primaryKey': 'id'})
                logger.info(f"Created Meilisearch index: {self.index_name}")
                
                index = self.meili_client.index(self.index_name)
                index.update_searchable_attributes([
                    'statement_text', 'topic', 'subtopic', 'tags', 'skills'
                ])
                index.update_filterable_attributes([
                    'topic', 'subtopic', 'difficulty', 'format', 'tags'
                ])
        except Exception as e:
            logger.error(f"Error creating Meilisearch index: {e}")
    
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
    
    def index_task(self, task_data: Dict[str, Any]):
        if not self.available:
            return False
            
        try:
            normalized_text = self.normalize_text(task_data['statement_text'])
            skeleton = self.extract_skeleton(normalized_text)
            skeleton_hash = self.compute_skeleton_hash(skeleton)
            
            # Генерация эмбеддинга
            if self.embedding_model:
                embedding = self.embedding_model.encode(normalized_text).tolist()
            else:
                embedding = np.random.rand(384).tolist()
            
            # Индексация в Qdrant
            self.qdrant_client.upsert(
                collection_name=self.collection_name,
                points=[
                    models.PointStruct(
                        id=task_data['id'],
                        vector=embedding,
                        payload={
                            "task_id": task_data['id'],
                            "topic": task_data['topic'],
                            "subtopic": task_data.get('subtopic', ''),
                            "difficulty": task_data['difficulty'],
                            "skeleton_hash": skeleton_hash
                        }
                    )
                ]
            )
            
            # Индексация в Meilisearch
            meili_doc = {
                "id": task_data['id'],
                "statement_text": normalized_text,
                "topic": task_data['topic'],
                "subtopic": task_data.get('subtopic', ''),
                "difficulty": task_data['difficulty'],
                "tags": task_data.get('tags', []),
                "skills": task_data.get('skills', []),
                "skeleton_hash": skeleton_hash
            }
            
            index = self.meili_client.index(self.index_name)
            index.add_documents([meili_doc])
            
            logger.info(f"Indexed task {task_data['id']} successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error indexing task {task_data['id']}: {e}")
            return False
    
    def hybrid_search(
        self,
        query: str,
        topic: Optional[str] = None,
        difficulty_range: Optional[Tuple[int, int]] = None,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        
        if not self.available:
            return []
            
        try:
            # Генерация эмбеддинга запроса
            if self.embedding_model:
                query_embedding = self.embedding_model.encode(query).tolist()
            else:
                query_embedding = np.random.rand(384).tolist()
            
            # Векторный поиск в Qdrant
            qdrant_filter = models.Filter(must=[])
            if topic:
                qdrant_filter.must.append(
                    models.FieldCondition(key="topic", match=models.MatchValue(value=topic))
                )
            if difficulty_range:
                qdrant_filter.must.append(
                    models.FieldCondition(
                        key="difficulty",
                        range=models.Range(gte=difficulty_range[0], lte=difficulty_range[1])
                    )
                )
            
            vector_results = self.qdrant_client.search(
                collection_name=self.collection_name,
                query_vector=query_embedding,
                query_filter=qdrant_filter if qdrant_filter.must else None,
                limit=limit
            )
            
            # BM25 поиск в Meilisearch
            meili_filter = []
            if topic:
                meili_filter.append(f"topic = '{topic}'")
            if difficulty_range:
                meili_filter.append(f"difficulty >= {difficulty_range[0]} AND difficulty <= {difficulty_range[1]}")
            
            index = self.meili_client.index(self.index_name)
            bm25_results = index.search(
                query,
                {
                    "limit": limit,
                    "filter": " AND ".join(meili_filter) if meili_filter else None
                }
            )
            
            # Комбинирование результатов (60% векторы + 40% BM25)
            combined_scores = {}
            
            for result in vector_results:
                task_id = result.payload["task_id"]
                combined_scores[task_id] = {
                    "task_id": task_id,
                    "vector_score": result.score,
                    "bm25_score": 0.0,
                    "combined_score": result.score * 0.6
                }
            
            for result in bm25_results["hits"]:
                task_id = result["id"]
                bm25_score = 1.0 / (1.0 + result.get("_rankingScore", 1000))
                
                if task_id in combined_scores:
                    combined_scores[task_id]["bm25_score"] = bm25_score
                    combined_scores[task_id]["combined_score"] = (
                        combined_scores[task_id]["vector_score"] * 0.6 + bm25_score * 0.4
                    )
                else:
                    combined_scores[task_id] = {
                        "task_id": task_id,
                        "vector_score": 0.0,
                        "bm25_score": bm25_score,
                        "combined_score": bm25_score * 0.4
                    }
            
            # Сортировка по итоговому скору
            sorted_results = sorted(
                combined_scores.values(),
                key=lambda x: x["combined_score"],
                reverse=True
            )
            
            return sorted_results[:limit]
            
        except Exception as e:
            logger.error(f"Error in hybrid search: {e}")
            return []
    
    def get_collection_info(self):
        if not self.available:
            return {"error": "RAG Service not available"}
            
        try:
            # Информация о Qdrant коллекции
            collection_info = self.qdrant_client.get_collection(self.collection_name)
            
            # Информация о Meilisearch индексе
            index = self.meili_client.index(self.index_name)
            index_stats = index.get_stats()
            
            return {
                "qdrant": {
                    "collection": self.collection_name,
                    "points_count": collection_info.points_count,
                    "vector_size": collection_info.config.params.vectors.size
                },
                "meilisearch": {
                    "index": self.index_name,
                    "documents_count": index_stats.get("numberOfDocuments", 0)
                }
            }
        except Exception as e:
            return {"error": str(e)}

