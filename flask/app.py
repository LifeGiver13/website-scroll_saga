from flask import Flask, render_template


app = Flask(__name__)


@app.route('/landing_page')
def style():
    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True)
