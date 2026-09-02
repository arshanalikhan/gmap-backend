import ifcopenshell
import ifcopenshell.util.element
import pandas as pd
import json

def parse_ifc_model(file_path: str) -> pd.DataFrame:
    """
    Extracts physical elements and their base quantities from an IFC file.
    """
    print(f"Loading IFC Model: {file_path}")
    model = ifcopenshell.open(file_path)
    
    extracted_data = []
    
    # Target common structural elements
    element_types = ["IfcWall", "IfcSlab", "IfcColumn", "IfcBeam"]
    
    for ifc_type in element_types:
        elements = model.by_type(ifc_type)
        
        for element in elements:
            # Get spatial container (e.g., Level 1, Ground Floor)
            container = ifcopenshell.util.element.get_container(element)
            floor_name = container.Name if container else "Unknown Level"
            
            # Fetch all Property Sets (Psets) and Quantity Sets (Qsets)
            psets = ifcopenshell.util.element.get_psets(element)
            
            # Look specifically for BaseQuantities (Standard IFC geometry data)
            quantities = psets.get("Qto_WallBaseQuantities") or psets.get("Qto_SlabBaseQuantities") or psets.get("Qto_ColumnBaseQuantities") or {}
            
            # Extract key metrics safely
            volume = quantities.get("NetVolume")
            area = quantities.get("NetArea") or quantities.get("NetSideArea")
            
            extracted_data.append({
                "GlobalId": element.GlobalId,
                "ElementType": ifc_type,
                "ElementName": element.Name or "Unnamed",
                "Floor": floor_name,
                "Volume_m3": volume,
                "Area_m2": area
            })
            
    # Convert to an in-memory DataFrame
    df = pd.DataFrame(extracted_data)
    print(f"Extracted {len(df)} elements.")
    return df

if __name__ == "__main__":
    # Test execution
    # df_ifc = parse_ifc_model("sample_building.ifc")
    # print(df_ifc.head())
    pass