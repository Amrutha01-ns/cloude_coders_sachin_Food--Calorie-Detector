"""
AI Food Recognition Model Training Script
Trains a custom CNN model to recognize food items from images
"""

import os
import numpy as np
from pathlib import Path
import json
from datetime import datetime

try:
    import tensorflow as tf
    from tensorflow import keras
    from tensorflow.keras import layers, models
    from tensorflow.keras.applications import MobileNetV2
    from tensorflow.keras.preprocessing.image import ImageDataGenerator
    from tensorflow.keras.callbacks import ModelCheckpoint, EarlyStopping, ReduceLROnPlateau
    TENSORFLOW_AVAILABLE = True
except ImportError:
    TENSORFLOW_AVAILABLE = False
    print("Warning: TensorFlow not installed. Install with: pip install tensorflow")

BASE_DIR = Path(__file__).parent
MODELS_DIR = BASE_DIR / "models"
TRAINING_DATA_DIR = BASE_DIR / "training_data"
MODEL_PATH = MODELS_DIR / "food_recognition_model.h5"
CLASS_INDEX_PATH = MODELS_DIR / "food_classes.json"

# Food classes - can use Food-101 or custom classes
# If Food-101 dataset is prepared, classes will be loaded from there
FOOD_CLASSES = [
    "rice", "chicken", "roti", "dal", "vegetables", "curry", 
    "bread", "egg", "fish", "salad", "pasta", "potato", 
    "onion", "tomato", "yogurt", "cheese", "milk", 
    "banana", "apple", "orange"
]

# Try to load Food-101 classes if available
try:
    from food101_loader import FOOD101_CLASSES, check_food101_dataset
    exists, _ = check_food101_dataset()
    if exists:
        # Check if training data uses Food-101
        training_classes_file = TRAINING_DATA_DIR / "food101_classes.json"
        if training_classes_file.exists():
            with open(training_classes_file, 'r') as f:
                food101_mapping = json.load(f)
                FOOD_CLASSES = list(food101_mapping.values())
                print(f"✅ Using Food-101 classes: {len(FOOD_CLASSES)} classes")
except ImportError:
    pass

IMG_SIZE = 224
BATCH_SIZE = 32
EPOCHS = 50


def create_model(num_classes):
    """Create a food recognition model using transfer learning"""
    if not TENSORFLOW_AVAILABLE:
        raise ImportError("TensorFlow is required for model training")
    
    # Use MobileNetV2 as base (pre-trained on ImageNet)
    base_model = MobileNetV2(
        input_shape=(IMG_SIZE, IMG_SIZE, 3),
        include_top=False,
        weights='imagenet'
    )
    
    # Freeze base model layers initially
    base_model.trainable = False
    
    # Add custom classification head
    model = models.Sequential([
        base_model,
        layers.GlobalAveragePooling2D(),
        layers.Dropout(0.3),
        layers.Dense(512, activation='relu'),
        layers.Dropout(0.3),
        layers.Dense(256, activation='relu'),
        layers.Dropout(0.2),
        layers.Dense(num_classes, activation='softmax', name='food_classifier')
    ])
    
    # Compile model
    model.compile(
        optimizer=keras.optimizers.Adam(learning_rate=0.001),
        loss='categorical_crossentropy',
        metrics=['accuracy', 'top_3_accuracy']
    )
    
    return model


def prepare_data_generators():
    """Prepare data generators for training and validation"""
    if not TRAINING_DATA_DIR.exists():
        print(f"Creating training data directory: {TRAINING_DATA_DIR}")
        TRAINING_DATA_DIR.mkdir(parents=True, exist_ok=True)
        print("\n⚠️  Training data directory created. Please organize your food images as follows:")
        print("training_data/")
        print("  ├── train/")
        print("  │   ├── rice/")
        print("  │   ├── chicken/")
        print("  │   ├── roti/")
        print("  │   └── ...")
        print("  └── validation/")
        print("      ├── rice/")
        print("      ├── chicken/")
        print("      └── ...")
        return None, None
    
    train_dir = TRAINING_DATA_DIR / "train"
    val_dir = TRAINING_DATA_DIR / "validation"
    
    if not train_dir.exists() or not val_dir.exists():
        print(f"⚠️  Training directories not found. Expected:")
        print(f"  - {train_dir}")
        print(f"  - {val_dir}")
        return None, None
    
    # Data augmentation for training
    train_datagen = ImageDataGenerator(
        rescale=1./255,
        rotation_range=20,
        width_shift_range=0.2,
        height_shift_range=0.2,
        horizontal_flip=True,
        zoom_range=0.2,
        fill_mode='nearest'
    )
    
    # Only rescale for validation
    val_datagen = ImageDataGenerator(rescale=1./255)
    
    train_generator = train_datagen.flow_from_directory(
        train_dir,
        target_size=(IMG_SIZE, IMG_SIZE),
        batch_size=BATCH_SIZE,
        class_mode='categorical',
        shuffle=True
    )
    
    val_generator = val_datagen.flow_from_directory(
        val_dir,
        target_size=(IMG_SIZE, IMG_SIZE),
        batch_size=BATCH_SIZE,
        class_mode='categorical',
        shuffle=False
    )
    
    return train_generator, val_generator


