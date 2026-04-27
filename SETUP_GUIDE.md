# AI Voice Assistant - Setup Guide

## Prerequisites
- Python 3.8 or higher
- A Groq API key (get from https://console.groq.com)

## Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

If you get any import errors, install missing packages:
```bash
pip install SpeechRecognition pyttsx3 pywhatkit wikipedia pyjokes
```

## Step 2: Create `.env` File

Copy the `.env.example` file and create a `.env` file in the project root:

```bash
cp .env.example .env
```

Edit `.env` and add your Groq API key:
```
GROQ_API_KEY=your_actual_groq_api_key_here
```

Get your API key from: https://console.groq.com

## Step 3: Run the Application

### Option A: Web Interface (Recommended)

```bash
python main.py
```

Choose option `2` for web-based

Then open your browser to:
```
http://localhost:5000
```

### Option B: CLI Interface

```bash
python main.py
```

Choose option `1` for CLI-based

## Troubleshooting

### "Could not reach the server" Error
- Make sure Flask backend is running (`python main.py` → option 2)
- Check that you're accessing `http://localhost:5000` (not a different port)
- Open browser console (F12) to see detailed error messages

### "Port 5000 already in use" Error
Run on a different port:
```bash
PORT=5001 python main.py
```

### Module not found errors
Install all requirements:
```bash
pip install -r requirements.txt
```

### GROQ_API_KEY not set
- Create a `.env` file in the project root
- Add: `GROQ_API_KEY=your_key_here`
- Get your key from: https://console.groq.com

### Microphone access denied (CLI mode)
- Windows: Allow microphone access in Settings
- Mac: Grant microphone permission in System Preferences
- Linux: Check PulseAudio/ALSA configuration

## Available Routes

- `GET /` - Main web interface
- `GET /health` - Health check
- `GET /greet` - Get greeting audio
- `POST /voice` - Process audio input
- `POST /reset` - Reset conversation

## Features

- 🎤 Voice input with automatic transcription
- 🤖 AI responses powered by Groq LLM
- 🔊 Text-to-speech output
- 💬 Conversation history
- 🌐 Web UI and CLI modes
- 🛠️ Tool calling (weather, etc.)

## Default Configuration

- Host: `0.0.0.0`
- Port: `5000` (or `PORT` env variable)
- LLM Model: `llama-3.3-70b-versatile`
- Voice: Hindi greeting, English responses

## Need Help?

Check the browser console (F12) for detailed error messages and logs.
