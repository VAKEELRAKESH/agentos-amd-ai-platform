import chromadb
from chromadb.config import Settings as ChromaSettings
from sentence_transformers import SentenceTransformer
from configs.settings import settings
from datetime import datetime, timezone
import uuid, json, os
from typing import Optional

class MemoryManager:

    EMBEDDING_MODEL = "all-MiniLM-L6-v2"  # 80MB, fast, good quality
    COLLECTION_NAME = "agent_workflows"

    def __init__(self):
        # Create vector DB directory if it doesn't exist
        os.makedirs(settings.VECTOR_DB_PATH, exist_ok=True)
        
        # Initialize ChromaDB with persistent storage
        self.client = chromadb.PersistentClient(
            path=settings.VECTOR_DB_PATH,
            settings=ChromaSettings(anonymized_telemetry=False)
        )
        
        # Load local embedding model (downloads once, ~80MB)
        self.encoder = SentenceTransformer(self.EMBEDDING_MODEL)
        
        # Get or create the collection
        self.collection = self.client.get_or_create_collection(
            name=self.COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"}
        )

    def store_workflow(self, 
                       workflow_id: str,
                       task: str, 
                       plan: str, 
                       result: str,
                       status: str,
                       duration: float) -> str:
        """Store a completed workflow as a vector memory."""
        
        # Combine task + plan + result into one searchable document
        document = f"TASK: {task}\n\nPLAN:\n{plan}\n\nRESULT:\n{result}"
        
        # Generate embedding from the document
        embedding = self.encoder.encode(document).tolist()
        
        # Metadata for filtering and display
        metadata = {
            "workflow_id": workflow_id,
            "task": task[:500],           # ChromaDB metadata limit
            "status": status,
            "duration": round(duration, 3),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "task_length": len(task)
        }
        
        memory_id = f"wf_{workflow_id}_{uuid.uuid4().hex[:6]}"
        
        self.collection.add(
            ids=[memory_id],
            embeddings=[embedding],
            documents=[document],
            metadatas=[metadata]
        )
        
        return memory_id

    def recall_similar(self, 
                        query: str, 
                        n_results: int = 3,
                        min_similarity: float = 0.3) -> list[dict]:
        """Find past workflows similar to the current query."""
        
        total = self.collection.count()
        if total == 0:
            return []
        
        # Don't request more results than we have
        n_results = min(n_results, total)
        
        query_embedding = self.encoder.encode(query).tolist()
        
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            include=["documents", "metadatas", "distances"]
        )
        
        memories = []
        for i in range(len(results["ids"][0])):
            distance = results["distances"][0][i]
            similarity = 1 - distance      # cosine: distance → similarity
            
            if similarity >= min_similarity:
                memories.append({
                    "memory_id": results["ids"][0][i],
                    "similarity": round(similarity, 3),
                    "metadata": results["metadatas"][0][i],
                    "snippet": results["documents"][0][i][:300] + "..."
                })
        
        return sorted(memories, key=lambda x: x["similarity"], reverse=True)

    def get_stats(self) -> dict:
        """Return memory statistics."""
        total = self.collection.count()
        return {
            "total_memories": total,
            "collection_name": self.COLLECTION_NAME,
            "embedding_model": self.EMBEDDING_MODEL,
            "storage_path": settings.VECTOR_DB_PATH,
            "status": "active" if total >= 0 else "error"
        }

    def clear_all(self) -> dict:
        """Wipe all memories (use carefully)."""
        count_before = self.collection.count()
        self.client.delete_collection(self.COLLECTION_NAME)
        self.collection = self.client.get_or_create_collection(
            name=self.COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"}
        )
        return {"cleared": count_before, "status": "ok"}

# Singleton instance — one MemoryManager for the whole app
_memory_manager: Optional[MemoryManager] = None

def get_memory_manager() -> MemoryManager:
    global _memory_manager
    if _memory_manager is None:
        _memory_manager = MemoryManager()
    return _memory_manager
