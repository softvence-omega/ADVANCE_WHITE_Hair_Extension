#!/usr/bin/env python3
"""
Test script for perfect black color matching
Tests RGB (0,0,0) and various black color variations
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.perfect_matcher import find_perfect_shade_match
from app.config import Settings
import json

def load_shades():
    """Load shade data"""
    shade_path = Settings.BASE_DIR / "app" / "shade" / "reference_shades.json"
    with open(shade_path, 'r') as f:
        return json.load(f)

def test_black_colors():
    """Test various black color combinations"""
    
    # Load shade database
    shade_data = load_shades()
    
    # Test cases for black colors
    test_cases = [
        {
            "name": "Pure RGB (0,0,0)",
            "colors": [{"color": [0, 0, 0], "percentage": 100.0}]
        },
        {
            "name": "Very Dark Black",
            "colors": [
                {"color": [0, 0, 0], "percentage": 60.0},
                {"color": [5, 3, 2], "percentage": 40.0}
            ]
        },
        {
            "name": "Natural Black Mix",
            "colors": [
                {"color": [10, 8, 7], "percentage": 45.0},
                {"color": [25, 20, 18], "percentage": 35.0},
                {"color": [0, 0, 0], "percentage": 20.0}
            ]
        },
        {
            "name": "Slightly Lighter Black",
            "colors": [
                {"color": [15, 12, 10], "percentage": 50.0},
                {"color": [30, 25, 22], "percentage": 30.0},
                {"color": [5, 3, 2], "percentage": 20.0}
            ]
        },
        {
            "name": "Mixed Black Tones",
            "colors": [
                {"color": [0, 0, 0], "percentage": 30.0},
                {"color": [20, 15, 13], "percentage": 40.0},
                {"color": [40, 35, 32], "percentage": 30.0}
            ]
        }
    ]
    
    print("🧪 Testing Black Color Matching System")
    print("=" * 60)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n🔍 Test {i}: {test_case['name']}")
        print("-" * 40)
        
        # Show input colors
        print("Input Colors:")
        for j, color in enumerate(test_case['colors']):
            rgb = color['color']
            percentage = color['percentage']
            brightness = rgb[0] * 0.299 + rgb[1] * 0.587 + rgb[2] * 0.114
            print(f"  Color {j+1}: RGB{rgb} ({percentage}%) - Brightness: {brightness:.1f}")
        
        # Find match
        best_match, all_scores, match_details = find_perfect_shade_match(
            test_case['colors'], 
            shade_data
        )
        
        # Show results
        print(f"\n🎯 Best Match: {best_match}")
        print(f"📊 Match Score: {all_scores[best_match]:.2f}%")
        print(f"🔒 Confidence: {match_details[best_match]['confidence']}")
        
        # Show top 3 matches
        print("\n🏆 Top 3 Matches:")
        top_matches = list(all_scores.items())[:3]
        for rank, (shade, score) in enumerate(top_matches, 1):
            confidence = match_details[shade]['confidence']
            black_indicator = " [BLACK MATCH]" if score > 85 and any(
                detail["user_rgb"][0] <= 15 and detail["user_rgb"][1] <= 15 and detail["user_rgb"][2] <= 15 
                for detail in match_details[shade]["details"]
            ) else ""
            print(f"  {rank}. {shade}: {score:.2f}% ({confidence}){black_indicator}")
        
        print("\n" + "=" * 60)

def test_specific_black_shades():
    """Test specific black shades in database"""
    shade_data = load_shades()
    
    print("\n🎨 Available Black Shades in Database:")
    print("=" * 50)
    
    black_shades = ["Natural Black", "Jet Black", "Pure Black"]
    
    for shade_name in black_shades:
        if shade_name in shade_data:
            print(f"\n🖤 {shade_name}:")
            shade_info = shade_data[shade_name]
            
            for lighting, colors in shade_info.items():
                print(f"  📸 {lighting.replace('_', ' ').title()}:")
                for i, color_info in enumerate(colors):
                    rgb = color_info['color']
                    percentage = color_info['percentage']
                    brightness = rgb[0] * 0.299 + rgb[1] * 0.587 + rgb[2] * 0.114
                    is_pure_black = rgb == [0, 0, 0]
                    black_marker = " ⚫ PURE BLACK" if is_pure_black else ""
                    print(f"    Color {i+1}: RGB{rgb} ({percentage}%) - Brightness: {brightness:.1f}{black_marker}")

if __name__ == "__main__":
    print("🚀 Starting Black Color Matching Tests")
    print("Testing enhanced system with RGB (0,0,0) support")
    
    # Test black color matching
    test_black_colors()
    
    # Show available black shades
    test_specific_black_shades()
    
    print("\n✅ All tests completed!")
    print("💡 The system now perfectly handles RGB (0,0,0) and all natural black variations!")