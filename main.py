from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import fitz  # PyMuPDF
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
        
        # level ke mutabik image quality set hogi (bina crash kiye)
        quality_factor = max(10, 100 - int(level))
        
        for page in doc:
            # Page ki saari images ki list nikaalo
            image_list = page.get_images(full=True)
            
            for img_info in image_list:
                xref = img_info[0]
                
                # Image ka exact position (rect) pata karo page par
                rects = page.get_image_rects(xref)
                if not rects:
                    continue
                rect = rects[0] # Pehla bbox location
                
                # Pixmap nikaalo aur use low-quality JPEG bytes mein convert karo
                pix = fitz.Pixmap(doc, xref)
                compressed_bytes = pix.tobytes("jpeg", quality=quality_factor)
                
                # Purani heavy image ko page se delete karo aur nayi compressed image usi jagah chipkao
                page.delete_image(xref)
                page.insert_image(rect, stream=compressed_bytes)
        
        # Ab ekdum tightly pack karke save karo (bina crash hue chota size milega)
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
