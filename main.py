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
    # 1. User ki file ko temp save karo
    with open("temp.pdf", "wb") as buffer:
        buffer.write(await file.read())
    
    # 2. Slider input ke mutabik Ghostscript settings set karo
    # Agar compression high chahiye (slider value high), toh quality level low set karo
    gs_setting = "/ebook"
    if level > 70:
        gs_setting = "/screen"  # High compression, low resolution
    elif level < 30:
        gs_setting = "/printer" # Low compression, high quality
        
    # 3. Ghostscript Engine Run karo
    subprocess.run(["gs", "-sDEVICE=pdfwrite", f"-dPDFSETTINGS={gs_setting}", 
                    "-dNOPAUSE", "-dBATCH", "-sOutputFile=out.pdf", "temp.pdf"])
    
    return FileResponse("out.pdf", media_type="application/pdf", filename="compressed.pdf")
