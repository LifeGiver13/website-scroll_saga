from flask import Flask, render_template, request, url_for, redirect, session, flash, jsonify
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

# Set the folder for uploaded profile photo
app.config["UPLOAD_FOLDER2"] = "static/images"

# Configure MySQL connection for SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://life_giver:lifegiver13@localhost/scroll_saga'
# Disable modification tracking for performance
db = SQLAlchemy(app)  # Initialize SQLAlchemy with Flask app

# Define the Novel model

app.config['TEMPLATES_AUTO_RELOAD'] = True


class Novel(db.Model):
    __tablename__ = "novel_listings"  # Ensure table name matches the database
    novel_id = db.Column(db.Integer, primary_key=True)
    novel_title = db.Column(db.String(255), nullable=False)
    author = db.Column(db.String(255), nullable=False)
    genre = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    cover_image = db.Column(db.String(255), nullable=True)
    theme = db.Column(db.String(255), nullable=True)
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
            "theme": self.theme,
            "publish_date": self.publish_date.strftime('%Y-%m-%d') if self.publish_date else None
        }


class Users(db.Model):
    __tablename__ = "users"
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), nullable=False)
    email_address = db.Column(db.String(255), nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(255), nullable=False)
    profile_photo = db.Column(db.Text, nullable=True, default="default.png")
    user_bio = db.Column(db.String(255), nullable=True, default="None")

    def to_dict(self):
        """Convert the user object to a dictionary."""
        return {
            "user_id": self.user_id,
            "username": self.username,
            "email_address": self.email_address,
            "password": self.password,
            "role": self.role,
            "profile_photo": self.profile_photo,
            "user_bio": self.user_bio if self.user_bio else "None"
        }
    # Relationship with Users table


user = db.relationship("Users", backref="reviews")


class Reviews(db.Model):
    __tablename__ = "reviews"  # Ensure table name matches the database
    review_id = db.Column(db.Integer, primary_key=True)
    novel_id = db.Column(db.Integer, nullable=True)
    user_id = db.Column(db.Integer, nullable=False)
    rating = db.Column(db.Integer, nullable=False, default=0)
    novel_name = db.Column(db.String(225), nullable=False)
    review_text = db.Column(db.String(225), nullable=False)
    publish_time = db.Column(db.DateTime, default=datetime.utcnow)
    username = db.Column(db.String(255), nullable=False)
    profile_photo = db.Column(db.Text, nullable=True, default="default.png")

    def to_dict(self):
        """Convert the novel object to a dictionary."""
        return {
            "review_id": self.review_id,
            "novel_id": self.novel_id,
            "rating": self.rating,
            "review_text": self.review_text,
            "novel_name": self.novel_name,
            "publish_time": self.publish_time.strftime('%Y-%m-%d'),
            "chapters": self.user_id,
            "username": self.username,
            "profile_photo": self.profile_photo,

        }


