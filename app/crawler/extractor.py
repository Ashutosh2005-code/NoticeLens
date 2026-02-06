import logging
import mimetypes
from urllib.parse import urlparse

class ContentExtractor:
    def __init__(self):
        self.logger = logging.getLogger("crawler.extractor")

    def determine_content_type(self, url: str) -> str:
        parsed = urlparse(url)
        path = parsed.path.lower()
        
        type, _ = mimetypes.guess_type(path)
        
        if path.endswith(".pdf"):
            return "pdf"
        elif type and type.startswith("image"):
            return "image"
        else:
            return "html"
