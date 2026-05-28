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
        original_size = os.path.getsize(input_path)
        
        # 🎯 TARGET MB CALCULATOR
        # Slider value ke hisab se exact target size nikalenge bytes mein
        # Agar 32MB ki file hai aur user 20% bola, toh target size 26MB ke aas-paas set hoga
        reduction_ratio = (100 - level) / 100.0
        target_size = original_size * reduction_ratio
        
        # Dynamic feedback variables
        low_dpi = 60
        high_dpi = 300
        best_dpi = 150
        
        # ⚡ ITERATIVE TARGET FEEDBACK LOOP (Runs in 3-5 Sec)
        # Yeh server par 4 baar fast check chalayega taaki exact output size mile
        for _ in range(4):
            current_dpi = int((low_dpi + high_dpi) / 2)
            
            if os.path.exists(output_path): os.remove(output_path)
            
            subprocess.run([
                "gs", "-sDEVICE=pdfwrite", "-dCompatibilityLevel=1.4",
                "-dPDFSETTINGS=/printer", "-dNOPAUSE", "-dBATCH",
                "-dDownsampleColorImages=true", f"-dColorImageResolution={current_dpi}",
                "-dDownsampleGrayImages=true", f"-dGrayImageResolution={current_dpi}",
                f"-sOutputFile={output_path}", input_path
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            if not os.path.exists(output_path):
                break
                
            current_compressed_size = os.path.getsize(output_path)
            
            # Agar file target size se badi hai, toh quality/DPI aur kam karo
            if current_compressed_size > target_size:
                high_dpi = current_dpi - 1
            else:
                # Agar file target ke paas hai ya choti hai, toh safe zone save karo
                low_dpi = current_dpi + 1
                best_dpi = current_dpi
                
        # Final pass with the best matched DPI parameter
        if os.path.exists(output_path): os.remove(output_path)
        subprocess.run([
            "gs", "-sDEVICE=pdfwrite", "-dCompatibilityLevel=1.4",
            "-dPDFSETTINGS=/printer", "-dNOPAUSE", "-dBATCH",
            "-dDownsampleColorImages=true", f"-dColorImageResolution={best_dpi}",
            "-dDownsampleGrayImages=true", f"-dGrayImageResolution={best_dpi}",
            f"-sOutputFile={output_path}", input_path
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        return FileResponse(output_path, media_type="application/pdf", filename="compressed.pdf")
    except Exception as e:
        return {"error": str(e)}
