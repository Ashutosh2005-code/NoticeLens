import logging
import pytesseract
from PIL import Image
import io
import httpx

class OCRProcessor:
    def __init__(self):
        self.logger = logging.getLogger("processor.ocr")
        # Ensure tesseract is installed in the system or path
        # pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

    def process_image(self, image_content: bytes) -> str:
        try:
            image = Image.open(io.BytesIO(image_content))
            text = pytesseract.image_to_string(image)
            self.logger.info(f"OCR Extracted {len(text)} chars")
            return text
        except Exception as e:
            self.logger.error(f"OCR Failed: {e}")
            return ""

    async def process_url(self, url: str) -> str:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url)
                if response.status_code == 200:
                    return self.process_image(response.content)
            return ""
        except Exception as e:
            self.logger.error(f"Failed to fetch image {url}: {e}")
            return ""
