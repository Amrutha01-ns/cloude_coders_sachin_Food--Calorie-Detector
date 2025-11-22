# Troubleshooting Food Recognition

## Issue: Food items are not being identified

If food items are not being detected, follow these steps:

### 1. Check Backend Logs

When you upload an image, check the backend console output. You should see messages like:
```
🔍 Starting food analysis...
   AI Agent Available: True/False
   OpenAI Available: True/False
🤖 Attempting OpenAI Vision API...
✅ OpenAI detected 3 food items
```

### 2. Verify OpenAI API Key

**Check if API key is set:**
```bash
# Windows PowerShell
echo $env:OPENAI_API_KEY

# Windows CMD
echo %OPENAI_API_KEY%

# Linux/Mac
echo $OPENAI_API_KEY
```

**Set the API key if missing:**
```bash
# Windows PowerShell
$env:OPENAI_API_KEY="your-api-key-here"

# Windows CMD
set OPENAI_API_KEY=your-api-key-here

# Linux/Mac
export OPENAI_API_KEY="your-api-key-here"
```

**Restart the backend** after setting the key.

### 3. Check Image Format

The system supports:
- JPEG/JPG
- PNG
- Base64 encoded images

Make sure your images are:
- Clear and well-lit
- Show food items clearly
- Not too dark or blurry

### 4. Test OpenAI API Directly

Test if OpenAI is working:

```python
from openai import OpenAI
import base64

client = OpenAI(api_key="your-key")

# Test with a simple image
response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{
        "role": "user",
        "content": [
            {"type": "text", "text": "What food is in this image?"},
            {"type": "image_url", "image_url": {"url": "data:image/jpeg;base64,..."}}
        ]
    }]
)
print(response.choices[0].message.content)
```

### 5. Check Network Connection

OpenAI API requires internet connection. Verify:
- Internet is working
- No firewall blocking API calls
- API key has credits/quota

### 6. Enable Debug Mode

The backend now includes detailed logging. Look for:
- `✅` = Success
- `⚠️` = Warning (fallback used)
- `❌` = Error

### 7. Common Issues

**Issue: "OpenAI returned no food items"**
- The image might not contain recognizable food
- Try a clearer image
- Check if the image is actually a food photo

**Issue: "Using fallback random values"**
- OpenAI API key not set
- API call failed
- Check backend logs for error messages

**Issue: "JSON decode error"**
- OpenAI response format changed
- The system will try to extract food names from text
- Check logs for extracted foods

### 8. Verify Response Format

Check the API response in browser DevTools (Network tab):
- Should contain `food_items` array
- Each item should have `name` and `quantity`
- `detected: true` means AI was used

### 9. Test with Sample Image

Try uploading a clear photo of:
- A plate with rice and curry
- A sandwich
- A salad bowl

These are easier for AI to recognize.

### 10. Alternative: Train Custom Model

If OpenAI doesn't work, train your own model:
1. Collect food images
2. Run `python train_food_model.py`
3. The custom model will be used automatically

## Still Not Working?

1. **Check backend console** for detailed error messages
2. **Verify requirements** are installed: `pip install -r requirements.txt`
3. **Test API endpoint** directly:
   ```bash
   curl -X POST http://localhost:4000/api/analyze \
     -H "Content-Type: application/json" \
     -d '{"username":"test","image":"data:image/jpeg;base64,..."}'
   ```
4. **Check browser console** for frontend errors

## Quick Fixes

**Quick test without OpenAI:**
- The system will use heuristic fallback
- Shows estimated foods (rice, vegetables)
- Calculates nutrition from estimates

**Enable verbose logging:**
- Backend already logs detailed info
- Check console output when uploading images

