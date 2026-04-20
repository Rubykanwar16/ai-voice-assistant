import speech_recognition as sr
import pyttsx3
import pywhatkit
from assistant import process_command

listener = sr.Recognizer()
engine = pyttsx3.init()
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[1].id if len(voices) > 1 else voices[0].id)


def talk(text):
    print(f'Alexa: {text}')
    engine.say(text)
    engine.runAndWait()


def take_command():
    command = ''
    try:
        with sr.Microphone() as source:
            print('Listening...')
            listener.adjust_for_ambient_noise(source, duration=0.5)
            voice = listener.listen(source, timeout=5, phrase_time_limit=8)
            command = listener.recognize_google(voice)
            command = command.lower()
            print(f'You said: {command}')
    except sr.WaitTimeoutError:
        pass
    except sr.UnknownValueError:
        pass
    except sr.RequestError:
        talk('Speech service is unavailable.')
    except Exception as e:
        print(f'Error: {e}')
    return command


def run_cli():
    talk('Alexa is ready. Say a command.')
    while True:
        command = take_command()
        if not command:
            continue

        result = process_command(command)
        talk(result['text'])

        if result['action'] == 'play_youtube':
            try:
                pywhatkit.playonyt(result['value'])
            except Exception:
                talk('Could not open YouTube right now.')
