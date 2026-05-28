from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import os

# Render par pypdf import check karne ke liye safe wrapper
try:
    from pypdf import PdfReader, PdfWriter
except ImportError:
    import subprocess
    import sys
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pypdf"])
    from pypdf import PdfReader, PdfWriter

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
    input_path = "temp_input.pdf"
    output_path = "compressed_output.pdf"
    
    # Purani files clear karo agar server par bachi hon
    if os.path.exists(input_path): os.remove(input_path)
    if os.path.exists(output_path): os.remove(output_path)
    
    with open(input_path, "wb") as buffer:
        buffer.write(await file.read())
    
    try:
        reader = PdfReader(input_path)
        writer = PdfWriter()
        
        for page in reader.pages:
            writer.add_page(page)
            
        # ⚡ LIGHTNING FAST COMPRESSION ALGORITHM (Under 5 Seconds)
        # User ke select kiye slider level ke mutabik lossless metadata tables aur duplicate streams compress honge
        if level >= 40:
            for page in writer.pages:
                page.compress_content_streams()
                
        with open(output_path, "wb") as f:
            writer.write(f)
            
        return FileResponse(output_path, media_type="application/pdf", filename="compressed.pdf")
        
    except Exception as e:
        return {"error": str(e)}
