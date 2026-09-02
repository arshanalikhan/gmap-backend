import pdfplumber
import pandas as pd

def extract_digital_boq(pdf_path: str) -> pd.DataFrame:
    """
    Extracts tabular data from a digital PDF and returns a consolidated DataFrame.
    """
    print(f"Extracting tables from: {pdf_path}")
    all_tables = []
    
    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages):
            # Extract tables using visual gridlines and text spacing
            tables = page.extract_tables()
            
            for table in tables:
                if not table:
                    continue
                    
                # Clean up None values that occur from merged cells
                cleaned_table = [[cell if cell is not None else "" for cell in row] for row in table]
                
                # Assume the first row of the first page is the header
                if page_num == 0 and len(all_tables) == 0:
                    df = pd.DataFrame(cleaned_table[1:], columns=cleaned_table[0])
                else:
                    # For continuation pages, drop the header if it repeats
                    if cleaned_table[0] == all_tables[0].columns.tolist():
                        df = pd.DataFrame(cleaned_table[1:], columns=all_tables[0].columns)
                    else:
                        df = pd.DataFrame(cleaned_table)
                        
                all_tables.append(df)
                
    if all_tables:
        final_df = pd.concat(all_tables, ignore_index=True)
        # Clean newline characters from extracted text
        final_df = final_df.replace('\n', ' ', regex=True)
        return final_df
    else:
        print("No tables detected.")
        return pd.DataFrame()

if __name__ == "__main__":
    # Test execution
    # df_boq = extract_digital_boq("digital_boq.pdf")
    # print(df_boq.head())
    pass