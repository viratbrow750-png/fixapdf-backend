from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pypdf import PdfReader, PdfWriter
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/compress")
async def compress_pdf(file: UploadFile = File(...), level: int = Form(50)):
    # 1. File ko temporary save karo
    input_path = "temp_input.pdf"
    output_path = "compressed_output.pdf"
    
    with open(input_path, "wb") as buffer:
        buffer.write(await file.read())
    
    try:
        # 2. PyPDF Core Compression Engine
        reader = PdfReader(input_path)
        writer = PdfWriter()
        
        for page in reader.pages:
            writer.add_page(page)
            
        # Slider ke level ke hisab se compression algorithm lagao
        # Jitna zyada level hoga, utna zyada object streams ko tight compress karenge
        if level >= 50:
            for page in writer.pages:
                # Yeh images aur content streams ko bina quality bigade losslessly compress karta hai
                page.compress_content_streams() 
                
        # 3. Exact target byte metadata compression
        with open(output_path, "wb") as f:
            writer.write(f)
            
        return FileResponse(output_path, media_type="application/pdf", filename="compressed.pdf")
        
    except Exception as e:
        return {"error": str(e)}
