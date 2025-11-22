"""
AI Food Recognition Agent
Loads and uses the trained model for food recognition
"""

import os
import numpy as np
from pathlib import Path
import json
import base64
from io import BytesIO
from PIL import Image

try:
    import tensorflow as tf
    from tensorflow import keras
    TENSORFLOW_AVAILABLE = True
except ImportError:
    TENSORFLOW_AVAILABLE = False

BASE_DIR = Path(__file__).parent
MODELS_DIR = BASE_DIR / "models"
MODEL_PATH = MODELS_DIR / "food_recognition_model.h5"
CLASS_INDEX_PATH = MODELS_DIR / "food_classes.json"

# Food-101 integration
try:
    from food101_loader import FOOD101_CLASSES
    from backend import FOOD101_TO_SIMPLE
    FOOD101_AVAILABLE = True
except (ImportError, AttributeError):
    FOOD101_AVAILABLE = False
    FOOD101_CLASSES = []
    FOOD101_TO_SIMPLE = {}

IMG_SIZE = 224


class FoodRecognitionAgent:
    """AI Agent for recognizing food items in images"""
    
    def __init__(self):
        self.model = None
        self.class_indices = None
        self.index_to_class = None
        self.load_model()
    
    def load_model(self):
        """Load the trained model and class indices"""
        if not TENSORFLOW_AVAILABLE:
            print("Warning: TensorFlow not available. AI agent will use fallback.")
            return False
        
        if not MODEL_PATH.exists():
            print(f"Warning: Model not found at {MODEL_PATH}")
            print("   Run train_food_model.py to train a model first.")
            return False
        
        try:
            print(f"Loading AI model from {MODEL_PATH}...")
            self.model = keras.models.load_model(str(MODEL_PATH))
            print("✅ Model loaded successfully")
            
            # Load class indices
            if CLASS_INDEX_PATH.exists():
                with open(CLASS_INDEX_PATH, 'r') as f:
                    self.class_indices = json.load(f)
                # Create reverse mapping
                self.index_to_class = {v: k for k, v in self.class_indices.items()}
                print(f"✅ Loaded {len(self.class_indices)} food classes")
            else:
                print("⚠️  Class indices file not found")
                return False
            
            return True
        except Exception as e:
            print(f"❌ Error loading model: {e}")
            return False
    
    def preprocess_image(self, image_data):
        """Preprocess image for model input"""
        try:
            # Handle base64 data URL
            if isinstance(image_data, str):
                if image_data.startswith("data:image"):
                    # Extract base64 data
                    header, encoded = image_data.split(",", 1)
                    image_bytes = base64.b64decode(encoded)
                else:
                    # Assume it's already base64
                    image_bytes = base64.b64decode(image_data)
            else:
                image_bytes = image_data
            
            # Load and preprocess image
            img = Image.open(BytesIO(image_bytes))
            img = img.convert('RGB')
            img = img.resize((IMG_SIZE, IMG_SIZE))
            
            # Convert to array and normalize
            img_array = np.array(img) / 255.0
            img_array = np.expand_dims(img_array, axis=0)
            
            return img_array
        except Exception as e:
            print(f"Error preprocessing image: {e}")
            return None
    
    def predict_foods(self, image_data, top_k=5, confidence_threshold=0.1):
        """
        Predict food items in image
        
        Args:
            image_data: Base64 encoded image or image bytes
            top_k: Number of top predictions to return
            confidence_threshold: Minimum confidence score
        
        Returns:
            List of detected foods with confidence scores
        """
        if self.model is None or self.index_to_class is None:
            return []
        
        # Preprocess image
        img_array = self.preprocess_image(image_data)
        if img_array is None:
            return []
        
        # Get predictions
        try:
            predictions = self.model.predict(img_array, verbose=0)[0]
            
            # Get top-k predictions
            top_indices = np.argsort(predictions)[-top_k:][::-1]
            
            detected_foods = []
            for idx in top_indices:
                confidence = float(predictions[idx])
                if confidence >= confidence_threshold:
                    food_class = self.index_to_class.get(idx, "unknown")
                    detected_foods.append({
                        "name": food_class,
                        "confidence": confidence,
                        "quantity": self._estimate_quantity(food_class, confidence)
                    })
            
            return detected_foods
        except Exception as e:
            print(f"Error during prediction: {e}")
            return []
    
    def _estimate_quantity(self, food_class, confidence):
        """Estimate quantity based on confidence and food type"""
        # Higher confidence = more visible = larger portion
        if confidence > 0.8:
            return "1.5 portions"
        elif confidence > 0.6:
            return "1 portion"
        elif confidence > 0.4:
            return "0.75 portions"
        else:
            return "0.5 portions"
    
    def analyze_plate(self, image_data):
        """
        Complete plate analysis: detect foods and calculate nutrition
        
        Args:
            image_data: Base64 encoded image
        
        Returns:
            Dictionary with detected foods and nutritional values
        """
        detected_foods = self.predict_foods(image_data, top_k=5, confidence_threshold=0.1)
        
        if not detected_foods:
            return {
                "food_items": [],
                "detected": False,
                "calories": 0,
                "proteins": 0,
                "fats": 0,
                "carbohydrates": 0
            }
        
        # Calculate nutrition from detected foods
        from backend import FOOD_DATABASE, normalize_food_name, calculate_nutrition
        
        # Normalize Food-101 class names to simplified names
        for item in detected_foods:
            original_name = item["name"]
            # Check if it's a Food-101 class
            if FOOD101_AVAILABLE and original_name in FOOD101_CLASSES:
                item["name"] = FOOD101_TO_SIMPLE.get(original_name, normalize_food_name(original_name))
            else:
                item["name"] = normalize_food_name(original_name)
        
        # Format food items for nutrition calculation
        food_items_for_calc = [
            {
                "name": item["name"],
                "quantity": item["quantity"]
            }
            for item in detected_foods
        ]
        
        nutrition = calculate_nutrition(food_items_for_calc)
        
        return {
            "food_items": detected_foods,
            "detected": True,
            **nutrition
        }


# Global agent instance
_agent_instance = None

def get_agent():
    """Get or create the food recognition agent"""
    global _agent_instance
    if _agent_instance is None:
        _agent_instance = FoodRecognitionAgent()
    return _agent_instance

