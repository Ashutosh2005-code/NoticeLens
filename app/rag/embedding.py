from langchain_openai import OpenAIEmbeddings
import os
import logging

class EmbeddingGenerator:
    def __init__(self):
        self.logger = logging.getLogger("rag.embedding")
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            self.logger.warning("OPENAI_API_KEY not found. Embeddings will fail.")
        
        try:
            self.model = OpenAIEmbeddings(
                model="text-embedding-3-small",
                dimensions=1536
            )
        except Exception as e:
            self.logger.error(f"Failed to initialize embeddings: {e}")

    def generate(self, text: str):
        try:
            return self.model.embed_query(text)
        except Exception as e:
            self.logger.error(f"Embedding generation failed: {e}")
            return []
