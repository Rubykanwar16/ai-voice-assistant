# Setup Instructions

## Prerequisites
- Python 3.8 or higher
- FFmpeg (required for audio processing)
- Microphone (for CLI and voice input)

## Installation Steps

### 1. Clone and Install Dependencies
```bash
pip install -r requirements.txt
```

**Note:** PyAudio can be tricky on Windows. If installation fails:
- Download pre-built wheel from: https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio
- Install with: `pip install pyaudio-*.whl`

### 2. Set Up Environment Variables
```bash
# Copy the example file
copy .env.example .env

# Edit .env and add your API keys:
# - GROQ_API_KEY: Get from https://console.groq.com/keys
# - WEATHER_API_KEY: Get from https://openweathermap.org/api (optional)
```

### 3. Run the Application

**CLI Mode:**
```bash
python main.py
# Select option 1
```

**Web Mode:**
```bash
python main.py
# Select option 2
# Open http://localhost:5000 in your browser
```

## Troubleshooting

- **"GROQ_API_KEY not set"**: Create a `.env` file with your API key
- **Microphone not working**: Check system audio settings and ensure microphone permissions
- **PyAudio installation fails**: Use pre-built wheel (see above)
- **FFmpeg not found**: Install from https://ffmpeg.org/download.html
