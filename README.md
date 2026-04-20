# AI Voice Assistant

This project is a simple Alexa-style Python voice assistant built with:

- `pyttsx3` for text-to-speech
- `speech_recognition` for voice input
- `sounddevice` for microphone recording
- `pywhatkit` for playing songs on YouTube
- `wikipedia` for short person lookups
- `pyjokes` for joke responses

## What it does

- If your speech contains `time`, it says the current time
- If your speech contains `play`, it opens YouTube and plays the requested song
- If your speech contains `who the heck is`, it reads a short Wikipedia summary
- If your speech contains `joke`, it tells a joke
- If your speech contains `date`, it says `sorry, I have a headache`
- If your speech contains `are you single`, it gives a playful answer
- If your speech contains `exit`, `quit`, `stop`, or `bye`, it closes the app

Example:

```text
Alexa play Lahore
```

This becomes:

```python
pywhatkit.playonyt("Lahore")
```

## Install

```bash
pip install pyttsx3 SpeechRecognition pywhatkit sounddevice wikipedia pyjokes
```

## Run

```bash
python app.py
```

## Notes

- `SpeechRecognition` needs a working microphone
- `recognize_google()` needs an internet connection
- The app records about 5 seconds of audio each time it listens
- `pywhatkit.playonyt()` opens the browser and plays the song on YouTube
- Wikipedia lookups also need an internet connection
