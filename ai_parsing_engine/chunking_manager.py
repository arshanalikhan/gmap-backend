import pandas as pd
import time
from memory_bridge import dataframe_to_markdown_chunk
from llm_router import parse_with_gemini

def process_boq_dataframe(df: pd.DataFrame, batch_size: int = 7) -> pd.DataFrame:
    """
    Slices a large DataFrame into micro-batches, sends them to Gemini, 
    and handles state/rate limits.
    """
    total_rows = len(df)
    all_parsed_items = []
    
    print(f"Starting pipeline: {total_rows} items in micro-batches of {batch_size}.")
    
    for start_idx in range(0, total_rows, batch_size):
        end_idx = min(start_idx + batch_size, total_rows)
        print(f"Processing batch {start_idx} to {end_idx}...")
        
        # 1. Convert to Markdown Prompt
        prompt = dataframe_to_markdown_chunk(df, start_idx, end_idx)
        
        try:
            # 2. Send to Gemini Router
            parsed_batch = parse_with_gemini(prompt)
            
            # 3. Convert Pydantic objects back to dicts for our final DataFrame
            for item in parsed_batch:
                all_parsed_items.append(item.model_dump())
            
            # 4. Rate limit buffer (simple sleep to avoid 429 errors)
            time.sleep(2) 
            
        except Exception as e:
            print(f"[!] Error on batch {start_idx}-{end_idx}: {e}")
            print("State saved. Ready to resume.")
            break
            
    # Assemble the final Common Table
    common_table_df = pd.DataFrame(all_parsed_items)
    return common_table_df

if __name__ == "__main__":
    import sys
    
    # Example usage: Pass a real Excel or CSV file path from your terminal
    # e.g., py ai_parsing_engine/chunking_manager.py path/to/real_boq.xlsx
    
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
        print(f"Loading real file: {file_path}")
        
        # Load based on file extension
        if file_path.endswith('.csv'):
            real_df = pd.read_csv(file_path)
        elif file_path.endswith(('.xls', '.xlsx')):
            real_df = pd.read_excel(file_path)
        else:
            raise ValueError("Unsupported file format. Please provide a CSV or Excel file.")
            
        # Run the full pipeline on your real data
        final_common_table = process_boq_dataframe(real_df, batch_size=7)
        
        # Save the result to a clean JSON payload for the database / frontend
        output_json = "common_table_output.json"
        final_common_table.to_json(output_json, orient="records", indent=4)
        print(f"\n[+] Pipeline complete! Saved unified payload to {output_json}")
        
    else:
        print("Please provide a file path as an argument.")
        print("Example: py ai_parsing_engine/chunking_manager.py sample_boq.xlsx")