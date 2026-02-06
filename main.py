from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import logging
import asyncio
import sys
import uuid
from typing import List

# Fix for Windows: Enforce ProactorEventLoop for subprocess support (Playwright)
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

import httpx # Added for downloading assets

# Import our modules
from app.crawler.spider import UniversitySpider
from app.crawler.extractor import ContentExtractor
from app.processor.ocr import OCRProcessor
from app.processor.cleaner import HTMLCleaner
from app.processor.pdf import PDFProcessor
from app.rag.store import VectorStore
from app.rag.embedding import EmbeddingGenerator
from app.rag.query import QueryEngine
from app.processor.chunker import TextChunker

# Setup Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("api")

app = FastAPI(title="Digital Archaeology API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Connection Manager for WebSockets
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except:
                pass

manager = ConnectionManager()

# Init Core Systems (Lazy load or global)
# In production, these should be dependencies
vector_store = VectorStore()
embedding_gen = EmbeddingGenerator()
query_engine = QueryEngine(vector_store, embedding_gen)
ocr_proc = OCRProcessor()
pdf_proc = PDFProcessor()

class CrawlRequest(BaseModel):
    url: str
    max_depth: int = 3
    max_pages: int = 100

class QueryRequest(BaseModel):
    question: str

@app.get("/")
async def root():
    return {"status": "online", "system": "Digital Archaeology"}

@app.post("/crawl")
async def start_crawl(request: CrawlRequest):
    url = request.url
    max_depth = request.max_depth
    max_pages = request.max_pages
    
    logger.info(f"Received crawl request for {url} with depth={max_depth}, pages={max_pages}")
    await manager.broadcast(f"Starting crawl for {url}")
    
    # Run crawl in background to not block
    asyncio.create_task(run_crawling_pipeline(url, max_depth, max_pages))
    
    return {"status": "started", "message": f"Crawling {url}"}

async def run_crawling_pipeline(url: str, max_depth: int, max_pages: int):
    try:
        # Clear existing knowledge base before starting new crawl
        vector_store.clear()
        
        spider = UniversitySpider(url, max_depth=max_depth, max_pages=max_pages)
        await manager.broadcast("Spider initialized. Knowledge base cleared. Visiting pages...")
        
        assets = await spider.crawl()
        
        await manager.broadcast(f"Crawl finished. Found {len(assets['pdfs'])} PDFs and {len(assets['images'])} Images.")
        
        # Initialize Chunker
        chunker = TextChunker(chunk_size=1000, overlap=200)

        # Process PDFs
        for pdf in assets['pdfs']:
            try:
                await manager.broadcast(f"Processing PDF: {pdf}")
                async with httpx.AsyncClient() as client:
                    resp = await client.get(pdf)
                    if resp.status_code == 200:
                        text = pdf_proc.extract_text(resp.content)
                        if text:
                            chunks = chunker.split_text(text)
                            if chunks:
                                await manager.broadcast(f"Indexing PDF {pdf} in {len(chunks)} chunks")
                                vector_store.add_texts(
                                    texts=chunks,
                                    metadatas=[{"source": pdf, "type": "pdf"} for _ in chunks],
                                    ids=[str(uuid.uuid4()) for _ in chunks]
                                )
            except Exception as e:
                logger.error(f"Failed to process PDF {pdf}: {e}")

        # Process Images
        for img in assets['images']:
            try:
                await manager.broadcast(f"Processing Image (OCR): {img}")
                text = await ocr_proc.process_url(img)
                if text and len(text) > 10: 
                    chunks = chunker.split_text(text)
                    if chunks:
                        vector_store.add_texts(
                            texts=chunks,
                            metadatas=[{"source": img, "type": "image"} for _ in chunks],
                            ids=[str(uuid.uuid4()) for _ in chunks]
                        )
            except Exception as e:
                 logger.error(f"Failed to process Image {img}: {e}")

        if "pages" in assets:
            for page in assets["pages"]:
                await manager.broadcast(f"Indexing page: {page['url']}")
                content = page["content"]
                if content:
                    chunks = chunker.split_text(content)
                    if chunks:
                         vector_store.add_texts(
                            texts=chunks,
                            metadatas=[{"source": page["url"], "type": "html"} for _ in chunks],
                            ids=[str(uuid.uuid4()) for _ in chunks]
                        )

        await manager.broadcast("Indexing complete. Ready for questions.")
        
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        logger.error(f"Crawl failed: {error_trace}")
        await manager.broadcast(f"Error: {repr(e)}")

@app.post("/query")
async def query_knowledge(request: QueryRequest):
    response = query_engine.answer_question(request.question)
    return response # Returns {"answer": ..., "sources": ...}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

if __name__ == "__main__":
    import uvicorn
    # Reload=True can interfere with Windows Event Loops in asyncio
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=False)
