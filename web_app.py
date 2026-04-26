import asyncio
import base64
import datetime
import os
import re
import sys

import edge_tts
from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request

# Initialize Flask app first
app = Flask(__name__, template_folder='templates')

# Load environment variables
load_dotenv()

# Initialize Groq client safely
try:
    from groq import Groq
    api_key = os.environ.get("GROQ_API_KEY")
    if api_key:
        client = Groq(api_key=api_key)
    else:
        client = None
        print("WARNING: GROQ_API_KEY not set - AI features will not work")
except Exception as e:
    print(f"ERROR initializing Groq: {e}")
    client = None

# Import tools
try:
    from tools import TOOLS, execute_tool
except Exception as e:
    print(f"ERROR importing tools: {e}")
    TOOLS = []
    def execute_tool(name, args):
        return "Tool execution failed"

# Enable CORS for requests from port 5500
@app.after_request
def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    return response


@app.before_request
def before_request():
    """Check if API key is set"""
    if not client and request.path not in ['/health', '/']:
        return jsonify({"error": "GROQ_API_KEY not configured"}), 503

conversation_history = []

def _clean(text: str) -> str:
    return re.sub(r"<function=\w+>.*?</function>", "", text, flags=re.DOTALL).strip()


def get_system_prompt():
    now = datetime.datetime.now().strftime("%A, %d %B %Y, %I:%M %p")
    return (
        f"You are Ruby, a smart and friendly AI voice assistant. "
        f"Current date and time: {now}. "
        f"Keep responses concise (2-3 sentences) since they will be spoken aloud. "
        f"Be natural and conversational. "
        f"Avoid markdown formatting like bullet points, asterisks, or headers — plain sentences only."
    )

GREETING = "Namaskar, Mera Name Ruby hai, mai aapki kya sahayta kar sakti hoon"

VOICE_EN = "en-US-JennyNeural"
VOICE_HI = "hi-IN-SwaraNeural"
WHISPER_MODEL = "whisper-large-v3-turbo"
LLM_MODEL = "llama-3.3-70b-versatile"


def run_async(coro):
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


async def generate_speech(text, voice=VOICE_EN):
    """
    Generate speech audio from text using edge-tts.
    Falls back to alternative voice if main voice fails.
    """
    try:
        communicate = edge_tts.Communicate(text, voice)
        chunks = []
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                chunks.append(chunk["data"])
        return b"".join(chunks)
    except Exception as e:
        # Retry with alternative voice
        try:
            alt_voice = VOICE_HI if voice == VOICE_EN else VOICE_EN
            print(f"TTS failed with {voice}, retrying with {alt_voice}")
            communicate = edge_tts.Communicate(text, alt_voice)
            chunks = []
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    chunks.append(chunk["data"])
            return b"".join(chunks)
        except Exception as e2:
            # If TTS fails completely, raise with informative message
            raise Exception(f"Speech synthesis failed: {str(e)}. Please try again.") from e2


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

        # Store assistant tool-call message + tool result
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

        # Second call — generate natural response from tool result
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


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/health", methods=["GET"])
def health():
    """Health check endpoint for Render monitoring"""
    if client:
        return jsonify({"status": "healthy", "api_key": "configured"}), 200
    else:
        return jsonify({"status": "degraded", "api_key": "missing"}), 200


@app.route("/greet", methods=["GET", "OPTIONS"])
def greet():
    if not client:
        return jsonify({"error": "API key not configured. Set GROQ_API_KEY environment variable."}), 500
    try:
        audio_bytes = run_async(generate_speech(GREETING, VOICE_HI))
        audio_b64 = base64.b64encode(audio_bytes).decode()
        return jsonify({"text": GREETING, "audio": audio_b64})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/voice", methods=["POST", "OPTIONS"])
def voice():
    if not client:
        return jsonify({"error": "API key not configured. Set GROQ_API_KEY environment variable."}), 500
    
    audio_file = request.files.get("audio")
    if not audio_file:
        return jsonify({"error": "No audio received."}), 400

    # STT — Groq Whisper
    try:
        transcription = client.audio.transcriptions.create(
            model=WHISPER_MODEL,
            file=("recording.webm", audio_file.read(), "audio/webm"),
        )
        transcript = transcription.text.strip()
    except Exception as e:
        return jsonify({"error": f"Transcription failed: {e}"}), 500

    if not transcript:
        return jsonify({"error": "Could not understand audio."}), 400

    # LLM + tools
    try:
        response_text = ask_llm(transcript)
    except Exception as e:
        return jsonify({"error": f"LLM failed: {e}"}), 500

    # TTS — edge-tts
    try:
        audio_bytes = run_async(generate_speech(response_text))
        audio_b64 = base64.b64encode(audio_bytes).decode()
    except Exception as e:
        return jsonify({"error": f"TTS failed: {e}"}), 500

    return jsonify({
        "transcript": transcript,
        "response": response_text,
        "audio": audio_b64,
    })


@app.route("/reset", methods=["POST", "OPTIONS"])
def reset():
    conversation_history.clear()
    return jsonify({"status": "ok"})


def run_web():
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        print("\n  ERROR: GROQ_API_KEY not set in environment variables!\n")
        print("  For Render.com: Go to Settings → Environment and add GROQ_API_KEY\n")
        return
    port = int(os.environ.get("PORT", 5000))
    print(f"\n  AI Voice Assistant is running at http://localhost:{port}")
    print("  Open in Chrome or Edge\n")
    app.run(debug=False, host="0.0.0.0", port=port)