class BookList(db.Model):
    __tablename__ = 'book_list'
    bookList_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    novel_id = db.Column(db.Integer, db.ForeignKey('novel_listings.novel_id'))

    user = db.relationship("Users", backref="book_list")
    novel = db.relationship("Novel", backref="saved_by_users")

    def to_dict(self):
        return {
            "bookList_id": self.bookList_id,
            "user_id": self.user_id,
            "novel_id": self.novel_id
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


@app.route("/register", methods=["POST", "GET"])
def register():
    username = request.form.get("registerUsername")
    email = request.form.get("registerEmail")
    password = request.form.get("registerPassword")
    confirm_password = request.form.get("confirmPassword")
    fileName = request.files.get('profile')
    user_bio = request.form.get("user_bio")
    # Check if passwords match
    if password != confirm_password:
        flash("Passwords do not match. Please try again.", "danger")
        return redirect(url_for("novel_list"))

    # Check if the email already exists
    existing_email = Users.query.filter_by(email_address=email).first()
    if existing_email:
        flash("Email already exists. Please log in.", "warning")
        return redirect(url_for("login"))

    # Check if the username already exists
    existing_username = Users.query.filter_by(username=username).first()
    if existing_username:
        flash("Username already taken. Please choose another one.", "warning")
        return redirect(url_for("register"))

    # Default profile photo
    profile_photo_filename = "default.png"

    # If a file was uploaded and it's not empty
    if fileName and fileName.filename != '':
        # Save the file to your uploads directory (adjust the path if needed)
        upload_folder = os.path.join(
            app.root_path, 'static/images')
        os.makedirs(upload_folder, exist_ok=True)  # Ensure the folder exists
        file_path = os.path.join(upload_folder, fileName.filename)
        fileName.save(file_path)

        profile_photo_filename = fileName.filename

    # Hash the password
    hashed_password = generate_password_hash(password, method="pbkdf2:sha256")

    files = []
    if fileName and fileName.filename != '':
        files.append(
            ("inline", (fileName.filename, fileName.stream, fileName.mimetype)))
        print(files)
        url = "https://api.mailgun.net/v3/sandbox731194d37470413e8c548a52a345d7c7.mailgun.org/messages"

        data = {
            "from": "WIMHouse@sandbox731194d37470413e8c548a52a345d7c7.mailgun.org",
            "to": [email],
            "subject": "Welcome to WIM House(Info from the API)",
            "html": f"""
    <html>
    <body style="margin: 0; padding: 0; background-color: #f3e5ab;">
        <div style="
            max-width: 600px;
            margin: 30px auto;
            padding: 40px;
            background-image: url('https://sdmntprwestus.oaiusercontent.com/files/00000000-47c4-5230-affb-aedb600b6668/raw?se=2025-04-06T22%3A51%3A35Z&sp=r&sv=2024-08-04&sr=b&scid=e37f039a-0900-5c20-900b-a7f5f8a2410d&skoid=de76bc29-7017-43d4-8d90-7a49512bae0f&sktid=a48cca56-e6da-484e-a814-9c849652bcb3&skt=2025-04-06T07%3A09%3A14Z&ske=2025-04-07T07%3A09%3A14Z&sks=b&skv=2024-08-04&sig=2QAzqOu8VcmLgFDBer5LwdvDHM58KQG6CBTw5%2BX/WEo%3D'); /* placeholder parchment image */
            background-size: cover;
            background-repeat: no-repeat;
            background-position: center;
            border: 10px solid #a87c4f;
            border-radius: 20px;
            font-family: 'Georgia', serif;
            color: #4b3621;
            box-shadow: 0 0 20px rgba(0, 0, 0, 0.4);
        ">
            <h1 style="text-align: center; font-size: 28px;">📜 Welcome to Scroll Saga 📜</h1>
            <p style="font-size: 18px; line-height: 1.6;">
                Dear <strong>{username}</strong>,<br><br>
                You have been chosen to embark on a sacred journey through the realms of imagination.
                The Novel World awaits you — a haven where reality fades and fantasy thrives.
            </p>
            <p style="font-size: 18px; line-height: 1.6;">
                Read stories, support the writers, and help bring these worlds to life — maybe even on screen one day! ✨
            </p>
            <p style="font-size: 18px; line-height: 1.6;">
                Here is your uploaded Profile photo (if any) and your passport to this otherworldly domain.
            </p>
            <p style="font-size: 16px; text-align: right;">- The WIM House Guild</p>
        </div>
    </body>
    </html>
    """,
        }
        files = files
        auth = ("api", "04e7193703a33f3123f6eb1cf196e9bb-24bda9c7-1550a8f8")

        response = requests.post(url, auth=auth, data=data, files=files)
        print(response.status_code)
        print("Response Status Code: ", response.json())

    # Assign a default profile picture

    # Create a new user
    new_user = Users(
        username=username,
        email_address=email,
        password=hashed_password,
        role="user",
        profile_photo=profile_photo_filename,
        # Set default image
        # Change from "None" (string) to actual None (NULL in database)
        user_bio=user_bio
    )

    flash("Registration successful! Please log in.", "success")
    db.session.add(new_user)
    db.session.commit()

    return redirect(url_for("novel_list"))
# Logout Route


@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("novel_list"))

# Home route (for listing novels)


@app.route("/update_profile", methods=["POST"])
def update_profile():
    if 'username' not in session:
        return redirect("/login")

    user = Users.query.filter_by(username=session['username']).first()

    if user:
        user.username = request.form['username']
        user.email_address = request.form['email_address']
        user.user_bio = request.form['user_bio']

        # Handle profile photo upload
        photo = request.files.get('profile_photo')
        if photo and photo.filename != '':
            filename = secure_filename(photo.filename)
            photo.save(os.path.join('static/images', filename))
            user.profile_photo = filename

        db.session.commit()
        flash("Profile updated successfully!", "success")

    return redirect(url_for('novel_list'))


@app.route("/profile")
def profile():
    if 'username' not in session:
        return redirect("/login")

    user = Users.query.filter_by(username=session['username']).first()
    return render_template("profile.html", current_user=user)


