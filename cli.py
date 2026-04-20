import os
import re
import datetime
import winsound
import speech_recognition as sr
import pyttsx3
from groq import Groq
from dotenv import load_dotenv

from tools import TOOLS, execute_tool

load_dotenv()

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

listener = sr.Recognizer()
engine = pyttsx3.init()
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[1].id if len(voices) > 1 else voices[0].id)

conversation_history = []

def get_system_prompt():
    now = datetime.datetime.now().strftime("%A, %d %B %Y, %I:%M %p")
    return (
        f"You are Ruby, a smart and friendly AI voice assistant. "
        f"Current date and time: {now}. "
        f"Keep responses concise (2-3 sentences) since they will be spoken aloud. "
        f"Be natural and conversational. "
        f"Avoid markdown formatting like bullet points, asterisks, or headers — plain sentences only."
    )

LLM_MODEL = "llama-3.3-70b-versatile"


def _clean(text: str) -> str:
    return re.sub(r"<function=\w+>.*?</function>", "", text, flags=re.DOTALL).strip()


def talk(text):
    print(f'Ruby: {text}')
    engine.say(text)
    engine.runAndWait()


def take_command():
    command = ''
    try:
        with sr.Microphone() as source:
            listener.adjust_for_ambient_noise(source, duration=0.5)
            winsound.Beep(880, 150)   # listening start
            print('Listening...')
            voice = listener.listen(source, timeout=5, phrase_time_limit=8)
            winsound.Beep(440, 120)   # listening stop
            command = listener.recognize_google(voice)
            print(f'You said: {command}')
    except sr.WaitTimeoutError:
        pass
    except sr.UnknownValueError:
        winsound.Beep(300, 200)       # error / not understood
        pass
    except sr.RequestError:
        talk('Speech service is unavailable.')
    except Exception as e:
        print(f'Error: {e}')
    return command


import re

def _clean(text: str) -> str:
    # Strip raw tool-call syntax the model sometimes leaks into response text
    return re.sub(r"<function=\w+>.*?</function>", "", text, flags=re.DOTALL).strip()


def ask_llm(user_input):
    conversation_history.append({"role": "user", "content": user_input})
    messages = [{"role": "system", "content": get_system_prompt()}] + conversation_history


    # First call — LLM decides whether to use a tool
    resp1 = client.chat.completions.create(
        model=LLM_MODEL,
        messages=messages,
        tools=TOOLS,
        tool_choice="auto",
        max_tokens=200,
        temperature=0.7,
    )
    msg = resp1.choices[0].message

    if msg.tool_calls:
        tc = msg.tool_calls[0]
        tool_result = execute_tool(tc.function.name, tc.function.arguments)
        print(f'[Tool: {tc.function.name}] {tool_result}')

        conversation_history.append({
            "role": "assistant",
            "content": msg.content,
            "tool_calls": [{
                "id": tc.id,
                "type": "function",
                "function": {"name": tc.function.name, "arguments": tc.function.arguments}
            }]
        })
        conversation_history.append({
            "role": "tool",
            "tool_call_id": tc.id,
            "content": tool_result
        })

        # Second call — natural response from tool result
        resp2 = client.chat.completions.create(
            model=LLM_MODEL,
            messages=[{"role": "system", "content": get_system_prompt()}] + conversation_history,
            max_tokens=200,
            temperature=0.7,
        )
        response = _clean(resp2.choices[0].message.content)
    else:
        response = _clean(msg.content)

    conversation_history.append({"role": "assistant", "content": response})
    return response


def run_cli():
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        print("\n  ERROR: GROQ_API_KEY not set. Create a .env file with your key.\n")
        return

    talk('Namaskar! Main Ruby hoon, aapki AI assistant. Aap mujhse kuch bhi pooch sakte hain.')

    while True:
        command = take_command()
        if not command:
            continue

        if any(word in command.lower() for word in ('exit', 'quit', 'stop', 'bye')):
            talk('Goodbye! Have a great day.')
            break

        try:
            response = ask_llm(command)
            talk(response)
        except Exception as e:
            talk('Sorry, something went wrong.')
            print(f'Error: {e}')
