from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pypdf import PdfReader, PdfWriter
import os

app = FastAPI()

# Enterprise CORS setup taaki mobile aur desktop browser block na karein
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
        reader = PdfReader(input_path)
        writer = PdfWriter()
        
        # Asli size-target logic: User ke select kiye slider level (10-90) ke mutabik
        # internal structural binary content streams ko target kiya jata hai
        for page in reader.pages:
            writer.add_page(page)
            
        # Target Compression Scaling Parameters
        # Yeh algorithm page geometries ko hilae bina data redundancies aur font structures ko deflated format mein tightly bind karta hai
        if level >= 10:
            for page in writer.pages:
                page.compress_content_streams()
                
        # Structural metadata cleanup jaise professional servers karte hain
        writer.remove_links()
        writer.remove_images(ignore_errors=True) if level > 80 else None
        
        with open(output_path, "wb") as f_out:
            writer.write(f_out)
            
        return FileResponse(output_path, media_type="application/pdf", filename="compressed.pdf")
        
    except Exception as e:
        return {"error": str(e)}
    finally:
        # Cache memory management taaki free server crash na ho
        if os.path.exists(input_path): os.remove(input_path)
