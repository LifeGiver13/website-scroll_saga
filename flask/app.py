from flask import Flask, render_template, request, url_for, redirect, session, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import pymysql
import os
import json  # Required for SQLAlchemy MySQL connection
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
import requests

# Initialize Flask app
app = Flask(__name__)
# set a secret key
app.secret_key = "kenko182kaneju7364&*(jacee)[2]&238#"

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
    chapters = db.Column(db.Integer, nullable=False, default=0)

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


class Users(db.Model):
    __tablename__ = "users"
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), nullable=False)
    email_address = db.Column(db.String(255), nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(255), nullable=False)
    profile_photo = db.Column(db.Text, nullable=True)
    user_bio = db.Column(db.String(255), nullable=False, default=0)

    def to_dict(self):
        """Convert the user object to a dictionary."""
        return {
            "user_id": self.user_id,
            "username": self.username,
            "email_address": self.email_address,
            "password": self.password,
            "role": self.role,
            "profile_photo": self.profile_photo,
            "user_bio": self.user_bio if self.user_bio else None
        }
    # Relationship with Users table


user = db.relationship("Users", backref="reviews")


class Reviews(db.Model):
    __tablename__ = "reviews"  # Ensure table name matches the database
    review_id = db.Column(db.Integer, primary_key=True)
    novel_id = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, nullable=False)
    rating = db.Column(db.Integer, nullable=False, default=0)
    review_text = db.Column(db.String(225), nullable=False)
    publish_time = db.Column(db.DateTime, default=datetime.utcnow)
    username = db.Column(db.String(255), nullable=False)
    profile_photo = db.Column(db.Text, nullable=False, default="default.png")

    def to_dict(self):
        """Convert the novel object to a dictionary."""
        return {
            "review_id": self.review_id,
            "novel_id": self.novel_id,
            "rating": self.rating,
            "review_text": self.review_text,
            "publish_time": self.publish_time.strftime('%Y-%m-%d'),
            "chapters": self.user_id,
            "user": self.username,
            "profile_photo": self.profile_photo,

        }


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("loginPassword")

        user = Users.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            session["user_id"] = user.user_id
            session["username"] = user.username
            flash(f"Welcome, {user.username}!", "success")
            return redirect(url_for("novel_list"))
        else:
            flash("Invalid username or password", "danger")
    return redirect(url_for("novel_list"))  # Reload the homepage


@app.route("/register", methods=["POST"])
def register():
    username = request.form.get("registerUsername")
    email = request.form.get("registerEmail")
    password = request.form.get("registerPassword")
    confirm_password = request.form.get("confirmPassword")

    # Check if passwords match
    if password != confirm_password:
        flash("Passwords do not match. Please try again.", "danger")
        return redirect(url_for("novel_list"))

    # Check if the email already exists
    existing_email = Users.query.filter_by(email_address=email).first()
    if existing_email:
        flash("Email already exists. Please log in.", "warning")
        return redirect(url_for("novel_list"))

    # Check if the username already exists
    existing_username = Users.query.filter_by(username=username).first()
    if existing_username:
        flash("Username already taken. Please choose another one.", "warning")
        return redirect(url_for("novel_list"))

    # Hash the password
    hashed_password = generate_password_hash(password, method="pbkdf2:sha256")

    # Assign a default profile picture
    default_profile_photo = "default.png"

    # Create a new user
    new_user = Users(
        username=username,
        email_address=email,
        password=hashed_password,
        role="user",
        profile_photo=default_profile_photo,  # Set default image
        # Change from "None" (string) to actual None (NULL in database)
        user_bio=None
    )

    # Save to database
    db.session.add(new_user)
    db.session.commit()

    flash("Registration successful! Please log in.", "success")
    return redirect(url_for("novel_list"))
# Logout Route


@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("novel_list"))

# Home route (for listing novels)


@app.route("/profile")
def profile():
    return render_template("user_details.html", page_title="Profile")


@app.route("/admin_panel", methods=["GET", "POST"])
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
            filename = secure_filename(cover_image.filename)
            cover_image.save(os.path.join(
                app.config["UPLOAD_FOLDER"], filename))
        else:
            filename = None
        new_novel = Novel(novel_title=novel_title, author=author,
                          genre=genre, description=description, cover_image=filename)
        db.session.add(new_novel)
        db.session.commit()
        return redirect(url_for("panel"))
    return render_template("add_novel.html")


# @app.route("/")
# def home():
#     # Replace with the actual API endpoint
#     api_url = "https://mangahook-api.vercel.app/?utm_source=chatgpt.com"
#     response = requests.get(api_url)

#     if response.status_code == 200:
#         novels = response.json()  # Convert response to Python dictionary
#     else:
#         novels = []  # Empty list if API request fails

#     # Pass data to Jinja template
#     return render_template("index.html", novels=novels)


@app.route("/delete_novel/<int:novel_id>", methods=["POST"])
def delete_novel(novel_id):
    novel = Novel.query.get_or_404(novel_id)
    db.session.delete(novel)
    db.session.commit()
    return redirect(url_for("panel"))


@app.route("/edit_novel/<int:novel_id>", methods=["GET", "POST"])
def edit_novel(novel_id):
    novel = Novel.query.get_or_404(novel_id)

    if request.method == "POST":
        novel.novel_title = request.form.get("novel_title")
        novel.author = request.form.get("author")
        novel.genre = request.form.get("genre")
        novel.description = request.form.get("description")
        novel.publish_date = request.form.get("publish_date")

        # Save changes
        db.session.commit()

        return redirect(url_for("panel"))

    return render_template("edit_novel_form.html", novel=novel)


@app.route("/novel/<int:novel_id>/<string:novel_title>", methods=["GET", "POST"])
def novel_details_page(novel_id, novel_title):
    novel = Novel.query.get_or_404(novel_id)
    reviews = Reviews.query.filter_by(novel_id=novel_id).all()

    if request.method == "POST":
        if "user_id" not in session:
            flash("You need to be logged in to post a comment.", "danger")
            return redirect(url_for("login"))

        user = Users.query.get(session["user_id"])  # Fetch the logged-in user
        content = request.form.get("content")

        if content and user:
            new_review = Reviews(
                novel_id=novel_id,
                user_id=user.user_id,  # Associate review with logged-in user
                username=user.username,  # Store username
                profile_photo=user.profile_photo,  # Store profile photo
                review_text=content,
                publish_time=datetime.utcnow()
            )
            db.session.add(new_review)
            db.session.commit()
            flash("Your comment has been posted!", "success")
            return redirect(url_for("novel_details_page", novel_id=novel_id, novel_title=novel_title))

    return render_template("details.html", novel=novel, reviews=reviews)


@app.route("/about")
def about():
    return render_template("default_page.html", page_title="About Us")


# Run the Flask app
if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # Ensure tables are created before running
    app.run(debug=True)
