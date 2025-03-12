from flask import Flask, render_template, request
import pymysql
import mysql.connector

app = Flask(__name__)

app.config["UPLOAD_FOLDER"] = "static/uploaded_cover_page"


conn = mysql.connector.connect(

    host="localhost",
    user="life_giver",
    password="lifegiver13",
    database="scroll_saga"

)

cursor = conn.cursor(dictionary=True)


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
    cursor.execute(
        "SELECT novel_id, novel_title,  author, genre,description, cover_image FROM novel_listings")

    novels = cursor.fetchall()
    conn.commit()
    return render_template("admin_dashboard.html", novels=novels, row_count=cursor.rowcount)


@app.route("/landing_page")
def novel_list():
    cursor.execute(
        "SELECT novel_id, novel_title,  author, genre,description, cover_image FROM novel_listings")

    novels = cursor.fetchall()
    conn.commit()
    return render_template("index.html", novels=novels)


@app.route("/about")
def about():
    return render_template("default_page.html", page_title="About Us")


if __name__ == "__main__":
    app.run(debug=True)
