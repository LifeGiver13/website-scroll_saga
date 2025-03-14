from flask import Flask, render_template, request, url_for, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import pymysql
import os
import json  # Required for SQLAlchemy MySQL connection

# Initialize Flask app
app = Flask(__name__)

# Set the folder for uploaded cover images
app.config["UPLOAD_FOLDER"] = "static/uploaded_cover_page"

# Configure MySQL connection for SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://life_giver:lifegiver13@localhost/scroll_saga'
# Disable modification tracking for performance
db = SQLAlchemy(app)  # Initialize SQLAlchemy with Flask app

# Define the Novel model


class Novel(db.Model):
    __tablename__ = "novel_listings"  # Ensure table name matches the database
    novel_id = db.Column(db.Integer, primary_key=True)
    novel_title = db.Column(db.String(255), nullable=False)
    author = db.Column(db.String(255), nullable=False)
    genre = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    cover_image = db.Column(db.String(255), nullable=True)
    # Defaults to current date
    publish_date = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        """Convert the novel object to a dictionary."""
        return {
            "novel_id": self.novel_id,
            "novel_title": self.novel_title,
            "author": self.author,
            "genre": self.genre,
            "description": self.description,
            "cover_image": self.cover_image,
            "publish_date": self.publish_date.strftime('%Y-%m-%d') if self.publish_date else None
        }


@app.route("/register")
def register():
    return render_template("signUp.html", page_title="Sign Up")


@app.route("/profile")
def profile():
    return render_template("user_details.html", page_title="Profile")


@app.route("/admin_panel")
def panel():
    novels = Novel.query.all()  # Fetch all novels from the database
    novels_data = [novel.to_dict()
                   for novel in novels]
    return render_template("admin_dashboard.html", page_title="Admin Panel", novels=novels_data)


@app.route("/landing_page")
def novel_list():
    novels = Novel.query.all()  # Fetch all novels from the database
    novels_data = [novel.to_dict()
                   for novel in novels]  # Convert to dictionaries
    return render_template("index.html", novels=novels_data, date=datetime.utcnow().strftime('%Y-%m-%d'))


@app.route("/add_novel", methods=["GET", "POST"])
def add_novel():
    if request.method == "POST":
        novel_title = request.form["novel_title"]
        author = request.form["author"]
        genre = request.form["genre"]
        description = request.form["description"]
        cover_image = request.files["cover_image"]

        if cover_image:
            cover_path = os.path.join(
                app.config["UPLOAD_FOLDER"], cover_image.filename)  # Define the file path
            cover_image.save(cover_path)
        else:
            filename = None

        new_novel = Novel(novel_title=novel_title, author=author,
                          genre=genre, description=description, cover_image=filename)
        db.session.add(new_novel)
        print(new_novel)
        db.session.commit()
        return redirect(url_for("panel"))

    return render_template("add_novel.html")


@app.route("/edit_novel/<int:novel_id>", methods=["GET", "POST"])
def edit_novel(novel_id):
    novel = Novel.query.get(novel_id)
    if request.method == "POST":
        novel.novel_title = request.form["novel_title"]
        novel.author = request.form["author"]
        novel.genre = request.form["genre"]
        db.session.commit()
        return redirect(url_for("panel"))
    return render_template("edit_novel_form.html", novel=novel)


@app.route("/delete_novel/<int:novel_id>", methods=["POST"])
def delete_novel(novel_id):
    novel = Novel.query.get_or_404(novel_id)
    db.session.delete(novel)
    db.session.commit()
    return redirect(url_for("panel"))


@app.route("/about")
def about():
    return render_template("default_page.html", page_title="About Us")


# Run the Flask app
if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # Ensure tables are created before running
    app.run(debug=True)
