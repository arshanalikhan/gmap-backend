import pandas as pd
import re

def classify_and_normalize_materials(json_input_path: str) -> pd.DataFrame:
    """
    Reads the JSON payload from Layer 2, extracts mix ratios and concrete grades,
    and standardizes them for sustainability database matching.
    """
    print(f"Loading data from {json_input_path}...")
    df = pd.read_json(json_input_path)
    
    normalized_rows = []
    
    for _, row in df.iterrows():
        desc = row['description']
        category = row['material_category']
        
        # Default standard grade
        grade = "Standard"
        
        # Deterministic Regex to extract mix ratios (e.g., 1:2:4, 1:5:10)
        mix_match = re.search(r'1\s*:\s*([0-9\.]+)\s*:\s*([0-9\.]+)', desc)
        if mix_match:
            grade = f"Mix 1:{mix_match.group(1)}:{mix_match.group(2)}"
        
        # Check for explicit concrete grades (e.g., M25, M15)
        grade_match = re.search(r'\b(M\d{1,2})\b', desc, re.IGNORECASE)
        if grade_match:
            grade = grade_match.group(1).upper()
            
        # Add enriched fields
        normalized_row = row.to_dict()
        normalized_row['structural_grade'] = grade
        normalized_rows.append(normalized_row)
        
    enriched_df = pd.DataFrame(normalized_rows)
    return enriched_df

if __name__ == "__main__":
    # Test the classifier using the JSON output we just generated
    input_file = "common_table_output.json"
    
    try:
        result_df = classify_and_normalize_materials(input_file)
        print("\n--- CLASSIFIED MATERIALS SAMPLE ---")
        print(result_df[['boq_item_no', 'material_category', 'structural_grade', 'original_unit']].head(10).to_string())
        
        # Save the transformed table
        output_path = "transformed_common_table.json"
        result_df.to_json(output_path, orient="records", indent=4)
        print(f"\n[+] Data transformation complete! Saved to {output_path}")
        
    except Exception as e:
        print(f"Error: {e}")
        print("Make sure you run chunking_manager.py first to generate common_table_output.json!")