from flask import Flask, request, jsonify

app = Flask(__name__)
latest_sequence = None

@app.route("/upload_sequence", methods=["POST"])
def upload_sequence():
    global latest_sequence
    latest_sequence = request.get_json()["sequence"]
    return jsonify({"status": "ok"})

@app.route("/get_sequence", methods=["GET"])
def get_sequence():
    return jsonify({"sequence": latest_sequence})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=50007)