from fastapi import UploadFile
import pdfplumber
import docx
from typing import Optional
import io

class Parser:

    def __init__(self):
        pass
    
    async def read_file(self, file: UploadFile) -> Optional[str]:

        contents = await file.read()


        if file.content_type == "application/pdf":

            try:
                with pdfplumber.open(io.BytesIO(contents)) as pdf:
                    text = "".join([page.extract_text() for page in pdf.pages])
                    return text
            except Exception as e:
                print(f"Pdf parsing error: {e}")
                return None
        
        elif file.content_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            try:
                
                from io import BytesIO
                doc = docx.Document(BytesIO(contents))
                text = "\n".join([p.text for p in doc.paragraphs])
                return text
            except Exception as e:
               print(f"Docx parsing error : {e}") 
               return None
        else:
            return None
    
    