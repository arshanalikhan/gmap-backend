import os
from google import genai
from pydantic import BaseModel, Field

# 1. Define the strict output schema
class BOQItem(BaseModel):
    boq_item_no: str = Field(description="The original item number from the text (e.g., '1.1', '2a')")
    description: str = Field(description="The cleaned material description without OCR garbage")
    material_category: str = Field(description="Broad category e.g., 'Concrete', 'Earthwork', 'Steel'")
    original_quantity: float = Field(description="Extracted numerical quantity")
    original_unit: str = Field(description="Extracted unit of measurement (e.g., 'sqm', 'cum', 'kg')")

# 2. We expect a list of items back from the chunk
class BOQParsedChunk(BaseModel):
    items: list[BOQItem]

def parse_with_gemini(prompt: str) -> list[BOQItem]:
    """
    Sends the markdown prompt to Gemini Flash and forces a structured Pydantic response.
    """
    # The client automatically picks up the GEMINI_API_KEY environment variable
    client = genai.Client()
    
    print("Routing chunk to Gemini Flash...")
    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=prompt,
        config={
            "response_mime_type": "application/json",
            "response_schema": BOQParsedChunk,
            "temperature": 0.1 # Keep it low for deterministic engineering data
        },
    )
    
    return response.parsed.items

if __name__ == "__main__":
    # Quick test to see if the API key and client are working
    test_prompt = """
    Parse this dummy BOQ data:
    | Item No | Description | Qty | Unit |
    |---|---|---|---|
    | 4.1 | Reinforced Cement Concrete M25 | 150 | cum |
    """
    try:
        results = parse_with_gemini(test_prompt)
        for item in results:
            print(f"Successfully extracted: Item {item.boq_item_no} - {item.material_category} ({item.original_quantity} {item.original_unit})")
    except Exception as e:
        print(f"API Error: {e}")
        print("Did you remember to set your GEMINI_API_KEY in the terminal?")