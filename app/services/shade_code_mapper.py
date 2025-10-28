"""
Shade to Color Code Mapper
"""

SHADE_MAPPING = {
    "Natural Black": {"code": "1B", "tone": "Neutral", "description": "Natural black"},
    "Dark Brown": {"code": "2", "tone": "Neutral", "description": "Dark brown"},
    "Coffee Biscuit": {"code": "4", "tone": "Warm", "description": "Coffee brown"},
    "Coffee biscuit": {"code": "4", "tone": "Warm", "description": "Coffee brown"},
    "Cool Brown": {"code": "4", "tone": "Cool", "description": "Cool brown"},
    "Brown Soft Blended": {"code": "4", "tone": "Neutral", "description": "Soft brown blend"},
    "Medium Brown Balayage": {"code": "6", "tone": "Neutral", "description": "Medium brown balayage"},
    "Sandy Chocolate": {"code": "6", "tone": "Warm", "description": "Sandy chocolate brown"},
    "Dark Caramel Balayage": {"code": "6", "tone": "Warm", "description": "Dark caramel balayage"},
    "Natural Caramel": {"code": "6", "tone": "Warm", "description": "Natural caramel"},
    "Sunkissed Brown": {"code": "6", "tone": "Warm", "description": "Sunkissed brown"},
    "Autumn": {"code": "8", "tone": "Warm", "description": "Autumn brown"},
    "Copper": {"code": "8", "tone": "Warm", "description": "Copper"},
    "Copper_": {"code": "8", "tone": "Warm", "description": "Copper"},
    "Hot Toffee": {"code": "8", "tone": "Warm", "description": "Hot toffee"},
    "Hot toffee": {"code": "8", "tone": "Warm", "description": "Hot toffee"},
    "Rooted Golden Brown": {"code": "10", "tone": "Warm", "description": "Rooted golden brown"},
    "Old Money Blonde": {"code": "10", "tone": "Neutral", "description": "Old money blonde"},
    "Teddy Bear Blonde": {"code": "10", "tone": "Warm", "description": "Teddy bear blonde"},
    "Scandinavian Blonde": {"code": "12", "tone": "Neutral", "description": "Scandinavian blonde"},
    "Honey Blonde": {"code": "12", "tone": "Warm", "description": "Honey blonde"},
    "Mixed Blonde": {"code": "12", "tone": "Neutral", "description": "Mixed blonde"},
    "Luscious Blonde": {"code": "16", "tone": "Neutral", "description": "Luscious blonde"},
    "Summer Blonde": {"code": "16", "tone": "Warm", "description": "Summer blonde"},
    "Silver Blonde": {"code": "22", "tone": "Cool", "description": "Silver blonde"},
    "Silver blonde": {"code": "22", "tone": "Cool", "description": "Silver blonde"},
    "Champagne Blonde": {"code": "22", "tone": "Neutral", "description": "Champagne blonde"},
    "Platinum Blonde Balayage": {"code": "60", "tone": "Cool", "description": "Platinum blonde balayage"},
    "Platinum Blonde Balayage _CloseUp": {"code": "60", "tone": "Cool", "description": "Platinum blonde balayage"},
    "Ivory": {"code": "60", "tone": "Neutral", "description": "Ivory blonde"},
    "lvory": {"code": "60", "tone": "Neutral", "description": "Ivory blonde"},
    "Soft Blonde 'Old Money'": {"code": "12", "tone": "Neutral", "description": "Soft old money blonde"},
}

def get_color_code(shade_name):
    """Get color code for shade"""
    return SHADE_MAPPING.get(shade_name, {}).get("code", "N/A")

def get_tone_type(shade_name):
    """Get tone type for shade"""
    return SHADE_MAPPING.get(shade_name, {}).get("tone", "Neutral")

def get_description(shade_name):
    """Get description for shade"""
    return SHADE_MAPPING.get(shade_name, {}).get("description", shade_name)
