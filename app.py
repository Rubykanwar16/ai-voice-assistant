from flask import Flask, render_template, request, send_file

# ✅ FIRST create app
app = Flask(__name__)

# ✅ THEN use routes
@app.route('/')
def index():
    return render_template('index.html')


@app.route('/process_audio', methods=['POST'])
def process_audio():
    try:
        print("Request received")

        audio = request.files.get('audio')

        if audio is None:
            print("No audio received")
            return "No audio file", 400

        file_path = "input.wav"
        audio.save(file_path)

        print("Audio saved successfully")

        return send_file(file_path, mimetype="audio/wav")

    except Exception as e:
        print("ERROR:", e)
        return str(e), 500


# ✅ ALWAYS at bottom
if __name__ == "__main__":
    app.run(debug=True)