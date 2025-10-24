import json
import numpy as np
from pathlib import Path

def merge_shade_variants(shades_data):
    """Merge all variants of same shade into one"""
    merged = {}
    
    # Group by base shade name (remove _CloseUp, _IndoorLight, etc.)
    shade_groups = {}
    for shade_name, colors in shades_data.items():
        # Extract base name
        base_name = shade_name.replace("_CloseUp", "").replace("_IndoorLight", "").replace("_NaturalLight", "").replace("_light", "")
        
        if base_name not in shade_groups:
            shade_groups[base_name] = []
        
        shade_groups[base_name].extend(colors)
    
    # Merge colors for each shade
    for base_name, all_colors in shade_groups.items():
        print(f"Merging: {base_name} ({len(all_colors)} color groups)")
        
        merged_colors = []
        
        for color in all_colors:
            rgb = color["color"]
            pct = color["percentage"]
            tone = color["tone"]
            
            # Find similar color to merge
            found = False
            for existing in merged_colors:
                dist = np.sqrt(sum((a - b) ** 2 for a, b in zip(rgb, existing["color"])))
                
                # Merge if similar RGB and same tone
                if dist < 30 and existing["tone"] == tone:
                    # Weighted average
                    total = existing["percentage"] + pct
                    for i in range(3):
                        existing["color"][i] = int((existing["color"][i] * existing["percentage"] + rgb[i] * pct) / total)
                    existing["percentage"] = total
                    existing["brightness"] = (existing["brightness"] * existing["percentage"] + color["brightness"] * pct) / total
                    existing["hue"] = (existing["hue"] * existing["percentage"] + color["hue"] * pct) / total
                    existing["saturation"] = (existing["saturation"] * existing["percentage"] + color["saturation"] * pct) / total
                    found = True
                    break
            
            if not found:
                merged_colors.append(color.copy())
        
        # Normalize percentages
        total = sum(c["percentage"] for c in merged_colors)
        if total > 0:
            for c in merged_colors:
                c["percentage"] = round((c["percentage"] / total) * 100, 2)
                c["brightness"] = round(c["brightness"], 2)
                c["hue"] = round(c["hue"], 2)
                c["saturation"] = round(c["saturation"], 3)
        
        # Sort and keep top 3
        merged_colors.sort(key=lambda x: x["percentage"], reverse=True)
        merged[base_name] = merged_colors[:3]
        
        print(f"  Final: {len(merged[base_name])} colors")
        for c in merged[base_name]:
            print(f"    RGB{c['color']} - {c['tone']} ({c['percentage']}%)")
    
    return merged

def main():
    print("Merging shade variants into single database...\n")
    
    # Load current database
    input_path = Path("app/shade/perfect_shades.json")
    if not input_path.exists():
        print(f"[ERROR] {input_path} not found!")
        return
    
    with open(input_path, 'r') as f:
        shades_data = json.load(f)
    
    print(f"Loaded {len(shades_data)} shade variants\n")
    
    # Merge variants
    merged = merge_shade_variants(shades_data)
    
    # Save merged database
    output_path = Path("app/shade/merged_shades.json")
    with open(output_path, 'w') as f:
        json.dump(merged, f, indent=2)
    
    print(f"\n[OK] Created merged database with {len(merged)} shades")
    print(f"[OK] Saved to: {output_path}")

if __name__ == "__main__":
    main()
