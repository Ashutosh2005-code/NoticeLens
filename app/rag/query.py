import logging
from .store import VectorStore
from .embedding import EmbeddingGenerator
# Note: In a full implementation, we'd use a ChatModel here (e.g. ChatOpenAI)

class QueryEngine:
    def __init__(self, vector_store: VectorStore, embedding_generator: EmbeddingGenerator):
        self.store = vector_store
        self.embedder = embedding_generator
        self.logger = logging.getLogger("rag.query")

    def answer_question(self, question: str) -> str:
        self.logger.info(f"Answering: {question}")
        
        # 1. Retrieve context
        results = self.store.query(question)
        context_docs = results.get("documents", [])
        metadatas = results.get("metadatas", [])
        
        if not context_docs:
            return {"answer": "I couldn't find any relevant information on the website.", "sources": []}
        
        # Extract unique sources
        sources = set()
        for meta in metadatas:
            if "source" in meta:
                sources.add(meta["source"])
        
        # 2. Synthesize answer (Mocked for now without full LLM chain)
        # In real implementation: call LLM with context + question
        
        answer_intro = f"I found helpul information from {len(sources)} sources:"
        context_preview = "\n\n".join([d[:200] + "..." for d in context_docs[:3]])
        
        answer = f"{answer_intro}\n\n**Relevant Context:**\n{context_preview}\n\n**Summary:**\nBased on these documents, here is the answer to your question..."
        return {"answer": answer, "sources": list(sources)}
