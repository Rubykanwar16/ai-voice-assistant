"""
AI Voice Assistant - Production Flask App for Render.com
Clean, error-handled implementation for cloud deployment
"""
import asyncio
import base64
import datetime
import os
import re

from flask import Flask, jsonify, render_template, request
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Create Flask app
app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False

# Initialize clients
client = None
conversation_history = []

def init_clients():
    """Initialize Groq client safely"""
    global client
    try:
        from groq import Groq
        api_key = os.environ.get("GROQ_API_KEY")
        if api_key:
            client = Groq(api_key=api_key)
            print("✓ Groq client initialized")
        else:
            print("⚠ GROQ_API_KEY not set")
    except Exception as e:
        print(f"✗ Error initializing Groq: {e}")

def get_tools():
    """Get tools for LLM"""
    try:
        from tools import TOOLS
        return TOOLS
    except Exception:
        return []

def execute_tool(name, args):
    """Execute a tool"""
    try:
        from tools import execute_tool as exec_tool
        return exec_tool(name, args)
    except Exception as e:
        return f"Tool error: {str(e)}"

# Constants
GREETING = "Namaskar, Mera Name Ruby hai, mai aapki kya sahayta kar sakti hoon"
VOICE_EN = "en-US-JennyNeural"
VOICE_HI = "hi-IN-SwaraNeural"
WHISPER_MODEL = "whisper-large-v3-turbo"
LLM_MODEL = "llama-3.3-70b-versatile"


def run_async(coro):
    """Run async coroutine"""
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


async def generate_speech(text, voice=VOICE_EN):
    """Generate speech using edge-tts"""
    import edge_tts
    try:
        communicate = edge_tts.Communicate(text, voice)
        chunks = []
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                chunks.append(chunk["data"])
        return b"".join(chunks)
    except Exception:
        # Fallback to alternate voice
        alt_voice = VOICE_HI if voice == VOICE_EN else VOICE_EN
        communicate = edge_tts.Communicate(text, alt_voice)
        chunks = []
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                chunks.append(chunk["data"])
        return b"".join(chunks)


def _clean(text: str) -> str:
    """Clean LLM response"""
    return re.sub(r"<function=\w+>.*?</function>", "", text, flags=re.DOTALL).strip()


def get_system_prompt():
    """Get system prompt for LLM"""
    now = datetime.datetime.now().strftime("%A, %d %B %Y, %I:%M %p")
    return (
        f"You are Ruby, a smart and friendly AI voice assistant. "
        f"Current date and time: {now}. "
        f"Keep responses concise (2-3 sentences) since they will be spoken aloud. "
        f"Be natural and conversational. "
        f"Avoid markdown formatting like bullet points, asterisks, or headers — plain sentences only."
    )


def ask_llm(user_input):
    """Get LLM response"""
    if not client:
        return "API key not configured"
    
    conversation_history.append({"role": "user", "content": user_input})
    messages = [{"role": "system", "content": get_system_prompt()}] + conversation_history
    
    resp = client.chat.completions.create(
        model=LLM_MODEL,
        messages=messages,
        tools=get_tools(),
        tool_choice="auto",
        max_tokens=200,
        temperature=0.7,
    )
    
    msg = resp.choices[0].message
    
    if msg.tool_calls:
        tc = msg.tool_calls[0]
        tool_result = execute_tool(tc.function.name, tc.function.arguments)
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


# CORS Headers
@app.after_request
def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    return response


# Routes
@app.route("/", methods=["GET"])
def index():
    """Serve main page"""
    return render_template("index.html")


@app.route("/health", methods=["GET"])
def health():
    """Health check"""
    status = "healthy" if client else "degraded"
    return jsonify({"status": status}), 200


@app.route("/greet", methods=["GET", "OPTIONS"])
def greet():
    """Greeting endpoint"""
    if request.method == "OPTIONS":
        return jsonify({"status": "ok"}), 200
    
    try:
        audio_bytes = run_async(generate_speech(GREETING, VOICE_HI))
        audio_b64 = base64.b64encode(audio_bytes).decode()
        return jsonify({"text": GREETING, "audio": audio_b64})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/voice", methods=["POST", "OPTIONS"])
def voice():
    """Voice processing endpoint"""
    if request.method == "OPTIONS":
        return jsonify({"status": "ok"}), 200
    
    if not client:
        return jsonify({"error": "API not configured"}), 503
    
    audio_file = request.files.get("audio")
    if not audio_file:
        return jsonify({"error": "No audio received"}), 400
    
    # Transcribe
    try:
        transcription = client.audio.transcriptions.create(
            model=WHISPER_MODEL,
            file=("recording.webm", audio_file.read(), "audio/webm"),
        )
        transcript = transcription.text.strip()
    except Exception as e:
        return jsonify({"error": f"Transcription failed: {str(e)}"}), 500
    
    if not transcript:
        return jsonify({"error": "Could not understand audio"}), 400
    
    # Get LLM response
    try:
        response_text = ask_llm(transcript)
    except Exception as e:
        return jsonify({"error": f"LLM failed: {str(e)}"}), 500
    
    # Generate speech
    try:
        audio_bytes = run_async(generate_speech(response_text))
        audio_b64 = base64.b64encode(audio_bytes).decode()
    except Exception as e:
        return jsonify({"error": f"TTS failed: {str(e)}"}), 500
    
    return jsonify({
        "transcript": transcript,
        "response": response_text,
        "audio": audio_b64,
    })


@app.route("/reset", methods=["POST", "OPTIONS"])
def reset():
    """Reset conversation"""
    if request.method == "OPTIONS":
        return jsonify({"status": "ok"}), 200
    
    global conversation_history
    conversation_history.clear()
    return jsonify({"status": "ok"})


@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Not found"}), 404


@app.errorhandler(500)
def server_error(e):
    return jsonify({"error": "Server error"}), 500


def run_web():
    """Run Flask app"""
    init_clients()
    
    if not client:
        print("\n⚠ WARNING: GROQ_API_KEY not set!")
        print("Set it in Render Settings → Environment Variables\n")
    
    port = int(os.environ.get("PORT", 5000))
    print(f"\n✓ AI Voice Assistant starting on port {port}")
    app.run(debug=False, host="0.0.0.0", port=port)


if __name__ == "__main__":
    run_web()
