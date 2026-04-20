import speech_recognition as sr
import pyttsx3
import pywhatkit
import datetime
import wikipedia
import pyjokes

listener = sr.Recognizer()
engine = pyttsx3.init()
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[1].id if len(voices) > 1 else voices[0].id)


def talk(text):
    engine.say(text)
    engine.runAndWait()


def take_command():
    command = ''
    try:
        with sr.Microphone() as source:
            print('listening...')
            listener.adjust_for_ambient_noise(source, duration=0.5)
            voice = listener.listen(source, timeout=5, phrase_time_limit=8)
            command = listener.recognize_google(voice)
            command = command.lower()
            if 'alexa' in command:
                command = command.replace('alexa', '').strip()
                print(command)
    except sr.WaitTimeoutError:
        pass
    except sr.UnknownValueError:
        pass
    except sr.RequestError:
        talk('Speech service is unavailable.')
    except Exception as e:
        print(f'Error: {e}')
    return command


def run_alexa():
    command = take_command()
    if not command:
        return
    print(command)
    if 'play' in command:
        song = command.replace('play', '').strip()
        talk('playing ' + song)
        pywhatkit.playonyt(song)
    elif 'time' in command:
        time = datetime.datetime.now().strftime('%I:%M %p')
        talk('Current time is ' + time)
    elif 'who the heck is' in command:
        person = command.replace('who the heck is', '').strip()
        try:
            info = wikipedia.summary(person, sentences=1, auto_suggest=False)
            print(info)
            talk(info)
        except wikipedia.exceptions.DisambiguationError:
            talk('There are multiple results. Please be more specific.')
        except wikipedia.exceptions.PageError:
            talk('I could not find that on Wikipedia.')
        except Exception:
            talk('Wikipedia is unavailable right now.')
    elif 'date' in command:
        talk('sorry, I have a headache')
    elif 'are you single' in command:
        talk('I am in a relationship with wifi')
    elif 'joke' in command:
        talk(pyjokes.get_joke())
    else:
        talk('Please say the command again.')


while True:
    run_alexa()
