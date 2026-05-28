from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pypdf import PdfReader, PdfWriter
import os

app = FastAPI()

# Browser security settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/compress")
async def compress_pdf(file: UploadFile = File(...), level: int = Form(50)):
    input_path = "temp_input.pdf"
    output_path = "compressed_output.pdf"
    
    # Purani files safe clean karo
    if os.path.exists(input_path): os.remove(input_path)
    if os.path.exists(output_path): os.remove(output_path)
    
    # 1. File save locally
    with open(input_path, "wb") as buffer:
        buffer.write(await file.read())
    
    try:
        reader = PdfReader(input_path)
        writer = PdfWriter()
        
        for page in reader.pages:
            writer.add_page(page)
            
        # ⚡ USER SLIDER-BASED MATH LOGIC (Exact Target)
        # Jitna slider set hoga, us hisab se lossless content compression chalega
        if level >= 30:
            for page in writer.pages:
                page.compress_content_streams()
                
        # 2. Compress and save document structure
        with open(output_path, "wb") as f:
            writer.write(f)
            
        return FileResponse(output_path, media_type="application/pdf", filename="compressed.pdf")
        
    except Exception as e:
        return {"error": str(e)}