@app.route("/admin_panel", methods=["GET", "POST"])
def panel():
    novels = Novel.query.all()  # Fetch all novels from the database
    novels_data = [novel.to_dict()
                   for novel in novels]
    return render_template("admin_dashboard.html", page_title="Admin Panel", novels=novels_data)


@app.route("/users", methods=["POST", "GET"])
def users():
    users = Users.query.all()
    usersdata = [user.to_dict()
                 for user in users]
    return render_template("total_users.html", page_title="Users", users=usersdata)


@app.route("/comments", methods=["POST", "GET"])
def comments():
    reviews = Reviews.query.all()

    review_data = [review.to_dict()
                   for review in reviews]
    return render_template("comments.html", page_title="Reviews", reviews=review_data)


@app.route("/")
def novel_list():
    novels = Novel.query.all()  # Fetch all novels from the database
    novels_data = [novel.to_dict()
                   for novel in novels]  # Convert to dictionaries
    current_user = None
    if 'username' in session:
        current_user = Users.query.filter_by(
            username=session['username']).first()

    return render_template("index.html", novels=novels_data, current_user=current_user, date=datetime.utcnow().strftime('%Y-%m-%d'))


@app.route("/add_novel", methods=["POST"])
def add_novel():
    print(request.form)
    if request.method == "POST":
        novel_title = request.form["novel_title"]
        author = request.form["author"]
        genre = request.form["genre"]
        description = request.form["description"]
        cover_image = request.files["cover_image"]
        theme = request.form["theme"]
        publish_date = request.form["publish_date"]
        if cover_image:
            filename = secure_filename(cover_image.filename)
            cover_image.save(os.path.join(
                app.config["UPLOAD_FOLDER"], filename))
        else:
            filename = None
        new_novel = Novel(novel_title=novel_title, author=author,
                          genre=genre, description=description, cover_image=filename, theme=theme, publish_date=publish_date)
        db.session.add(new_novel)
        db.session.commit()
    print(new_novel)
    return jsonify(new_novel[0])
    # return jsonify({"message": "Novel added successfully!", "novel_id": new_novel.novel_title})
    # return render_template("add_novel.html")


@app.route('/search')
def search():
    query = request.args.get('query')
    results = []

    if query:
        # Example: search in novel titles or descriptions
        results = Novel.query.filter(
            Novel.novel_title.ilike(f'%{query}%') |
            Novel.description.ilike(f'%{query}%')
        ).all()

    return render_template('search_results.html', query=query, results=results)

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


@app.route("/delete_novel/<int:novel_id>", methods=["POST", "DELETE"])
def delete_novel(novel_id):
    novel = Novel.query.get_or_404(novel_id)
    db.session.delete(novel)
    db.session.commit()
    return redirect(url_for("panel"))


@app.route("/delete_comment/<int:review_id>", methods=["POST", "DELETE"])
def delete_comment(review_id):
    review = Reviews.query.get_or_404(review_id)
    db.session.delete(review)
    db.session.commit()
    return redirect(url_for("panel"))


@app.route("/delete_user/<int:user_id>", methods=["POST", "DELETE"])
def delete_user(user_id):
    user = Users.query.get_or_404(user_id)
    db.session.delete(user)
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
        novel.theme = request.form.get("theme")
        novel.publish_date = request.form.get("publish_date")

        # Save changes
        db.session.commit()

        return redirect(url_for("panel"))

    # return render_template("edit_novel_form.html", novel=novel)


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
                novel_name=novel_title,
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


@app.route('/my_booklist', methods=["POST", "GET"])
def my_booklist():
    saved = BookList.query.filter_by(user_id=["user_id"]).all()
    novels = [entry.novel for entry in saved]
    return render_template('booksList.html', novels=novels)


@app.route('/save_novel/<int:novel_id>', methods=['POST'])
def save_novel(novel_id):
    already_saved = BookList.query.filter_by(
        user_id=session["user_id"], novel_id=novel_id).first()
    if not already_saved:
        new_entry = BookList(user_id=session["user_id"], novel_id=novel_id)
        db.session.add(new_entry)
        db.session.commit()
    return jsonify(status="saved")


@app.route('/unsave_novel/<int:novel_id>', methods=['POST'])
def unsave_novel(novel_id):
    saved = BookList.query.filter_by(
        user_id=session["user_id"], novel_id=novel_id).first()
    if saved:
        db.session.delete(saved)
        db.session.commit()
    return jsonify(status="unsaved")


# Run the Flask app
if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # Ensure tables are created before running
    app.run(debug=True)
