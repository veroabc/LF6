from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/ask", methods=['POST'])
def hello_world():
    content = request.json
    print(content)
    return "<p>Hello, World!</p>"