from flask import Flask, jsonify

app = Flask(__name__)


@app.route("/")
def home():
    return jsonify({
        "service": "Service A",
        "status": "running",
        "message": "Welcome to the Zero Trust AWS project"
    })


@app.route("/health")
def health():
    return jsonify({
        "service": "Service A",
        "status": "healthy"
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)