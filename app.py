
from flask import Flask, request, jsonify

app = Flask(__name__)
messages = []

@app.route('/send', methods = ['POST'])
def send_message():
    data = request.get_json()
    username = data.get('username')
    text = data.get('text')
    messages.append({'username': username, 'text' : text})
    return jsonify({'status' : 'ok'})

@app.route('/messages', methods = ['GET'])
def get_messages():
    return jsonify(messages)

if __name__ == '__main__':
    app.run(host = '0.0.0.0' , port = 5000)