def train_model():
    """Train the food recognition model"""
    if not TENSORFLOW_AVAILABLE:
        print("❌ TensorFlow is not installed. Please install it first:")
        print("   pip install tensorflow")
        return False
    
    print("🍽️  Starting Food Recognition Model Training...")
    print("=" * 60)
    
    # Prepare data
    train_gen, val_gen = prepare_data_generators()
    if train_gen is None or val_gen is None:
        print("\n❌ Training data not found. Please organize your images first.")
        return False
    
    num_classes = len(train_gen.class_indices)
    print(f"\n📊 Found {num_classes} food classes")
    print(f"   Classes: {list(train_gen.class_indices.keys())}")
    
    # Save class indices for inference
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    with open(CLASS_INDEX_PATH, 'w') as f:
        json.dump(train_gen.class_indices, f, indent=2)
    print(f"   Saved class indices to {CLASS_INDEX_PATH}")
    
    # Create model
    print("\n🏗️  Creating model architecture...")
    model = create_model(num_classes)
    model.summary()
    
    # Callbacks
    callbacks = [
        ModelCheckpoint(
            str(MODEL_PATH),
            monitor='val_accuracy',
            save_best_only=True,
            verbose=1
        ),
        EarlyStopping(
            monitor='val_accuracy',
            patience=10,
            restore_best_weights=True,
            verbose=1
        ),
        ReduceLROnPlateau(
            monitor='val_loss',
            factor=0.5,
            patience=5,
            min_lr=1e-7,
            verbose=1
        )
    ]
    
    # Train model
    print("\n🚀 Starting training...")
    print(f"   Epochs: {EPOCHS}")
    print(f"   Batch size: {BATCH_SIZE}")
    print(f"   Image size: {IMG_SIZE}x{IMG_SIZE}")
    print("-" * 60)
    
    history = model.fit(
        train_gen,
        epochs=EPOCHS,
        validation_data=val_gen,
        callbacks=callbacks,
        verbose=1
    )
    
    # Fine-tuning: Unfreeze base model and train with lower learning rate
    print("\n🔧 Fine-tuning base model...")
    base_model = model.layers[0]
    base_model.trainable = True
    
    # Recompile with lower learning rate
    model.compile(
        optimizer=keras.optimizers.Adam(learning_rate=0.0001),
        loss='categorical_crossentropy',
        metrics=['accuracy', 'top_3_accuracy']
    )
    
    # Continue training
    history_finetune = model.fit(
        train_gen,
        epochs=10,
        validation_data=val_gen,
        callbacks=callbacks,
        verbose=1,
        initial_epoch=EPOCHS
    )
    
    # Final evaluation
    print("\n📈 Evaluating final model...")
    val_loss, val_acc, val_top3 = model.evaluate(val_gen, verbose=1)
    print(f"\n✅ Training complete!")
    print(f"   Validation Accuracy: {val_acc:.2%}")
    print(f"   Top-3 Accuracy: {val_top3:.2%}")
    print(f"   Model saved to: {MODEL_PATH}")
    
    return True


def download_sample_data():
    """Helper function to download sample training data"""
    print("\n📥 To train the model, you need food images organized by class.")
    print("   You can:")
    print("   1. Download Food-101 dataset: https://www.kaggle.com/datasets/kmader/food41")
    print("   2. Use your own food images organized in folders")
    print("   3. Use web scraping (with permission) to collect food images")
    print("\n   Expected structure:")
    print("   training_data/")
    print("     ├── train/")
    print("     │   ├── rice/")
    print("     │   │   ├── image1.jpg")
    print("     │   │   └── image2.jpg")
    print("     │   ├── chicken/")
    print("     │   └── ...")
    print("     └── validation/")
    print("         ├── rice/")
    print("         └── ...")


if __name__ == "__main__":
    print("🤖 Food Recognition AI Model Trainer")
    print("=" * 60)
    
    if not TENSORFLOW_AVAILABLE:
        print("❌ TensorFlow is required but not installed.")
        print("   Install with: pip install tensorflow")
        exit(1)
    
    # Check for GPU
    gpus = tf.config.list_physical_devices('GPU')
    if gpus:
        print(f"✅ GPU detected: {len(gpus)} device(s)")
        for gpu in gpus:
            print(f"   {gpu}")
    else:
        print("⚠️  No GPU detected. Training will use CPU (slower)")
    
    # Train model
    success = train_model()
    
    if not success:
        download_sample_data()
    else:
        print("\n🎉 Model training completed successfully!")
        print(f"   You can now use the model in backend.py")

