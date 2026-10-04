import os
from flask import Flask, send_from_directory
from backend.database import init
from backend.routes import api
from ml import predict

FE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "frontend")
app = Flask(__name__, static_folder=FE, static_url_path="")
app.register_blueprint(api)
init()
predict.load()  # trains the model on first run if ml/model.joblib is missing

@app.route("/")
def home():
    return send_from_directory(FE, "index.html")

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
