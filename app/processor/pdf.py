import logging
import io
from pypdf import PdfReader

class PDFProcessor:
    def __init__(self):
        self.logger = logging.getLogger("processor.pdf")

    def extract_text(self, file_content: bytes) -> str:
        """
        Extracts text from PDF bytes.
        """
        try:
            reader = PdfReader(io.BytesIO(file_content))
            text = []
            for page in reader.pages:
                extracted = page.extract_text()
                if extracted:
                    text.append(extracted)
            
            full_text = "\n".join(text)
            self.logger.info(f"Extracted {len(full_text)} characters from PDF")
            return full_text
        except Exception as e:
            self.logger.error(f"Error extracting PDF text: {e}")
            return ""
