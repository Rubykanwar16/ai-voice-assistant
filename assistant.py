import datetime
import wikipedia
import pyjokes


def process_command(command):
    """Returns dict: {text, action, value}"""
    command = command.lower().strip()
    if 'alexa' in command:
        command = command.replace('alexa', '').strip()

    if not command:
        return {'text': 'Yes?', 'action': None, 'value': None}

    if 'play' in command:
        song = command.replace('play', '').strip()
        return {'text': f'Playing {song} on YouTube.', 'action': 'play_youtube', 'value': song}

    if 'time' in command:
        t = datetime.datetime.now().strftime('%I:%M %p')
        return {'text': f'Current time is {t}', 'action': None, 'value': None}

    if 'who the heck is' in command:
        person = command.replace('who the heck is', '').strip()
        try:
            info = wikipedia.summary(person, sentences=1, auto_suggest=False)
            return {'text': info, 'action': None, 'value': None}
        except wikipedia.exceptions.DisambiguationError:
            return {'text': 'Multiple results found. Please be more specific.', 'action': None, 'value': None}
        except wikipedia.exceptions.PageError:
            return {'text': f'Could not find {person} on Wikipedia.', 'action': None, 'value': None}
        except Exception:
            return {'text': 'Wikipedia is unavailable right now.', 'action': None, 'value': None}

    if 'date' in command:
        return {'text': 'Sorry, I have a headache.', 'action': None, 'value': None}

    if 'are you single' in command:
        return {'text': 'I am in a relationship with wifi.', 'action': None, 'value': None}

    if 'joke' in command:
        return {'text': pyjokes.get_joke(), 'action': None, 'value': None}

    return {'text': 'Please say the command again.', 'action': None, 'value': None}
