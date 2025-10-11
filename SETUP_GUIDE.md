# Memora Setup Guide

## Quick Start (5 minutes)

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Get Gemini API Key
1. Visit: https://makersuite.google.com/app/apikey
2. Click "Create API Key"
3. Copy the generated key

### 3. Set Environment Variable
**Windows (PowerShell):**
```powershell
$env:GEMINI_API_KEY="your_actual_api_key_here"
```

**Windows (Command Prompt):**
```cmd
set GEMINI_API_KEY=your_actual_api_key_here
```

**Linux/Mac:**
```bash
export GEMINI_API_KEY="your_actual_api_key_here"
```

### 4. Run the Application
```bash
python run_memora.py
```

The app will open at: http://localhost:8501

## Alternative: Using .env File

1. Copy the example file:
```bash
cp .env.example .env
```

2. Edit `.env` and add your API key:
```
GEMINI_API_KEY=your_actual_api_key_here
```

3. Run the application:
```bash
streamlit run memora_app.py
```

## Testing the Installation

Run the test suite to verify everything works:
```bash
python test_memora.py
```

## Demo the Features

See what Memora can do:
```bash
python demo_usage.py
```

## Troubleshooting

### "Module not found" errors
- Make sure you installed requirements: `pip install -r requirements.txt`
- Check your Python version (3.11+ recommended)

### "API key not found" errors
- Verify your GEMINI_API_KEY is set correctly
- Make sure you copied the full API key from Google AI Studio

### "Permission denied" errors
- On Windows, try running PowerShell as Administrator
- On Linux/Mac, check file permissions

### App won't start
- Check if port 8501 is already in use
- Try a different port: `streamlit run memora_app.py --server.port 8502`

## File Structure

```
memora/
├── memora_app.py          # Main application
├── run_memora.py          # Launcher script
├── test_memora.py         # Test suite
├── demo_usage.py          # Feature demonstration
├── requirements.txt       # Dependencies
├── .env.example          # Environment template
├── README.md             # Full documentation
└── SETUP_GUIDE.md        # This file
```

## Next Steps

1. **First Run**: Start with the demo to understand features
2. **Test Assessment**: Try the cognitive assessment flow
3. **Customize**: Modify questions or scoring in `memora_app.py`
4. **Deploy**: Consider deploying to Streamlit Cloud for sharing

## Support

- Check the README.md for detailed documentation
- Run `python demo_usage.py` to see all features
- Run `python test_memora.py` to verify installation
