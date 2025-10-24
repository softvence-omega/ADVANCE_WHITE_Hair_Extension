"""
Map custom shade names to standard color codes based on tone, brightness, hue
"""

SHADE_TO_CODE_MAP = {
    # Black Series
    "Natural Black": "1B",
    
    # Brown Series
    "Dark Brown": "2",
    "Cool Brown": "2",
    "Coffee biscuit": "4",
    "Coffee Biscuit": "4",
    "Medium Brown Balayage": "4",
    "Brown Soft Blended": "4",
    "Sandy Chocolate": "6",
    "Sunkissed Brown": "6",
    "Natural Caramel": "6",
    "Autumn": "6",
    "Hot Toffee": "8",
    "Hot toffee": "8",
    
    # Blonde Series - Dark to Medium
    "Dark Caramel Balayage": "10",
    "Rooted Golden Brown": "10",
    "Teddy Bear Blonde": "12",
    "Scandinavian Blonde": "12",
    "Old Money Blonde": "12",
    "Soft Blonde 'Old Money'": "12",
    "Mixed Blonde": "16",
    "Honey Blonde": "16",
    "Summer Blonde": "16",
    
    # Blonde Series - Light
    "Luscious Blonde": "22",
    "Champagne Blonde": "22",
    "lvory": "22",
    "Ivory": "22",
    
    # Platinum/Ash Series
    "Platinum Blonde Balayage": "60",
    "Silver blonde": "60",
    "Silver Blonde": "60",
}

def get_color_code(shade_name):
    """Get standard color code for a shade name"""
    # Remove variant suffix if present
    base_name = shade_name.split("_")[0] if "_" in shade_name else shade_name
    return SHADE_TO_CODE_MAP.get(base_name, "Unknown")

def get_tone_type(shade_name):
    """Determine tone type based on shade characteristics"""
    base_name = shade_name.split("_")[0] if "_" in shade_name else shade_name
    
    # Cool tones
    cool_shades = ["Natural Black", "Cool Brown", "Silver Blonde", "Silver blonde", 
                   "Platinum Blonde Balayage", "Champagne Blonde", "Ivory", "lvory"]
    
    # Warm tones
    warm_shades = ["Dark Brown", "Sandy Chocolate", "Sunkissed Brown", "Natural Caramel",
                   "Autumn", "Hot Toffee", "Hot toffee", "Dark Caramel Balayage",
                   "Rooted Golden Brown", "Mixed Blonde", "Honey Blonde", "Summer Blonde"]
    
    # Neutral tones
    neutral_shades = ["Coffee biscuit", "Coffee Biscuit", "Medium Brown Balayage",
                      "Brown Soft Blended", "Teddy Bear Blonde", "Scandinavian Blonde",
                      "Old Money Blonde", "Soft Blonde 'Old Money'", "Luscious Blonde"]
    
    if base_name in cool_shades:
        return "Cool"
    elif base_name in warm_shades:
        return "Warm"
    elif base_name in neutral_shades:
        return "Neutral"
    else:
        return "Neutral"

def get_description(shade_name):
    """Get description for shade"""
    base_name = shade_name.split("_")[0] if "_" in shade_name else shade_name
    
    descriptions = {
        "Natural Black": "Soft natural black with brown undertone",
        "Dark Brown": "Dark espresso brown",
        "Cool Brown": "Muted grey-brown undertone",
        "Coffee biscuit": "Rich coffee with biscuit warmth",
        "Coffee Biscuit": "Rich coffee with biscuit warmth",
        "Medium Brown Balayage": "Balanced mid-brown with highlights",
        "Brown Soft Blended": "Soft blended brown tones",
        "Sandy Chocolate": "Light brown with golden undertone",
        "Sunkissed Brown": "Sun-kissed warm brown",
        "Natural Caramel": "Natural caramel warmth",
        "Autumn": "Warm autumn brown tones",
        "Hot Toffee": "Reddish-brown, rich and glossy",
        "Hot toffee": "Reddish-brown, rich and glossy",
        "Dark Caramel Balayage": "Dark brown with caramel highlights",
        "Rooted Golden Brown": "Golden brown with darker roots",
        "Teddy Bear Blonde": "Soft brown-blonde mix",
        "Scandinavian Blonde": "Muted golden beige",
        "Old Money Blonde": "Classic elegant blonde",
        "Soft Blonde 'Old Money'": "Soft elegant blonde tone",
        "Mixed Blonde": "Honey-golden finish",
        "Honey Blonde": "Honey-golden finish",
        "Summer Blonde": "Sun-kissed blonde warmth",
        "Luscious Blonde": "Neutral pale blonde tone",
        "Champagne Blonde": "Neutral pale champagne tone",
        "lvory": "Neutral pale ivory tone",
        "Ivory": "Neutral pale ivory tone",
        "Platinum Blonde Balayage": "Icy platinum with dimension",
        "Silver blonde": "Frosty metallic shade",
        "Silver Blonde": "Frosty metallic shade",
    }
    
    return descriptions.get(base_name, "Beautiful hair shade")
