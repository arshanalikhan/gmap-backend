import os
import sys
from google import genai
from pydantic import BaseModel, Field

class BOQItem(BaseModel):
    boq_item_no: str = Field(description="The original item number from the text (e.g., '1.1', '2a')")
    description: str = Field(description="The cleaned material description")
    material_category: str = Field(description="Broad category e.g., 'Concrete', 'Earthwork', 'Steel', 'Brick'")
    original_quantity: float = Field(description="Extracted numerical quantity")
    original_unit: str = Field(description="Extracted unit of measurement (e.g., 'sqm', 'cum', 'kg', 'm')")

class BOQExtractionPayload(BaseModel):
    items: list[BOQItem]

def parse_boq_pdf_with_gemini(pdf_path: str):
    """
    Uploads a scanned or digital BOQ PDF directly to Gemini 3.6-flash 
    and forces a structured Pydantic response containing all line items.
    """
    client = genai.Client()
    
    print(f"Uploading and processing PDF via Gemini API: {pdf_path}...")
    
    # 1. Upload the PDF file using the GenAI Files API
    uploaded_file = client.files.upload(file=pdf_path)
    
    # 2. Prompt Gemini to analyze the document and conform to our schema
    prompt = """
    Analyze this Bill of Quantities (BOQ) document carefully. 
    Extract all line items, including their item numbers, full material descriptions, 
    material categories, numerical quantities, and units of measurement.
    """
    
    print("Sending document to Gemini 3.6-flash for structured extraction...")
    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=[uploaded_file, prompt],
        config={
            "response_mime_type": "application/json",
            "response_schema": BOQExtractionPayload,
            "temperature": 0.1
        }
    )
    
    # 3. Clean up the remote file after processing
    client.files.delete(name=uploaded_file.name)
    
    return response.parsed.items

if __name__ == "__main__":
    if len(sys.argv) > 1:
        pdf_file = sys.argv[1]
        try:
            items = parse_boq_pdf_with_gemini(pdf_file)
            
            # Convert extracted Pydantic objects to dictionary records
            records = [item.model_dump() for item in items]
            
            # Save directly as the common table output for downstream layers
            import pandas as pd
            df = pd.DataFrame(records)
            output_json = "common_table_output.json"
            df.to_json(output_json, orient="records", indent=4)
            
            print(f"\n[+] Successfully extracted {len(records)} items from PDF!")
            print(f"[+] Saved structured payload to {output_json}")
            
        except Exception as e:
            print(f"[-] Error processing PDF: {e}")
    else:
        print("Please provide a PDF path.")