from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pdf2image import convert_from_path
import img2pdf
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
        # ⚡ LIGHTNING FAST COMPRESSION ENGINE (Under 5 Seconds)
        # Slider level ke basis par exact quality filter math lagao
        # level jitna high (jaise 70%), quality parameters ko utna downscale karenge
        target_quality = max(10, 100 - int(level))
        
        # 1. Convert PDF pages to optimized compressed buffers
        pages = convert_from_path(input_path, dpi=100)
        image_bytes_list = []
        
        for i, page in enumerate(pages):
            img_buf = f"page_{i}.jpg"
            # Target quality parameters exact mapping
            page.save(img_buf, 'JPEG', quality=target_quality)
            with open(img_buf, "rb") as f:
                image_bytes_list.append(f.read())
            os.remove(img_buf)
            
        # 2. Reconstruct exactly optimized PDF structural loop
        with open(output_path, "wb") as f_out:
            f_out.write(img2pdf.convert(image_bytes_list))
            
        return FileResponse(output_path, media_type="application/pdf", filename="compressed.pdf")
    except Exception as e:
        return {"error": str(e)}
