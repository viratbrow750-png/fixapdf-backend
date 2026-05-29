from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import fitz  # PyMuPDF Core Engine
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
        doc = fitz.open(input_path)
        
        # Asli size-change logic: level jitna badhega, compression utna heavy hoga
        # level=10 matlab original ke paas (90% quality), level=50 matlab safe balance (50% quality)
        quality_factor = max(10, 100 - int(level))
        
        for page in doc:
            for img in page.get_images(full=True):
                xref = img[0]
                pix = fitz.Pixmap(doc, xref)
                
                # Squeezer engine running inside byte matrices
                compressed_img_bytes = pix.tobytes("jpeg", quality=quality_factor)
                doc.update_stream(xref, compressed_img_bytes)
        
        # Professional compression settings with absolute metadata optimization
        doc.save(
            output_path, 
            garbage=4, 
            deflate=True, 
            clean=True
        )
        doc.close()
            
        return FileResponse(output_path, media_type="application/pdf", filename="compressed.pdf")
    except Exception as e:
        return {"error": str(e)}
