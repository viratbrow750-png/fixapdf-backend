from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import subprocess
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
    input_path = "temp_input.pdf"
    output_path = "compressed_output.pdf"
    
    if os.path.exists(input_path): os.remove(input_path)
    if os.path.exists(output_path): os.remove(output_path)
    
    with open(input_path, "wb") as buffer:
        buffer.write(await file.read())
        
    try:
        # 🎯 EXACT MATHEMATICAL MATCHING FORMULA
        # Slider value (10 to 90) ke basis par resolution DPI calculate hoga.
        # Agar user kam compress bolega, toh DPI high rahega (exact size match).
        # Formula: Slider level jitna high hoga, DPI utna downscale hoga.
        dpi = int(300 - (level * 2.2))
        if dpi < 72: dpi = 72  # Minimum safe DPI boundary
        
        # ⚡ LIGHTNING FAST DYNAMIC GHOSTSCRIPT PROTOCOL
        # Isme hum fixed presets (/screen or /ebook) use nahi kar rahe hain,
        # balki user ke custom resolution parameters ko seedha script injection se command bana rahe hain.
        subprocess.run([
            "gs", 
            "-sDEVICE=pdfwrite", 
            "-dCompatibilityLevel=1.4",
            "-dPDFSETTINGS=/printer",  # Starts with maximum baseline data retention
            "-dNOPAUSE", 
            "-dBATCH",
            "-dDownsampleColorImages=true",
            f"-dColorImageResolution={dpi}",
            "-dDownsampleGrayImages=true",
            f"-dGrayImageResolution={dpi}",
            f"-sOutputFile={output_path}", 
            input_path
        ])
        
        return FileResponse(output_path, media_type="application/pdf", filename="compressed.pdf")
    except Exception as e:
        return {"error": str(e)}
