#!/usr/bin/env python3
"""
Process all hair data folders: data, new_data, new_shade, New4_Data
"""

import os
from pathlib import Path
from app.services.data_annotator import HairDataAnnotator
import json

def process_single_folder(folder_name):
    """Process a single data folder"""
    folder_path = Path(folder_name)
    if not folder_path.exists():
        print(f"❌ Folder not found: {folder_name}")
        return None
    
    print(f"\n📁 Processing folder: {folder_name}")
    annotator = HairDataAnnotator()
    
    # Check if folder contains subdirectories (shade folders) or direct images
    subdirs = [d for d in folder_path.iterdir() if d.is_dir()]
    
    if subdirs:
        # Process as shade directories
        result = annotator.annotate_all_data(folder_name, f"{folder_name}_shades.json")
    else:
        # Process as single shade folder
        colors = annotator.process_shade_directory(folder_path, folder_name)
        if colors:
            result = {folder_name: colors}
            # Save individual result
            output_path = Path("app/shade") / f"{folder_name}_single.json"
            output_path.parent.mkdir(exist_ok=True)
            with open(output_path, 'w') as f:
                json.dump(result, f, indent=2)
        else:
            result = None
    
    return result

def main():
    """Process all data folders"""
    print("🚀 Processing all hair data folders...")
    
    folders = ["data", "new_data", "new_shade", "New4_Data"]
    all_results = {}
    
    for folder in folders:
        result = process_single_folder(folder)
        if result:
            all_results.update(result)
            print(f"✅ Successfully processed {folder}")
        else:
            print(f"⚠️ No data extracted from {folder}")
    
    # Combine all results
    if all_results:
        final_path = Path("app/shade/perfect_shades.json")
        final_path.parent.mkdir(exist_ok=True)
        
        with open(final_path, 'w') as f:
            json.dump(all_results, f, indent=2)
        
        print(f"\n🎉 Perfect database created: {final_path}")
        print(f"📊 Total shades: {len(all_results)}")
        
        # Show summary
        print("\n📋 Shade Summary:")
        for shade_name, colors in all_results.items():
            print(f"  • {shade_name}: {len(colors)} colors")
    else:
        print("\n❌ No data processed. Check your folders.")

if __name__ == "__main__":
    main()