from flask import Flask, render_template


app = Flask(__name__)


@app.route("/login")
def login():
    return render_template("login.html", page_title="About Us")


@app.route("/register")
def register():
    return render_template("signUp.html", page_title="About Us")


@app.route("/profile")
def profile():
    return render_template("user_details.html", page_title="About Us")


@app.route("/admin_panel")
def panel():
    return render_template("admin_pannel.html", page_title="About Us")


@app.route('/landing_page')
def style():
    return render_template("index.html", page_title="Welcome to Scroll Saga")


@app.route("/about")
def about():
    return render_template("default_page.html", page_title="About Us")


if __name__ == "__main__":
    app.run(debug=True)
