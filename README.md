# Ruby — AI Voice Assistant

A full-fledged LLM-powered voice assistant with a web UI and CLI mode.

| Component | Technology |
|---|---|
| Speech-to-Text | Groq Whisper (`whisper-large-v3-turbo`) |
| AI Reasoning | Groq LLM (`llama-3.3-70b-versatile`) with tool calling |
| Weather | OpenWeatherMap API (free) |
| Text-to-Speech | Edge TTS (`hi-IN-SwaraNeural` / `en-US-JennyNeural`) |
| Web Framework | Flask |
| CLI mic input | SpeechRecognition + PyAudio |

---

## Get API Keys

### Groq API Key (Free)

1. Go to [https://console.groq.com](https://console.groq.com) and sign up (free)
2. Navigate to **API Keys** → **Create API Key**
3. Copy the key

### OpenWeatherMap API Key (Free)

1. Go to [https://openweathermap.org/api](https://openweathermap.org/api) and sign up (free)
2. Go to **My API Keys** → copy the default key
3. Free tier includes 60 calls/minute and current weather data

---

## Setup

### 1. Create a virtual environment (Python 3.12 required)

> PyAudio does not support Python 3.13+. Use Python 3.12.

```bash
py -3.12 -m venv venv
```

### 2. Activate it

```bash
# Windows
source venv/Scripts/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

**Note on PyAudio (Windows):** If installation fails, download a pre-built wheel from [here](https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio) and install with:
```bash
pip install pyaudio-*.whl
```

### 4. Add your API keys

```bash
copy .env.example .env
```

Open `.env` and fill in your API keys:

```
GROQ_API_KEY=your_actual_groq_api_key
WEATHER_API_KEY=your_actual_openweather_key
```

---

## Run

```bash
python main.py
```

You'll see a menu:
```
How do you want to use the assistant?
  1) CLI based
  2) Web based
```

### Web Mode (Recommended)

```
Select: 2
Ruby is running at http://localhost:5000
```

- Open **Chrome** or **Edge** at `http://localhost:5000`
- Click the microphone button to start recording
- Ruby will transcribe, process, and respond
- CORS is enabled for cross-origin requests

### CLI Mode

```
Select: 1
```

- Uses your microphone directly
- Type or speak to interact
- Say "exit", "quit", "stop", or "bye" to quit

---

## What Ruby can do

- Answer any general question via LLM
- Get real-time city weather — *"What's the weather in Mumbai?"*
- Tell jokes, chat, explain topics
- Maintains full conversation history across turns
- Greets in Hindi on startup

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `GROQ_API_KEY not set` | Create `.env` file with your API key from [console.groq.com](https://console.groq.com) |
| `ModuleNotFoundError: No module named 'X'` | Run `pip install -r requirements.txt` |
| Microphone not working | Check system audio settings, grant microphone permission |
| PyAudio installation fails on Windows | Download pre-built wheel from [lfd.uci.edu](https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio) |
| Web page won't load | Ensure Flask is running on port 5000 (not already in use) |
| Audio playback not working in web | Use Chrome or Edge; Safari doesn't support web audio well |

---

## Notes

- The `.env` file is gitignored — never commit your API keys
- Groq free tier is generous — Whisper and LLM calls are free up to rate limits
- Edge TTS is completely free, no API key needed
- Weather tool is called automatically by the LLM when needed — no special phrasing required
- Web mode requires Chrome or Edge (MediaRecorder API)
