from paddleocr import PaddleOCR
import pandas as pd
import fitz  # PyMuPDF for rendering PDF pages to images
import cv2
import numpy as np

def extract_scanned_boq(pdf_path: str) -> pd.DataFrame:
    """
    Renders a scanned PDF to images and uses PaddleOCR to extract text blocks.
    Note: Full table reconstruction from OCR requires geometric matching of bounding boxes.
    """
    print(f"Initializing OCR for: {pdf_path}")
    # Initialize PaddleOCR (English language, layout analysis enabled)
    ocr = PaddleOCR(use_angle_cls=True, lang='en', show_log=False)
    
    doc = fitz.open(pdf_path)
    raw_extracted_text = []
    
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        # Render page to a high-resolution image matrix
        pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
        img = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, pix.n)
        
        # Convert RGB to BGR for OpenCV processing
        if pix.n == 3:
            img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
            
        # Run PaddleOCR inference
        result = ocr.ocr(img, cls=True)
        
        # Extract the text strings and bounding boxes
        for line in result[0]:
            bbox = line[0]     # [ [x,y], [x,y], [x,y], [x,y] ]
            text = line[1][0]  # The actual recognized string
            confidence = line[1][1]
            
            raw_extracted_text.append({
                "Page": page_num + 1,
                "Text": text,
                "Confidence": round(confidence, 2),
                "Y_Coordinate": bbox[0][1] # Used later for row-alignment
            })
            
    df = pd.DataFrame(raw_extracted_text)
    
    # In a production environment, you would sort by Y_Coordinate 
    # to reconstruct the rows of the BOQ table here.
    return df

if __name__ == "__main__":
    # Test execution
    # df_scan = extract_scanned_boq("scanned_boq.pdf")
    # print(df_scan.head())
    pass