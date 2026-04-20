# AI Voice Assistant

A simple Alexa-style Python voice assistant built with:

- `pyttsx3` for text-to-speech
- `speech_recognition` + `pyaudio` for voice input
- `pywhatkit` for playing songs on YouTube
- `wikipedia` for short person lookups
- `pyjokes` for joke responses

## What it does

Say **"Alexa"** followed by a command:

| Command | Response |
|---|---|
| `Alexa play Lahore` | Opens YouTube and plays the song |
| `Alexa what's the time` | Says the current time |
| `Alexa who the heck is Elon Musk` | Reads a Wikipedia summary |
| `Alexa tell me a joke` | Tells a random joke |
| `Alexa what's the date` | Says it has a headache |
| `Alexa are you single` | Gives a playful answer |

## Setup

### 1. Create a virtual environment (Python 3.12 required)

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

## Run

```bash
python app.py
```

## Notes

- `pyaudio` requires **Python 3.12** — it does not build on Python 3.13+
- Needs a working microphone
- `recognize_google()` requires an internet connection
- `pywhatkit.playonyt()` opens the browser to play the song on YouTube
