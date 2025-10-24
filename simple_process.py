import os
from pathlib import Path
from app.services.data_annotator import HairDataAnnotator
import json

def main():
    print("Processing all hair data folders...")
    
    folders = ["data", "new_data", "new_shade", "New4_Data"]
    all_results = {}
    annotator = HairDataAnnotator()
    
    for folder in folders:
        folder_path = Path(folder)
        if not folder_path.exists():
            print(f"Folder not found: {folder}")
            continue
        
        print(f"\nProcessing folder: {folder}")
        
        # Check if folder contains subdirectories or direct images
        subdirs = [d for d in folder_path.iterdir() if d.is_dir()]
        
        if subdirs:
            # Process as shade directories
            result = annotator.annotate_all_data(folder, f"{folder}_shades.json")
        else:
            # Process as single shade folder
            colors = annotator.process_shade_directory(folder_path, folder)
            if colors:
                result = {folder: colors}
            else:
                result = None
        
        if result:
            all_results.update(result)
            print(f"Successfully processed {folder}")
        else:
            print(f"No data extracted from {folder}")
    
    # Save final database
    if all_results:
        final_path = Path("app/shade/perfect_shades.json")
        final_path.parent.mkdir(exist_ok=True)
        
        with open(final_path, 'w') as f:
            json.dump(all_results, f, indent=2)
        
        print(f"\nPerfect database created: {final_path}")
        print(f"Total shades: {len(all_results)}")
        
        for shade_name, colors in all_results.items():
            print(f"  {shade_name}: {len(colors)} colors")
    else:
        print("\nNo data processed. Check your folders.")

if __name__ == "__main__":
    main()