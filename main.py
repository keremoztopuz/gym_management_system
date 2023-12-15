<<<<<<< HEAD
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
=======
from flask import Flask
from flask import render_template

app = Flask(__name__)

@app.route('/')
def homepage():
    return render_template("homepage.html")

if __name__ == '__main__':
    app.run(debug=True)
>>>>>>> 82d6cfd335e793ab7fbd73851601d5503b3945d4
