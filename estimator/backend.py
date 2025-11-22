"""
Food Analysis Backend with Food-101 Dataset Integration
Supports food recognition using Food-101 dataset classes
"""

import json
import os
import random
import base64
import hashlib
import sys
from datetime import datetime
from pathlib import Path

from flask import Flask, jsonify, request
from flask_cors import CORS

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    print("Warning: OpenAI library not installed. Install with: pip install openai")

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
DATA_FILE = DATA_DIR / "analyses.json"
CACHE_FILE = DATA_DIR / "image_cache.json"
FOOD101_META_FILE = DATA_DIR / "food101_meta.json"
PORT = int(os.environ.get("PORT", 4000))

# Food-101 Dataset Classes (101 food categories)
FOOD101_CLASSES = [
    "apple_pie", "baby_back_ribs", "baklava", "beef_carpaccio", "beef_tartare",
    "beet_salad", "beignets", "bibimbap", "bread_pudding", "breakfast_burrito",
    "bruschetta", "caesar_salad", "cannoli", "caprese_salad", "carrot_cake",
    "ceviche", "cheesecake", "cheese_plate", "chicken_curry", "chicken_quesadilla",
    "chicken_wings", "chocolate_cake", "chocolate_mousse", "churros", "clam_chowder",
    "club_sandwich", "crab_cakes", "creme_brulee", "croque_madame", "cup_cakes",
    "deviled_eggs", "donuts", "eggs_benedict", "escargots", "falafel",
    "filet_mignon", "fish_and_chips", "foie_gras", "french_fries", "french_onion_soup",
    "french_toast", "fried_calamari", "fried_rice", "frozen_yogurt", "garlic_bread",
    "gnocchi", "greek_salad", "grilled_cheese_sandwich", "grilled_salmon", "guacamole",
    "gyoza", "hamburger", "hot_and_sour_soup", "hot_dog", "huevos_rancheros",
    "hummus", "ice_cream", "lasagna", "lobster_bisque", "lobster_roll_sandwich",
    "macaroni_and_cheese", "macarons", "miso_soup", "mussels", "nachos",
    "omelette", "onion_rings", "oysters", "pad_thai", "paella",
    "pancakes", "panna_cotta", "peking_duck", "pho", "pizza",
    "pork_chop", "poutine", "prime_rib", "pulled_pork_sandwich", "ramen",
    "ravioli", "red_velvet_cake", "risotto", "samosa", "sashimi",
    "scallops", "seaweed_salad", "shrimp_and_grits", "spaghetti_bolognese", "spaghetti_carbonara",
    "spring_rolls", "steak", "strawberry_shortcake", "sushi", "tacos",
    "takoyaki", "tiramisu", "tuna_tartare", "waffles"
]

# Map Food-101 classes to simplified food names for nutrition calculation
FOOD101_TO_SIMPLE = {
    "apple_pie": "apple", "baby_back_ribs": "chicken", "baklava": "bread",
    "beef_carpaccio": "chicken", "beef_tartare": "chicken", "beet_salad": "salad",
    "beignets": "bread", "bibimbap": "rice", "bread_pudding": "bread",
    "breakfast_burrito": "bread", "bruschetta": "bread", "caesar_salad": "salad",
    "cannoli": "bread", "caprese_salad": "salad", "carrot_cake": "bread",
    "ceviche": "fish", "cheesecake": "cheese", "cheese_plate": "cheese",
    "chicken_curry": "chicken", "chicken_quesadilla": "chicken", "chicken_wings": "chicken",
    "chocolate_cake": "bread", "chocolate_mousse": "milk", "churros": "bread",
    "clam_chowder": "soup", "club_sandwich": "bread", "crab_cakes": "fish",
    "creme_brulee": "milk", "croque_madame": "bread", "cup_cakes": "bread",
    "deviled_eggs": "egg", "donuts": "bread", "eggs_benedict": "egg",
    "escargots": "fish", "falafel": "vegetables", "filet_mignon": "chicken",
    "fish_and_chips": "fish", "foie_gras": "chicken", "french_fries": "potato",
    "french_onion_soup": "soup", "french_toast": "bread", "fried_calamari": "fish",
    "fried_rice": "rice", "frozen_yogurt": "yogurt", "garlic_bread": "bread",
    "gnocchi": "pasta", "greek_salad": "salad", "grilled_cheese_sandwich": "bread",
    "grilled_salmon": "fish", "guacamole": "vegetables", "gyoza": "noodles",
    "hamburger": "bread", "hot_and_sour_soup": "soup", "hot_dog": "bread",
    "huevos_rancheros": "egg", "hummus": "vegetables", "ice_cream": "milk",
    "lasagna": "pasta", "lobster_bisque": "soup", "lobster_roll_sandwich": "fish",
    "macaroni_and_cheese": "pasta", "macarons": "bread", "miso_soup": "soup",
    "mussels": "fish", "nachos": "bread", "omelette": "egg",
    "onion_rings": "onion", "oysters": "fish", "pad_thai": "noodles",
    "paella": "rice", "pancakes": "bread", "panna_cotta": "milk",
    "peking_duck": "chicken", "pho": "noodles", "pizza": "bread",
    "pork_chop": "chicken", "poutine": "potato", "prime_rib": "chicken",
    "pulled_pork_sandwich": "chicken", "ramen": "noodles", "ravioli": "pasta",
    "red_velvet_cake": "bread", "risotto": "rice", "samosa": "bread",
    "sashimi": "fish", "scallops": "fish", "seaweed_salad": "salad",
    "shrimp_and_grits": "fish", "spaghetti_bolognese": "pasta", "spaghetti_carbonara": "pasta",
    "spring_rolls": "bread", "steak": "chicken", "strawberry_shortcake": "bread",
    "sushi": "fish", "tacos": "bread", "takoyaki": "fish",
    "tiramisu": "bread", "tuna_tartare": "fish", "waffles": "bread"
}

