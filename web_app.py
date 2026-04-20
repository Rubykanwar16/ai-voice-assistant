import urllib.parse
from flask import Flask, render_template, request, jsonify
from assistant import process_command

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/command', methods=['POST'])
def command():
    data = request.get_json()
    text = data.get('command', '').strip()
    if not text:
        return jsonify({'text': 'No command received.', 'action': None, 'value': None})

    result = process_command(text)

    if result['action'] == 'play_youtube':
        query = urllib.parse.quote(result['value'])
        result['url'] = f'https://www.youtube.com/results?search_query={query}'

    return jsonify(result)


def run_web():
    print('\n  Web assistant running at http://localhost:5000')
    print('  Open the URL in Chrome or Edge (Web Speech API required)\n')
    app.run(debug=False, port=5000)
