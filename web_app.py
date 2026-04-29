"""
AI Voice Assistant - Flask Web Application
Production-ready implementation with error handling and CORS support
"""
import asyncio
import base64
import datetime
import os
import re

from flask import Flask, jsonify, render_template, request
from dotenv import load_dotenv

# Try to import Flask-CORS
try:
    from flask_cors import CORS
    HAS_CORS = True
except ImportError:
    HAS_CORS = False

# Load environment variables
load_dotenv()

# Get absolute path for templates folder
TEMPLATE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')

# Create Flask app with absolute path to templates
app = Flask(__name__, template_folder=TEMPLATE_DIR)
app.config['JSON_SORT_KEYS'] = False

# Enable CORS
if HAS_CORS:
    CORS(app, resources={r"/*": {"origins": "*"}})

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
            client = Groq(api_key=api_key, max_retries=3)
            print("✓ Groq client initialized successfully")
            return True
        else:
            print("⚠ WARNING: GROQ_API_KEY not set in .env file")
            print("  LLM functionality will be disabled")
            return False
    except ImportError:
        print("✗ ERROR: Groq library not installed")
        print("  Run: pip install -r requirements.txt")
        return False
    except Exception as e:
        print(f"✗ ERROR initializing Groq: {e}")
        return False

def get_client():
    try:
        from groq import Groq
        api_key = os.environ.get("GROQ_API_KEY", "").strip()
        return Groq(api_key=api_key, max_retries=3) if api_key else None
    except Exception:
        return None

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

# Ensure clients are initialized immediately upon import
init_clients()

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
    fresh_client = get_client()
    if not fresh_client:
        return "API key not configured"
    
    conversation_history.append({"role": "user", "content": user_input})
    messages = [{"role": "system", "content": get_system_prompt()}] + conversation_history
    
    tools_list = get_tools()
    kwargs = {
        "model": LLM_MODEL,
        "messages": messages,
        "max_tokens": 200,
        "temperature": 0.7,
    }
    if tools_list:
        kwargs["tools"] = tools_list
        kwargs["tool_choice"] = "auto"

    resp = fresh_client.chat.completions.create(**kwargs)
    
    msg = resp.choices[0].message
    
    if msg.tool_calls:
        tc = msg.tool_calls[0]
        tool_result = execute_tool(tc.function.name, tc.function.arguments)
        conversation_history.append({
            "role": "assistant",
            "content": msg.content or "",
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
        
        resp2 = fresh_client.chat.completions.create(
            model=LLM_MODEL,
            messages=[{"role": "system", "content": get_system_prompt()}] + conversation_history,
            max_tokens=200,
            temperature=0.7,
        )
        response = _clean(resp2.choices[0].message.content)
    else:
        response = _clean(msg.content or "")
    
    conversation_history.append({"role": "assistant", "content": response})
    return response


# CORS Headers - Enhanced
@app.before_request
def handle_preflight():
    if request.method == "OPTIONS":
        response = jsonify({"status": "ok"})
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        return response, 200

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
    try:
        return render_template("index.html")
    except Exception as e:
        print(f"Index error: {e}")
        return jsonify({"error": f"Could not load index: {str(e)}"}), 500


@app.route("/health", methods=["GET", "OPTIONS"])
def health():
    """Health check"""
    if request.method == "OPTIONS":
        return jsonify({"status": "ok"}), 200
    fresh_client = get_client()
    status = "healthy" if fresh_client else "degraded"
    return jsonify({"status": status}), 200


@app.route("/greet", methods=["GET", "OPTIONS"])
def greet():
    """Greeting endpoint"""
    if request.method == "OPTIONS":
        return jsonify({"status": "ok"}), 200
    
    try:
        audio_bytes = run_async(generate_speech(GREETING, VOICE_HI))
        audio_b64 = base64.b64encode(audio_bytes).decode()
        return jsonify({"text": GREETING, "audio": audio_b64}), 200
    except Exception as e:
        print(f"Greet error: {e}")
        return jsonify({"error": f"Greeting failed: {str(e)}", "text": GREETING, "audio": ""}), 500


@app.route("/voice", methods=["POST", "OPTIONS"])
def voice():
    """Voice processing endpoint"""
    if request.method == "OPTIONS":
        return jsonify({"status": "ok"}), 200
    
    fresh_client = get_client()
    if not fresh_client:
        return jsonify({"error": "API not configured"}), 503
    
    audio_file = request.files.get("audio")
    if not audio_file:
        return jsonify({"error": "No audio received"}), 400
    
    # Transcribe using requests to bypass httpx multipart issues on Vercel
    try:
        import requests
        api_key = os.environ.get("GROQ_API_KEY", "").strip()
        headers = {
            "Authorization": f"Bearer {api_key}"
        }
        files = {
            "file": ("recording.webm", audio_file.read(), "audio/webm")
        }
        data = {
            "model": WHISPER_MODEL
        }
        resp = requests.post(
            "https://api.groq.com/openai/v1/audio/transcriptions",
            headers=headers,
            files=files,
            data=data,
            timeout=20
        )
        if resp.status_code != 200:
            return jsonify({"error": f"Transcription API error {resp.status_code}: {resp.text}"}), 500
            
        transcript = resp.json().get("text", "").strip()
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
    return jsonify({"error": "Endpoint not found"}), 404

@app.errorhandler(405)
def method_not_allowed(e):
    return jsonify({"error": f"Method {request.method} not allowed on this endpoint"}), 405

@app.errorhandler(500)
def server_error(e):
    print(f"Server error: {e}")
    return jsonify({"error": "Internal server error"}), 500


def run_web():
    """Run Flask app"""
    print("\n" + "="*70)
    print("  AI VOICE ASSISTANT - STARTING FLASK SERVER")
    print("="*70)
    
    # Check if templates folder exists
    if not os.path.isdir(TEMPLATE_DIR):
        print(f"\n✗ ERROR: Templates folder not found at: {TEMPLATE_DIR}")
        print("  Make sure index.html exists in the templates/ folder\n")
        return
    
    print(f"\n✅ Templates folder found: {TEMPLATE_DIR}")
    
    # Initialize Groq client
    print("\n🔧 Initializing clients...")
    client_ok = init_clients()
    
    if not client_ok:
        print("⚠️  API key missing - voice features will not work")
    
    # Get configuration
    port = int(os.environ.get("PORT", 5000))
    host = "0.0.0.0"
    
    # Display configuration
    print(f"\n🔌 Server Configuration:")
    print(f"   - Host: {host}")
    print(f"   - Port: {port}")
    print(f"   - Access URL: http://localhost:{port}")
    print(f"   - Debug Mode: OFF (Production mode)")
    
    # List available routes
    routes = [str(rule) for rule in app.url_map.iter_rules() if 'static' not in str(rule)]
    print(f"\n📍 Available Routes:")
    for route in sorted(routes):
        print(f"   {route}")
    
    print("\n" + "="*70)
    print("  🚀 Server is starting - Press Ctrl+C to stop")
    print("="*70 + "\n")
    
    try:
        app.run(debug=False, host=host, port=port, threaded=True)
    except OSError as e:
        if "Address already in use" in str(e):
            print(f"\n❌ ERROR: Port {port} is already in use")
            print(f"   Try: PORT=5001 python main.py")
        else:
            print(f"\n❌ ERROR: {e}")
        return
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        return


if __name__ == "__main__":
    run_web()