# Food nutrition database (per 100g)
FOOD_DATABASE = {
    "rice": {"calories": 130, "proteins": 2.7, "fats": 0.3, "carbs": 28},
    "chicken": {"calories": 165, "proteins": 31, "fats": 3.6, "carbs": 0},
    "roti": {"calories": 297, "proteins": 7.9, "fats": 9.2, "carbs": 46},
    "dal": {"calories": 105, "proteins": 6.8, "fats": 0.4, "carbs": 18},
    "vegetables": {"calories": 25, "proteins": 1.5, "fats": 0.2, "carbs": 5},
    "curry": {"calories": 120, "proteins": 2, "fats": 8, "carbs": 10},
    "bread": {"calories": 265, "proteins": 9, "fats": 3.2, "carbs": 49},
    "egg": {"calories": 155, "proteins": 13, "fats": 11, "carbs": 1.1},
    "fish": {"calories": 206, "proteins": 22, "fats": 12, "carbs": 0},
    "salad": {"calories": 15, "proteins": 0.9, "fats": 0.2, "carbs": 3},
    "pasta": {"calories": 131, "proteins": 5, "fats": 1.1, "carbs": 25},
    "potato": {"calories": 77, "proteins": 2, "fats": 0.1, "carbs": 17},
    "onion": {"calories": 40, "proteins": 1.1, "fats": 0.1, "carbs": 9},
    "tomato": {"calories": 18, "proteins": 0.9, "fats": 0.2, "carbs": 3.9},
    "yogurt": {"calories": 59, "proteins": 10, "fats": 0.4, "carbs": 3.6},
    "cheese": {"calories": 402, "proteins": 25, "fats": 33, "carbs": 1.3},
    "milk": {"calories": 42, "proteins": 3.4, "fats": 1, "carbs": 5},
    "banana": {"calories": 89, "proteins": 1.1, "fats": 0.3, "carbs": 23},
    "apple": {"calories": 52, "proteins": 0.3, "fats": 0.2, "carbs": 14},
    "orange": {"calories": 47, "proteins": 0.9, "fats": 0.1, "carbs": 12},
    "soup": {"calories": 50, "proteins": 2, "fats": 1, "carbs": 8},
    "noodles": {"calories": 138, "proteins": 4.5, "fats": 2.1, "carbs": 25}
}

# Image analysis cache
image_cache = {}

# Initialize OpenAI client if API key is available
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
openai_client = None
if OPENAI_AVAILABLE and OPENAI_API_KEY:
    openai_client = OpenAI(api_key=OPENAI_API_KEY)
    print("✅ OpenAI client initialized")
else:
    print("⚠️  OpenAI not available (set OPENAI_API_KEY environment variable)")

