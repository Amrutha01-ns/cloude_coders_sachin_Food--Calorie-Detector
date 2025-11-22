# AI Food Recognition Model Training Guide

This guide explains how to train your custom AI agent for food recognition and calorie analysis.

## Overview

The system uses a **Convolutional Neural Network (CNN)** based on MobileNetV2 (transfer learning) to recognize food items in images. The trained model can identify multiple foods in a single image and calculate accurate nutritional values.

## Architecture

- **Base Model**: MobileNetV2 (pre-trained on ImageNet)
- **Custom Head**: Dense layers for food classification
- **Input Size**: 224x224 pixels
- **Output**: Probability distribution over food classes

## Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- TensorFlow (for deep learning)
- Pillow (for image processing)
- NumPy (for numerical operations)

## Step 2: Prepare Training Data

Organize your food images in the following structure:

```
training_data/
├── train/
│   ├── rice/
│   │   ├── rice_001.jpg
│   │   ├── rice_002.jpg
│   │   └── ...
│   ├── chicken/
│   │   ├── chicken_001.jpg
│   │   └── ...
│   ├── roti/
│   ├── dal/
│   └── ... (other food classes)
└── validation/
    ├── rice/
    ├── chicken/
    └── ... (same structure as train)
```

### Data Requirements

- **Minimum**: 50-100 images per class for training
- **Recommended**: 200+ images per class for better accuracy
- **Validation**: 20-30% of total images (separate from training)
- **Format**: JPG, PNG (RGB images)
- **Size**: Any size (will be resized to 224x224)

### Where to Get Training Data

1. **Food-101 Dataset**: 
   - Download from: https://www.kaggle.com/datasets/kmader/food41
   - Contains 101 food categories with 1000 images each

2. **Your Own Images**:
   - Take photos of your meals
   - Organize by food type
   - Ensure good lighting and clear visibility

3. **Web Scraping** (with permission):
   - Use food image datasets from research papers
   - Ensure you have rights to use the images

## Step 3: Train the Model

Run the training script:

```bash
python train_food_model.py
```

### Training Process

1. **Data Loading**: Loads images from `training_data/` directory
2. **Data Augmentation**: Applies rotations, flips, zooms to increase dataset
3. **Transfer Learning**: Uses pre-trained MobileNetV2 weights
4. **Training**: Trains custom classification head
5. **Fine-tuning**: Unfreezes base model for final optimization
6. **Saving**: Saves best model to `models/food_recognition_model.h5`

### Training Parameters

- **Epochs**: 50 (with early stopping)
- **Batch Size**: 32
- **Learning Rate**: 0.001 (initial), 0.0001 (fine-tuning)
- **Image Size**: 224x224

### Expected Training Time

- **CPU**: 2-4 hours (depending on dataset size)
- **GPU**: 30-60 minutes (much faster)

## Step 4: Verify Model

After training, the model will be saved to:
- `models/food_recognition_model.h5` (model weights)
- `models/food_classes.json` (class labels)

Check the training output for:
- **Validation Accuracy**: Should be >80% for good performance
- **Top-3 Accuracy**: Should be >90%

## Step 5: Use the Trained Model

The backend automatically loads the trained model when available:

```bash
python backend.py
```

The AI agent will:
1. Load the trained model on startup
2. Use it for food recognition in API calls
3. Calculate nutrition based on detected foods

## Improving Model Performance

### 1. More Training Data
- Add more images per class
- Ensure diverse lighting conditions
- Include different angles and presentations

### 2. Data Augmentation
Already included in training:
- Rotation (±20°)
- Horizontal flip
- Zoom (0.8-1.2x)
- Width/height shifts

### 3. Hyperparameter Tuning
Edit `train_food_model.py` to adjust:
- Learning rate
- Batch size
- Dropout rates
- Model architecture

### 4. Transfer Learning Options
Try different base models:
- EfficientNet (better accuracy, slower)
- ResNet50 (balanced)
- MobileNetV3 (faster, smaller)

## Troubleshooting

### "No training data found"
- Ensure `training_data/train/` and `training_data/validation/` exist
- Check folder names match food classes exactly

### "Out of memory"
- Reduce batch size (e.g., 16 instead of 32)
- Use smaller image size (e.g., 128x128)
- Train on fewer classes at once

### "Low accuracy"
- Add more training images
- Check image quality
- Ensure proper class balance
- Increase training epochs

### "Model not loading"
- Verify model file exists at `models/food_recognition_model.h5`
- Check TensorFlow version compatibility
- Re-train if model file is corrupted

## Advanced: Custom Food Classes

To add new food classes:

1. Add images to training data:
   ```
   training_data/train/new_food/
   training_data/validation/new_food/
   ```

2. Add nutrition data to `backend.py`:
   ```python
   FOOD_DATABASE["new_food"] = {
       "calories": 100,
       "proteins": 5,
       "fats": 2,
       "carbs": 15
   }
   ```

3. Re-train the model

## Model Evaluation

After training, evaluate on test set:

```python
from food_ai_agent import get_agent

agent = get_agent()
# Test on individual images
result = agent.analyze_plate(image_data)
print(result)
```

## Production Deployment

For production:
1. Use GPU for faster inference
2. Optimize model (TensorFlow Lite for mobile)
3. Add caching for repeated images
4. Monitor accuracy and retrain periodically

## Next Steps

- Collect more training data
- Fine-tune on specific cuisines
- Add portion size estimation
- Integrate with calorie tracking apps

