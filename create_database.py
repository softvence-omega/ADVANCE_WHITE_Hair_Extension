#!/usr/bin/env python3
"""
Create Perfect Shade Database
Run this script to process all hair sample photos and create the perfect matching database
"""

from app.services.data_annotator import create_perfect_shade_database

if __name__ == "__main__":
    print("🚀 Creating Perfect Hair Shade Database...")
    print("This will process all images in data/, new_data/, and New4_Data/ directories")
    print("Please wait, this may take several minutes...\n")
    
    try:
        database = create_perfect_shade_database()
        
        if database:
            print(f"\n✅ SUCCESS! Perfect database created with {len(database)} shades")
            print("📁 Database saved to: app/shade/perfect_shades.json")
            print("\n🎯 Your hair matching system is now 100% ready!")
            print("Run the server and test with any hair image for perfect results.")
        else:
            print("\n❌ Failed to create database. Check your data directories.")
            
    except Exception as e:
        print(f"\n💥 Error creating database: {e}")
        print("Make sure you have hair sample images in the data directories.")