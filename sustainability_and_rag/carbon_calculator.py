import pandas as pd

# Standard Embodied Carbon Coefficients (kg CO2e per unit) based on ICE V3.0 / CPWD benchmarks
CARBON_DATABASE = {
    "concrete": {"cum": 300.0, "cu m": 300.0},
    "steel": {"kg": 2.89},
    "brick": {"cum": 180.0, "cu m": 180.0},
    "earthwork": {"cum": 5.0, "cu m": 5.0},
    "wood": {"sqm": 15.0, "sq m": 15.0},
    "formwork": {"sqm": 15.0, "sq m": 15.0},
    "bitumen": {"sqm": 25.0, "sq m": 25.0},
    "chemicals": {"sqm": 12.0, "sq m": 12.0},
    "waterproofing": {"sqm": 20.0, "sq m": 20.0},
    "pest control": {"sqm": 12.0, "sq m": 12.0}
}

def calculate_embodied_carbon(input_json_path: str) -> pd.DataFrame:
    """
    Multiplies material quantities by standard carbon emission factors 
    to generate A1-A3 embodied carbon metrics for the GMAP project.
    """
    print(f"Loading transformed data from {input_json_path}...")
    df = pd.read_json(input_json_path)
    
    carbon_records = []
    
    for _, row in df.iterrows():
        category = str(row['material_category']).lower().strip()
        # Normalize unit string: lowercase, remove periods, strip extra spaces
        unit = str(row['original_unit']).lower().replace(".", "").strip()
        qty = row['original_quantity']
        
        # Look up emission factor based on category and normalized unit
        category_factors = CARBON_DATABASE.get(category, {})
        emission_factor = category_factors.get(unit, 0.0)
        
        # Calculate total embodied carbon (A1-A3 lifecycle stage)
        total_co2e = round(qty * emission_factor, 2)
        
        record = row.to_dict()
        record['carbon_factor_used'] = emission_factor
        record['embodied_carbon_kg_co2e'] = total_co2e
        carbon_records.append(record)
        
    enriched_df = pd.DataFrame(carbon_records)
    return enriched_df

if __name__ == "__main__":
    input_file = "transformed_common_table.json"
    
    try:
        final_carbon_df = calculate_embodied_carbon(input_file)
        
        print("\n--- EMBODIED CARBON SUMMARY (74 ITEMS) ---")
        print(final_carbon_df[['boq_item_no', 'material_category', 'original_quantity', 'original_unit', 'embodied_carbon_kg_co2e']].head(15).to_string())
        
        # Grand total carbon footprint
        total_project_carbon = final_carbon_df['embodied_carbon_kg_co2e'].sum()
        print(f"\n[+] Total Estimated Embodied Carbon (A1-A3): {total_project_carbon:,.2f} kg CO2e")
        
        # Save final payload for the frontend API Gateway
        final_output = "gmap_final_enriched_payload.json"
        final_carbon_df.to_json(final_output, orient="records", indent=4)
        print(f"[+] Final fully-enriched pipeline payload saved to {final_output}")
        
    except Exception as e:
        print(f"Error: {e}")
        print("Make sure you ran material_classifier.py first!")