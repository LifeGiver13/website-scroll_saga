from flask import Flask, render_template


app = Flask(__name__)


@app.route('/landing_page')
def style():
    return render_template("index.html", page_title="Welcome to Scroll Saga")


@app.route("/about")
def about():
    return render_template("default_page.html", page_title="About Us")


if __name__ == "__main__":
    app.run(debug=True)