app = Flask(__name__)
CORS(app, resources={
    r"/api/*": {
        "origins": "*",
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})


def ensure_data_dir():
    """Ensure data directory exists"""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not DATA_FILE.exists():
        DATA_FILE.write_text("[]", encoding="utf-8")
    load_image_cache()
    save_food101_meta()


def save_food101_meta():
    """Save Food-101 metadata to file"""
    try:
        meta = {
            "classes": FOOD101_CLASSES,
            "class_count": len(FOOD101_CLASSES),
            "mapping": FOOD101_TO_SIMPLE
        }
        FOOD101_META_FILE.write_text(json.dumps(meta, indent=2), encoding="utf-8")
        print(f"✅ Food-101 metadata saved ({len(FOOD101_CLASSES)} classes)")
    except Exception as e:
        print(f"⚠️  Could not save Food-101 metadata: {e}")


def load_image_cache():
    """Load cached analysis results"""
    global image_cache
    try:
        if CACHE_FILE.exists():
            image_cache = json.loads(CACHE_FILE.read_text(encoding="utf-8"))
            print(f"✅ Loaded {len(image_cache)} cached analyses")
    except Exception as e:
        print(f"⚠️  Could not load cache: {e}")


def save_image_cache():
    """Save image cache to file"""
    try:
        CACHE_FILE.write_text(json.dumps(image_cache, indent=2), encoding="utf-8")
    except Exception as e:
        print(f"⚠️  Could not save cache: {e}")


def get_image_hash(image_data):
    """Generate hash for image caching"""
    try:
        if not image_data:
            return None
        
        if isinstance(image_data, str):
            if image_data.startswith("data:image"):
                base64_data = image_data.split(",", 1)[1]
            else:
                base64_data = image_data
        else:
            base64_data = base64.b64encode(image_data).decode('utf-8')
        
        if not base64_data:
            return None
        
        # Use sampling strategy for better uniqueness
        data_len = len(base64_data)
        if data_len <= 3000:
            hash_input = base64_data
        else:
            sample_size = 1000
            start = base64_data[:sample_size]
            middle_start = data_len // 2 - sample_size // 2
            middle = base64_data[middle_start:middle_start + sample_size]
            end = base64_data[-sample_size:]
            hash_input = start + middle + end
        
        return hashlib.md5(hash_input.encode('utf-8')).hexdigest()
    except Exception as e:
        print(f"❌ Error creating image hash: {e}")
        return None


def normalize_food_name(food_name):
    """Normalize food name to match database"""
    food_lower = food_name.lower().strip().replace("_", " ")
    
    # Check if it's a Food-101 class name
    if food_lower in FOOD101_CLASSES:
        return FOOD101_TO_SIMPLE.get(food_lower, "vegetables")
    
    # Direct matches
    if food_lower in FOOD_DATABASE:
        return food_lower
    
    # Partial matches
    for key in FOOD_DATABASE.keys():
        if key in food_lower or food_lower in key:
            return key
    
    # Common variations
    variations = {
        "chicken curry": "chicken", "chicken dish": "chicken",
        "dal curry": "dal", "lentil": "dal", "lentils": "dal",
        "vegetable": "vegetables", "veggies": "vegetables",
        "roti": "roti", "chapati": "roti", "naan": "roti",
        "rice": "rice", "cooked rice": "rice", "white rice": "rice",
        "bread": "bread", "slice of bread": "bread",
        "egg": "egg", "boiled egg": "egg", "fried egg": "egg",
        "fish": "fish", "fish curry": "fish",
        "salad": "salad", "green salad": "salad",
        "pasta": "pasta", "spaghetti": "pasta",
        "potato": "potato", "potatoes": "potato"
    }
    return variations.get(food_lower, "vegetables")


def calculate_nutrition(food_items):
    """Calculate total nutrition from food items"""
    total_calories = 0
    total_proteins = 0
    total_fats = 0
    total_carbs = 0
    
    for item in food_items:
        food_key = normalize_food_name(item.get("name", ""))
        if food_key in FOOD_DATABASE:
            nutrition = FOOD_DATABASE[food_key]
            quantity = item.get("quantity", 1)
            if isinstance(quantity, str):
                import re
                numbers = re.findall(r'\d+', quantity)
                quantity = float(numbers[0]) if numbers else 1.0
            
            total_calories += nutrition["calories"] * quantity
            total_proteins += nutrition["proteins"] * quantity
            total_fats += nutrition["fats"] * quantity
            total_carbs += nutrition["carbs"] * quantity
    
    return {
        "calories": round(total_calories),
        "proteins": round(total_proteins, 1),
        "fats": round(total_fats, 1),
        "carbohydrates": round(total_carbs, 1)
    }


def recognize_food_with_ai(image_data):
    """Use OpenAI Vision API to recognize food items"""
    if not openai_client:
        return None
    
    if not image_data:
        print("   ⚠️  No image data provided to OpenAI")
        return None
    
    try:
        print("   📞 Calling OpenAI API...")
        
        # Handle different image data formats
        if isinstance(image_data, str):
            if image_data.startswith("data:image"):
                base64_data = image_data.split(",")[1]
                image_format = "png" if "image/png" in image_data else "jpeg"
            else:
                base64_data = image_data
                image_format = "jpeg"
        else:
            print("   ⚠️  Image data is not a string format")
            return None
        
        prompt = f"""Analyze this food image and identify ALL visible food items.

Use Food-101 dataset classes if applicable. Available Food-101 classes: {', '.join(FOOD101_CLASSES[:20])}... (101 total classes)

Return ONLY a valid JSON array. Each item must have "name" and "quantity" fields.
Example: [{{"name": "pizza", "quantity": "1 slice"}}, {{"name": "caesar_salad", "quantity": "1 portion"}}]

If you see NO food items, return: []

Food items in this image:"""
        
        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": f"data:image/{image_format};base64,{base64_data}"}}
                ]
            }],
            max_tokens=800,
            temperature=0.3
        )
        
        content = response.choices[0].message.content.strip()
        print(f"   ✅ OpenAI API call successful")
        print(f"   📝 Response preview: {content[:200]}...")
        
        # Parse JSON from response
        import re
        json_match = re.search(r'\[.*?\]', content, re.DOTALL)
        if json_match:
            try:
                food_items = json.loads(json_match.group())
                if isinstance(food_items, list):
                    valid_items = []
                    for item in food_items:
                        if isinstance(item, dict) and item.get('name'):
                            food_name = str(item.get('name', '')).lower().strip()
                            normalized_name = normalize_food_name(food_name)
                            valid_items.append({
                                "name": normalized_name,
                                "quantity": str(item.get('quantity', '1 portion')).strip()
                            })
                    if valid_items:
                        print(f"   ✅ Detected {len(valid_items)} food items")
                        return valid_items
            except json.JSONDecodeError as e:
                print(f"   ⚠️  JSON decode error: {e}")
        
        print("   ⚠️  No food items extracted")
        return []
    except Exception as e:
        print(f"   ❌ OpenAI error: {e}")
        return None


