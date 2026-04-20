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

### 4. Add your API keys

```bash
cp .env.example .env
```

Open `.env` and fill in both keys:

```
GROQ_API_KEY=your_groq_api_key_here
WEATHER_API_KEY=your_openweathermap_api_key_here
```

---

## Run

```bash
python main.py
```

```
How do you want to use the assistant?
  1) CLI based
  2) Web based
```

- **Web mode** — opens at http://localhost:5000 — use Chrome or Edge
- **CLI mode** — uses your microphone directly via PyAudio

---

## What Ruby can do

- Answer any general question via LLM
- Get real-time city weather — *"What's the weather in Mumbai?"*
- Tell jokes, chat, explain topics
- Maintains full conversation history across turns
- Greets in Hindi on startup

---

## Notes

- The `.env` file is gitignored — never commit your API keys
- Groq free tier is generous — Whisper and LLM calls are free up to rate limits
- Edge TTS is completely free, no API key needed
- Weather tool is called automatically by the LLM when needed — no special phrasing required
- Web mode requires Chrome or Edge (MediaRecorder API)
