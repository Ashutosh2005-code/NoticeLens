import asyncio
import logging
from playwright.async_api import async_playwright, Page, BrowserContext
from typing import Set, List, Dict, Any
from urllib.parse import urlparse

class UniversitySpider:
    def __init__(self, start_url: str, max_depth: int = 2, max_pages: int = 50, concurrency: int = 5):
        self.start_url = start_url
        self.domain = urlparse(start_url).netloc
        self.max_depth = max_depth
        self.max_pages = max_pages
        self.concurrency = concurrency
        self.visited: Set[str] = set()
        self.queue = asyncio.Queue()
        self.assets: Dict[str, List[Any]] = {
            "pdfs": [],
            "images": [],
            "docs": [],
            "pages": []
        }
        self.logger = logging.getLogger("spider")

    async def crawl(self):
        self.logger.info(f"Starting concurrent crawl for {self.start_url} with {self.concurrency} workers")
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(user_agent="DigitalArchaeology/1.0")
            
            # Init queue
            self.queue.put_nowait((self.start_url, 0))
            self.visited.add(self.start_url)
            
            # Start workers
            workers = [asyncio.create_task(self._worker(context, i)) for i in range(self.concurrency)]
            
            await self.queue.join()
            self.logger.info("Queue empty, crawl complete.")
            
            for w in workers:
                w.cancel()
            
            await browser.close()
        return self.assets

    async def _worker(self, context: BrowserContext, worker_id: int):
        page = await context.new_page()
        try:
            while True:
                try:
                    url, depth = await self.queue.get()
                    
                    if len(self.visited) >= self.max_pages:
                        self.queue.task_done()
                        continue
                        
                    await self._process_url(page, url, depth)
                    self.queue.task_done()
                except asyncio.CancelledError:
                    break
                except Exception as e:
                     logger = logging.getLogger("spider")
                     logger.error(f"Worker {worker_id} error on {url if 'url' in locals() else 'unknown'}: {e}")
                     # Ensure we don't hang if we crash
                     try: self.queue.task_done() 
                     except: pass
        finally:
            await page.close()

    async def _process_url(self, page: Page, url: str, depth: int):
        self.logger.info(f"Visiting: {url} (Depth: {depth})")
        
        try:
            response = await page.goto(url, wait_until="domcontentloaded", timeout=30000)
            if not response or response.status >= 400:
                return

            # Extract assets
            await self._extract_assets(page, url)

            # Find links
            if depth < self.max_depth:
                links = await page.evaluate("""
                    () => Array.from(document.querySelectorAll('a[href]')).map(a => a.href)
                """)
                
                for link in links:
                    parsed = urlparse(link)
                    # Allow all domains, relying on max_depth and max_pages for control
                    if True:
                        clean_link = link.split('#')[0]
                        
                        # Atomic check-and-add for concurrency safety should ideally be locked,
                        # but for simple crawling slight races are acceptable or we can add a lock.
                        # Since we are in asyncio (single threaded event loop), set operations are atomic.
                        if clean_link not in self.visited:
                            if len(self.visited) < self.max_pages:
                                self.visited.add(clean_link)
                                self.queue.put_nowait((clean_link, depth + 1))
                            
        except Exception as e:
            self.logger.error(f"Error visiting {url}: {str(e)}")

    async def _extract_assets(self, page: Page, current_url: str):
        # Extract PDFs
        pdfs = await page.evaluate("""
            () => Array.from(document.querySelectorAll('a[href$=".pdf"]')).map(a => a.href)
        """)
        self.assets["pdfs"].extend(pdfs)
        
        # Extract Images (basic)
        images = await page.evaluate("""
            () => Array.from(document.querySelectorAll('img[src]')).map(img => img.src)
        """)
        self.assets["images"].extend(images)
        
        # Extract Text Content
        text_content = await page.evaluate("document.body.innerText")
        if text_content and len(text_content.strip()) > 100:
            self.assets["pages"].append({
                "url": current_url,
                "content": text_content.strip()
            })
