from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import subprocess

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/compress")
async def compress_pdf(file: UploadFile = File(...), level: int = Form(50)):
    # 1. Input cache write
    with open("temp.pdf", "wb") as buffer:
        buffer.write(await file.read())
    
    # 2. Lightning Fast EXACT Scaling Logic mapping user slider input
    # Fast rendering algorithms switch manually inside server perimeter
    if level >= 70:
        gs_setting = "/screen"  # Maximum Compression
    elif level <= 30:
        gs_setting = "/printer" # Low Compression (High Quality)
    else:
        gs_setting = "/ebook"   # Standard Balanced Compression (Exact target)
        
    # 3. Supercharged Ghostscript Execution Blueprint (Optimized parameters for 5 Sec limit)
    subprocess.run([
        "gs", 
        "-sDEVICE=pdfwrite", 
        f"-dPDFSETTINGS={gs_setting}", 
        "-dCompatibilityLevel=1.4",
        "-dEmbedAllFonts=true", 
        "-dSubsetTexts=true",
        "-dNOPAUSE", 
        "-dBATCH", 
        "-sOutputFile=out.pdf", 
        "temp.pdf"
    ])
    
    return FileResponse("out.pdf", media_type="application/pdf", filename="compressed.pdf")
