# Backend Diagnostic Guide

## Quick Test

To check if your backend is working correctly, run the diagnostic script:

```bash
python test_backend.py
```

This will test:
1. ✅ Backend health check
2. ✅ API info endpoint
3. ✅ Analyze function
4. ✅ Image analysis with sample data

## Manual Testing

### 1. Check if backend is running

Open in browser: `http://localhost:4000/health`

Should return: `{"status": "ok", "analysesCount": X}`

### 2. Check API info

Open in browser: `http://localhost:4000/api/test`

Should show OpenAI and AI agent availability.

### 3. Test analysis function

Open in browser: `http://localhost:4000/api/test-analyze`

Should return a test result with nutrition values.

### 4. Check backend console

When you upload an image, the backend console should show:

```
============================================================
📥 NEW ANALYSIS REQUEST
   User: guest
   Image provided: True
   Image data length: XXXXX chars
============================================================
🔍 Calling analyze_plate()...
📸 Image hash: abc123...
🔍 Starting food analysis...
   AI Agent Available: True/False
   OpenAI Available: True/False
...
✅ ANALYSIS COMPLETE
   Calories: XXX cal
   Proteins: XXg
   ...
============================================================
```

## Common Issues

### Issue: "Cannot connect to backend"
**Solution:** Make sure `python backend.py` is running

### Issue: "Analysis returned None"
**Solution:** Check backend console for errors in `analyze_plate()` function

### Issue: "Image data length: 0 chars"
**Solution:** Frontend is not sending image data correctly

### Issue: "OpenAI recognition error"
**Solution:** Check if OPENAI_API_KEY is set, or backend will use fallback

## Expected Backend Output on Startup

```
============================================================
🚀 STARTING FLASK SERVER
============================================================
   Host: 0.0.0.0
   Port: 4000
   API endpoint: http://localhost:4000/api/analyze
   Health check: http://localhost:4000/health
   Test endpoint: http://localhost:4000/api/test
============================================================
   Press Ctrl+C to stop
============================================================

🍽️  Food Analysis Backend Starting...
   Cache entries: X
   AI Agent: ✅ Available / ❌ Not available
   OpenAI: ✅ Available / ❌ Not available (set OPENAI_API_KEY)
============================================================

🧪 Testing analyze_plate function on startup...
✅ analyze_plate test passed: XXX cal

✅ Server ready to accept requests

 * Running on http://0.0.0.0:4000
```

## Expected Output When Analyzing Image

```
============================================================
📥 NEW ANALYSIS REQUEST
   User: guest
   Image provided: True
   Image data length: 50000 chars
============================================================
🔍 Calling analyze_plate()...
📸 Image hash: abc123def456...
🆕 New image, not in cache (cache size: 0)

🔍 Starting food analysis...
   AI Agent Available: False
   OpenAI Available: True

🤖 Attempting OpenAI Vision API...
OpenAI raw response: [{"name": "rice", "quantity": "1 cup"}...
✅ Detected 2 food items: ['rice', 'chicken']
✅ OpenAI detected 2 food items
   Calculated nutrition: 450 cal, 28g protein
⚠️  Using deterministic fallback (AI unavailable or no items detected)
   Generated consistent values: 450 cal, 28g protein
   ✅ Cached for future use (cache size: 1)

✅ ANALYSIS COMPLETE
   Calories: 450 cal
   Proteins: 28g
   Fats: 20g
   Carbs: 50g
   Food items: 2
   Detected: True
   Record keys: ['user', 'image', 'calories', 'proteins', ...]
============================================================
```

## If Analysis Fails

1. **Check backend console** - Look for ❌ error messages
2. **Check image data** - Should be > 1000 chars
3. **Check hash generation** - Should show image hash
4. **Check AI availability** - OpenAI or fallback should work
5. **Check final result** - Should always return nutrition values

## Debug Mode

To see more detailed output, the backend already logs everything. Check the console where you ran `python backend.py` for detailed information.

