from flask import Flask
from line_handlers.follow import test_function

app = Flask(__name__)

@app.route("/")
def home():
    return test_function()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)