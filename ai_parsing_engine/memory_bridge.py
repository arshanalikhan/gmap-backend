import pandas as pd

def dataframe_to_markdown_chunk(df: pd.DataFrame, start_idx: int, end_idx: int) -> str:
    """
    Slices a DataFrame and converts it to a Markdown table string 
    for highly token-efficient LLM prompts.
    """
    # Slice the dataframe based on the batch size
    chunk = df.iloc[start_idx:end_idx]
    
    # Convert to markdown, omitting the dataframe index
    markdown_table = chunk.to_markdown(index=False)
    
    prompt = f"""
Parse the following raw BOQ tabular data and map it to our standard JSON schema.
Ensure all dimensions, materials, and quantities are accurately extracted.

RAW DATA:
{markdown_table}
"""
    return prompt