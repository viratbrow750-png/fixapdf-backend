from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import fitz  # PyMuPDF engine
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
        # 🎯 ENTERPRISE IMAGE & MATRIX DEFLECTION ALGORITHM
        # User ke slider percentage input (10 to 90) ko lekar 
        # exact target stream grid calculations kiya jata hai.
        doc = fitz.open(input_path)
        
        # Calculate optimal quality from level input
        # level jitna high hoga, pixel sampling threshold ko utna custom bound kiya jayega
        quality_factor = max(10, 100 - int(level))
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            image_list = page.get_images(full=True)
            
            for img in image_list:
                xref = img[0]
                base_image = doc.extract_image(xref)
                image_bytes = base_image["image"]
                
                # Compress individual embedded image streams with targeted quality parameters
                # Isse text and links save rahenge, par elements exact scale ho jayenge
                pix = fitz.Pixmap(doc, xref)
                compressed_img_bytes = pix.tobytes("jpeg", quality=quality_factor)
                
                # Replace the original high-size stream with the compressed block
                doc.update_stream(xref, compressed_img_bytes)
        
        # Save with garbage collection level 4 (Professional metadata tree deflate)
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
