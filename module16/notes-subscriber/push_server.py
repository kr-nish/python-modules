from flask import Flask, request
app = Flask(__name__)

@app.route("/push", methods=["POST"])
def push_handler():
    message = request.get_json()
    print(f"Push recived: {message["message"]["data"]}")
    return 'ACK', 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8081)