def analyze_plate(image_data=None):
    """Analyze plate with AI"""
    if not image_data:
        print("⚠️  No image data provided")
        return {
            "calories": 0,
            "proteins": 0,
            "fats": 0,
            "carbohydrates": 0,
            "food_items": [],
            "detected": False
        }
    
    image_hash = get_image_hash(image_data)
    
    if image_hash and image_hash in image_cache:
        print(f"✅ Using cached analysis")
        return image_cache[image_hash].copy()
    
    print(f"\n🔍 Starting food analysis...")
    print(f"   Image data length: {len(image_data) if image_data else 0} chars")
    print(f"   Image data type: {type(image_data).__name__}")
    if image_data and isinstance(image_data, str):
        print(f"   Image data preview: {image_data[:50]}...")
    print(f"   OpenAI Available: {openai_client is not None}")
    
    # Try OpenAI Vision API first
    if openai_client:
        try:
            print("🤖 Attempting OpenAI Vision API...")
            food_items = recognize_food_with_ai(image_data)
            
            if food_items is not None and len(food_items) > 0:
                print(f"   ✅ OpenAI detected {len(food_items)} food items")
                nutrition = calculate_nutrition(food_items)
                result = {
                    **nutrition,
                    "food_items": food_items,
                    "detected": True
                }
                if image_hash:
                    image_cache[image_hash] = result
                    save_image_cache()
                return result
            elif food_items is not None:
                print("   ⚠️  OpenAI returned empty results (no food detected)")
            else:
                print("   ⚠️  OpenAI returned None (error or unavailable)")
        except Exception as e:
            print(f"❌ OpenAI analysis failed: {e}")
            import traceback
            traceback.print_exc()
    
    # Try FoodRecognitionAgent as fallback
    try:
        from food_ai_agent import get_agent
        agent = get_agent()
        if agent and agent.model is not None:
            print("🤖 Attempting FoodRecognitionAgent (local model)...")
            result = agent.analyze_plate(image_data)
            if result and result.get("detected") and len(result.get("food_items", [])) > 0:
                print(f"   ✅ Local model detected {len(result['food_items'])} food items")
                if image_hash:
                    image_cache[image_hash] = result
                    save_image_cache()
                return result
            else:
                print("   ⚠️  Local model did not detect any food items")
        else:
            print("   ⚠️  FoodRecognitionAgent not available (model not loaded)")
    except ImportError:
        print("   ⚠️  FoodRecognitionAgent not available (tensorflow not installed)")
    except Exception as e:
        print(f"   ⚠️  FoodRecognitionAgent error: {e}")
        import traceback
        traceback.print_exc()
    
    # Final fallback - return empty result
    print("⚠️  No food items detected by any method")
    result = {
        "calories": 0,
        "proteins": 0,
        "fats": 0,
        "carbohydrates": 0,
        "food_items": [],
        "detected": False
    }
    if image_hash:
        image_cache[image_hash] = result
        save_image_cache()
    return result


