import chromadb
import logging
from typing import List, Dict, Any

class VectorStore:
    def __init__(self, persistence_path: str = "./chroma_db"):
        self.logger = logging.getLogger("rag.store")
        self.persistence_path = persistence_path
        try:
            self.client = chromadb.PersistentClient(path=persistence_path)
            self.collection = self.client.get_or_create_collection(name="university_knowledge")
            self.logger.info(f"Connected to ChromaDB at {persistence_path}")
        except Exception as e:
            self.logger.error(f"Failed to initialize ChromaDB: {e}")
            raise e

    def clear(self):
        """
        Clear the entire vector store to remove old data.
        """
        try:
            self.client.delete_collection("university_knowledge")
            self.collection = self.client.get_or_create_collection(name="university_knowledge")
            self.logger.info("Vector store cleared successfully.")
            return True
        except Exception as e:
            self.logger.error(f"Failed to clear vector store: {e}")
            return False

    def add_texts(self, texts: List[str], metadatas: List[Dict[str, Any]], ids: List[str]):
        """
        Add text chunks to the vector store.
        """
        if not texts:
            return
        
        try:
            self.collection.add(
                documents=texts,
                metadatas=metadatas,
                ids=ids
            )
            self.logger.info(f"Added {len(texts)} documents to vector store")
        except Exception as e:
            self.logger.error(f"Error adding documents: {e}")

    def query(self, query_text: str, n_results: int = 5) -> List[str]:
        """
        Semantic search.
        """
        try:
            results = self.collection.query(
                query_texts=[query_text],
                n_results=n_results
            )
            # Flatten results
            documents = results.get("documents", [])
            metadatas = results.get("metadatas", [])
            
            if documents and metadatas:
                 return {"documents": documents[0], "metadatas": metadatas[0]}
            return {"documents": [], "metadatas": []}
        except Exception as e:
            self.logger.error(f"Error querying vector store: {e}")
            return []
