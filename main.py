from flask import Flask
from flask import render_template
import argparse

app = Flask(__name__)

@app.route("/homepage")
def index():
    return render_template("layout.html")

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=5000)
    args = parser.parse_args()
    app.run(debug=True, port=args.port)