# Initialize
ensure_data_dir()
analyses = []

print("\n" + "="*60)
print("🍽️  Food Analysis Backend with Food-101 Integration")
print(f"   Food-101 Classes: {len(FOOD101_CLASSES)}")
print(f"   OpenAI: {'✅ Available' if openai_client else '❌ Not available'}")
print("="*60 + "\n")


@app.get("/health")
def health_check():
    return jsonify({
        "status": "ok",
        "analysesCount": len(analyses),
        "food101_classes": len(FOOD101_CLASSES)
    })


@app.get("/api/food101/classes")
def get_food101_classes():
    """Get all Food-101 class names"""
    return jsonify({
        "classes": FOOD101_CLASSES,
        "count": len(FOOD101_CLASSES),
        "mapping": FOOD101_TO_SIMPLE
    })


@app.post("/api/analyze")
def post_analyze():
    try:
        payload = request.get_json(force=True, silent=True) or {}
        username = payload.get("username", "guest")
        image = payload.get("image")
        
        print(f"\n{'='*60}")
        print(f"📥 NEW ANALYSIS REQUEST")
        print(f"   User: {username}")
        print(f"   Image provided: {bool(image)}")
        print(f"{'='*60}")
        
        if not image:
            return jsonify({"message": "Image data is required."}), 400
        
        result = analyze_plate(image)
        
        if "food_items" not in result:
            result["food_items"] = []
        
        record = {
            "user": username,
            "image": image,
            **result,
            "date": datetime.now().strftime("%Y-%m-%d"),
            "id": f"py-{datetime.now().timestamp():.0f}-{random.randint(1000, 9999)}"
        }
        
        analyses.append(record)
        DATA_FILE.write_text(json.dumps(analyses, indent=2), encoding="utf-8")
        
        print(f"\n✅ ANALYSIS COMPLETE")
        print(f"   Food items: {len(result.get('food_items', []))}")
        print(f"   Detected: {result.get('detected', False)}")
        print(f"{'='*60}\n")
        
        return jsonify(record), 201
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@app.get("/api/analyses")
def get_analyses():
    return jsonify(analyses)


if __name__ == "__main__":
    print(f"\n🚀 Starting server on port {PORT}...")
    print(f"   Backend URL: http://localhost:{PORT}")
    print(f"   Health check: http://localhost:{PORT}/health")
    print(f"   API endpoint: http://localhost:{PORT}/api/analyze")
    print(f"\n   Press Ctrl+C to stop the server\n")
    try:
        app.run(host="127.0.0.1", port=PORT, debug=True, use_reloader=False)
    except OSError as e:
        if "Address already in use" in str(e) or "address is already in use" in str(e).lower():
            print(f"\n❌ ERROR: Port {PORT} is already in use!")
            print(f"   Please stop the other process using port {PORT} or change the PORT variable.")
            print(f"   To find what's using the port, run: netstat -ano | findstr :{PORT}")
        else:
            print(f"\n❌ ERROR starting server: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print(f"\n\n👋 Server stopped by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
