from flask import render_template, request, jsonify, redirect, url_for, session, flash
from flask import Flask, render_template, request, url_for, redirect, session, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import pymysql
import os
import base64
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
ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "gif"}

# Set the folder for uploaded profile photo
app.config["UPLOAD_FOLDER2"] = "static/images"

# Configure MySQL connection for SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://life_giver:lifegiver13@localhost/scroll_saga'
# Disable modification tracking for performance
db = SQLAlchemy(app)  # Initialize SQLAlchemy with Flask app

# Define the Novel model
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}


app.config['TEMPLATES_AUTO_RELOAD'] = True


class Page(db.Model):
    __tablename__ = "pages"
    page_id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String(50), unique=True, nullable=False)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    image_filename = db.Column(db.String(100))
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "page_id": self.page_id,
            "slug": self.slug,
            "title": self.title,
            "content": self.content,
            "image_filename": self.image_filename,
            "updated_at": self.updated_at}


class Novel(db.Model):
    __tablename__ = "novel_listings"  # Ensure table name matches the database
    novel_id = db.Column(db.Integer, primary_key=True)
    novel_title = db.Column(db.String(255), nullable=False)
    author = db.Column(db.String(255), nullable=False)
    genre = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(255), nullable=True)
    cover_image = db.Column(db.String(255), nullable=True)
    theme = db.Column(db.String(255), nullable=True)
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
            "theme": self.theme,
            "publish_date": self.publish_date.strftime('%Y-%m-%d') if self.publish_date else None
        }
  # One-to-many relationship


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
    # novel_title = db.Column(
    #     db.String(225), nullable=False, )
    # username = db.Column(db.String(255), nullable=False)

    user = db.relationship("Users", backref="book_list")
    novel = db.relationship("Novel", backref="saved_by_users")

    def to_dict(self):
        return {
            "bookList_id": self.bookList_id,
            "user_id": self.user_id,
            "novel_id": self.novel_id,
            "novel_title": self.novel_title,
            "username": self.username
        }


class Chapters(db.Model):
    __tablename__ = 'chapters'

    chapter_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    novel_id = db.Column(db.Integer, db.ForeignKey(
        'novel_listings.novel_id'), nullable=False)
    novel_title = db.Column(db.String(255))
    # Used for order within the novel
    chapter_number = db.Column(db.Integer, nullable=False)
    chapter_name = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=False)
    novel = db.relationship('Novel', backref='chapters', lazy=True)

    __table_args__ = (
        db.UniqueConstraint('novel_id', 'chapter_name',
                            name='uix_novel_chapter_name'),
        db.UniqueConstraint('novel_id', 'chapter_number',
                            name='uix_novel_chapter_number')

    )

    def to_dict(self):
        return {
            "chapter_id": self.chapter_id,
            "novel_id": self.novel_id,
            "chapter_number": self.chapter_number,
            "chapter_name": self.chapter_name,
            "content": self.content,
            "novel_title": self.novel_title
        }


@app.route('/<slug>')
def show_page(slug):
    novels = Novel.query.all()
    page = Page.query.filter_by(slug=slug).first_or_404()
    return render_template(f'{slug}.html', page=page, novels=novels)


@app.route("/pages", methods=["POST", "GET"])
def pages():
    pages = Page.query.all()
    page_data = [page.to_dict()
                 for page in pages]
    return render_template("pages.html", page=page_data)


@app.route('/pages/<int:page_id>/update', methods=['PUT'])
def update_page(page_id):
    data = request.get_json()

    page = Page.query.get(page_id)
    if not page:
        return jsonify({'error': 'Page not found'}), 404

    page.slug = data.get('slug', page.slug)
    page.title = data.get('title', page.title)
    page.content = data.get('content', page.content)
    page.image_filename = data.get('image_filename', page.image_filename)

    db.session.commit()

    return jsonify({'success': True})


@app.route("/login", methods=["GET", "POST"])
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    user = Users.query.filter_by(username=username).first()

    if user and check_password_hash(user.password, password):
        session["user_id"] = user.user_id
        session["username"] = user.username
        return jsonify({"status": "success", "message": f"Welcome, {user.username}!"})

    return jsonify({"status": "danger", "message": "Invalid username or password."}), 401


@app.route("/register", methods=["POST", "GET"])
def register():
    data = request.get_json()
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")
    confirm_password = data.get("confirm_password")
    user_bio = data.get("bio")
    profile_base64 = data.get("profile_photo")

    # Validations
    if not all([username, email, password, confirm_password]):
        return jsonify({"status": "danger", "message": "Please fill in all required fields."}), 400

    if password != confirm_password:
        return jsonify({"status": "danger", "message": "Passwords do not match."}), 400

    if Users.query.filter_by(username=username).first():
        return jsonify({"status": "danger", "message": "Username already taken."}), 400

    if Users.query.filter_by(email_address=email).first():
        return jsonify({"status": "danger", "message": "Email already registered."}), 400

    # Handle profile photo (optional)
    profile_photo_filename = "default.png"
    if profile_base64:
        try:
            # Extract actual image data
            header, encoded = profile_base64.split(",", 1)
            # image/png, image/jpeg etc.
            ext = header.split("/")[1].split(";")[0]
            image_data = base64.b64decode(encoded)
            timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
            profile_photo_filename = f"{username}_{timestamp}.{ext}"
            image_path = os.path.join(
                app.root_path, 'static/images', profile_photo_filename)
            os.makedirs(os.path.dirname(image_path), exist_ok=True)

            with open(image_path, "wb") as f:
                f.write(image_data)
        except Exception as e:
            return jsonify({"status": "danger", "message": "Invalid profile image."}), 400

    # Create new user
    hashed_password = generate_password_hash(password, method="pbkdf2:sha256")
    # Send welcome email using Mailgun with profile photo attached
    if email:
        try:

            # Path to the saved profile photo
            image_path = os.path.join(
                app.root_path, 'static/images', profile_photo_filename)

            url = "https://api.mailgun.net/v3/sandbox731194d37470413e8c548a52a345d7c7.mailgun.org/messages"

            data = {
                "from": "WIMHouse@sandbox731194d37470413e8c548a52a345d7c7.mailgun.org",
                "to": [email],
                "subject": "Welcome to Scroll Saga ✨",
                "html": f"""
    <html>
    <body style="margin: 0; padding: 0; background-color: #f5deb3;">
        <div style="
            max-width: 600px;
            margin: 30px auto;
            padding: 40px;
            background-image: url('https://sdmntprwestus.oaiusercontent.com/files/00000000-47c4-5230-affb-aedb600b6668/raw?se=2025-04-06T22%3A51%3A35Z&sp=r&sv=2024-08-04&sr=b&scid=e37f039a-0900-5c20-900b-a7f5f8a2410d&skoid=de76bc29-7017-43d4-8d90-7a49512bae0f&sktid=a48cca56-e6da-484e-a814-9c849652bcb3&skt=2025-04-06T07%3A09%3A14Z&ske=2025-04-07T07%3A09%3A14Z&sks=b&skv=2024-08-04&sig=2QAzqOu8VcmLgFDBer5LwdvDHM58KQG6CBTw5%2BX/WEo%3D');
            background-size: cover;
            border: 10px solid #a87c4f;
            border-radius: 20px;
            font-family: Georgia, serif;
            color: #4b3621;
            box-shadow: 0 0 20px rgba(0, 0, 0, 0.4);">

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
                Your profile photo has been attached to this scroll — your passport to the saga.
            </p>
            <p style="font-size: 16px; text-align: right;">- The WIM House Guild</p>
        </div>
    </body>
    </html>
    """
            }

            files = [("attachment", (profile_photo_filename,
                      open(image_path, "rb").read()))]

            auth = ("api", "YOUR_API_KEY")

            response = requests.post(url, auth=auth, data=data, files=files)
            print("Mailgun response:", response.status_code)
        except Exception as e:
            print("Mailgun failed:", e)

    # files = []
    # if profile_base64 and profile_base64.filename != '':
    #     files.append(
    #         ("inline", (profile_base64.filename, profile_base64.stream, profile_base64.mimetype)))
    #     print(files)
    #     url = "https://api.mailgun.net/v3/sandbox731194d37470413e8c548a52a345d7c7.mailgun.org/messages"

    #     data = {
    #         "from": "WIMHouse@sandbox731194d37470413e8c548a52a345d7c7.mailgun.org",
    #         "to": [email],
    #         "subject": "Welcome to WIM House(Info from the API)",
    #         "html": f"""
    # <html>
    # <body style="margin: 0; padding: 0; background-color: #f3e5ab;">
    #     <div style="
    #         max-width: 600px;
    #         margin: 30px auto;
    #         padding: 40px;
    #         background-image: url('https://sdmntprwestus.oaiusercontent.com/files/00000000-47c4-5230-affb-aedb600b6668/raw?se=2025-04-06T22%3A51%3A35Z&sp=r&sv=2024-08-04&sr=b&scid=e37f039a-0900-5c20-900b-a7f5f8a2410d&skoid=de76bc29-7017-43d4-8d90-7a49512bae0f&sktid=a48cca56-e6da-484e-a814-9c849652bcb3&skt=2025-04-06T07%3A09%3A14Z&ske=2025-04-07T07%3A09%3A14Z&sks=b&skv=2024-08-04&sig=2QAzqOu8VcmLgFDBer5LwdvDHM58KQG6CBTw5%2BX/WEo%3D'); /* placeholder parchment image */
    #         background-size: cover;
    #         background-repeat: no-repeat;
    #         background-position: center;
    #         border: 10px solid #a87c4f;
    #         border-radius: 20px;
    #         font-family: 'Georgia', serif;
    #         color: #4b3621;
    #         box-shadow: 0 0 20px rgba(0, 0, 0, 0.4);
    #     ">
    #         <h1 style="text-align: center; font-size: 28px;">📜 Welcome to Scroll Saga 📜</h1>
    #         <p style="font-size: 18px; line-height: 1.6;">
    #             Dear <strong>{username}</strong>,<br><br>
    #             You have been chosen to embark on a sacred journey through the realms of imagination.
    #             The Novel World awaits you — a haven where reality fades and fantasy thrives.
    #         </p>
    #         <p style="font-size: 18px; line-height: 1.6;">
    #             Read stories, support the writers, and help bring these worlds to life — maybe even on screen one day! ✨
    #         </p>
    #         <p style="font-size: 18px; line-height: 1.6;">
    #             Here is your uploaded Profile photo (if any) and your passport to this otherworldly domain.
    #         </p>
    #         <p style="font-size: 16px; text-align: right;">- The WIM House Guild</p>
    #     </div>
    # </body>
    # </html>
    # """,
    #     }
    #     files = files
    #     auth = ("api", "04e7193703a33f3123f6eb1cf196e9bb-24bda9c7-1550a8f8")

    #     response = requests.post(url, auth=auth, data=data, files=files)
    #     print(response.status_code)
    #     print("Response Status Code: ", response.json())

    # Assign a default profile picture

    # Create a new user
    new_user = Users(
        username=username,
        email_address=email,
        password=hashed_password,
        role="user",
        profile_photo=profile_photo_filename,
        user_bio=user_bio
    )
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"status": "success", "message": "Registration successful! Please log in."})


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


@app.route("/update_novel/<int:novel_id>", methods=["PUT"])
def update_novel(novel_id):
    data = request.get_json()

    title = data.get("title")
    author = data.get("author")
    description = data.get("description")

    # Query novel from database
    novel = Novel.query.get(novel_id)

    if not novel:
        return jsonify({"error": "Novel not found"}), 404

    # Update fields if provided
    if title:
        novel.title = title
    if author:
        novel.author = author
    if description:
        novel.description = description

    db.session.commit()

    return jsonify({"message": "Novel updated successfully"}), 200


@app.route("/get_novel/<int:novel_id>", methods=["GET"])
def get_novel(novel_id):
    novel = Novel.query.get(novel_id)
    if not novel:
        return jsonify({"error": "Novel not found"}), 404

    return jsonify({
        "title": novel.novel_title,
        "author": novel.author,
        "description": novel.description
    }), 200


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/upload_cover", methods=["POST", "GET"])
def upload_cover():
    if "cover_image" not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files["cover_image"]

    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        unique_filename = f"{timestamp}_{filename}"
        file_path = os.path.join(app.config["UPLOAD_FOLDER"], unique_filename)
        file.save(file_path)
        return jsonify({"filename": unique_filename}), 200
    else:
        return jsonify({"error": "Invalid file type"}), 400


@app.route("/add_novel", methods=["POST"])
def add_novel():
    data = request.get_json()

    novel_title = data.get("novel_title")
    author = data.get("author")
    genre = data.get("genre")
    theme = data.get("theme")
    description = data.get("description")
    publish_date_str = data.get("publish_date")
    cover_image = data.get("cover_image", "default_cover.jpg")

    if not novel_title or not author:
        return jsonify({"error": "Title and author are required"}), 400

    # Convert publish_date string to datetime.date
    try:
        if publish_date_str:
            publish_date = datetime.strptime(
                publish_date_str, "%Y-%m-%d").date()
        else:
            publish_date = datetime.utcnow().date()
    except ValueError:
        return jsonify({"error": "Invalid publish date format. Use YYYY-MM-DD."}), 400

    # Create novel entry
    new_novel = Novel(
        novel_title=novel_title,
        author=author,
        genre=genre,
        theme=theme,
        description=description,
        cover_image=cover_image,
        publish_date=publish_date
    )

    db.session.add(new_novel)
    db.session.commit()

    return jsonify({
        "message": "Novel added successfully!",
        "novel_id": new_novel.novel_id,
        "novel_title": new_novel.novel_title
    })


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

    # Get all chapters of this novel
    chapters = Chapters.query.filter_by(
        novel_id=novel_id).order_by(Chapters.chapter_id).all()

    # Define the first chapter to display by default
    first_chapter = chapters[0] if chapters else None

    # Get reviews for this novel
    reviews = Reviews.query.filter_by(novel_id=novel_id).all()

    # Redirect if not logged in
    if 'username' not in session:
        return redirect(url_for("login"))

    # Handle POST request for new comment
    if request.method == "POST":
        if "user_id" not in session:
            flash("You need to be logged in to post a comment.", "danger")
            return redirect(url_for("login"))

    user = Users.query.get(session["user_id"])
    content = request.form.get("content")

    if content and user:
        new_review = Reviews(
            novel_id=novel_id,
            user_id=user.user_id,
            username=user.username,
            novel_name=novel_title,
            profile_photo=user.profile_photo,
            review_text=content,
            publish_time=datetime.utcnow()
        )
        db.session.add(new_review)
        db.session.commit()
        flash("Your comment has been posted!", "success")
        return redirect(url_for("novel_details_page", novel_id=novel_id, novel_title=novel_title))

    # Pass the novel, reviews, all chapters, and first chapter to the template
    return render_template(
        "details.html",
        novel=novel,
        reviews=reviews,
        chapters=chapters,
        chapter=first_chapter  # Single chapter to load initially
    )


@app.route('/chapter/<int:novel_id>/<int:chapter_number>', methods=['GET'])
def get_chapter(novel_id, chapter_number):
    # Get the chapter by novel_id and chapter_number
    chapter = Chapters.query.filter_by(
        novel_id=novel_id, chapter_number=chapter_number).first()

    if not chapter:
        return jsonify({'error': 'Chapter not found'}), 404

    # Find the next and previous chapters (by ID)
    next_chapter = Chapters.query.filter_by(
        novel_id=novel_id, chapter_number=chapter.chapter_number + 1).first()
    prev_chapter = Chapters.query.filter_by(
        novel_id=novel_id, chapter_number=chapter.chapter_number - 1).first()

    return jsonify({
        "chapter_name": chapter.chapter_name,
        "content": chapter.content,
        "previous_id": chapter.chapter_number - 1 if prev_chapter else None,
        "next_id": chapter.chapter_number + 1 if next_chapter else None
    })


@app.route('/chapters', methods=["POST", "GET"])
def chapters():
    if request.method == "POST":
        data = request.get_json()

        chapter_id = data.get("chapter_id")
        chapter_name = data.get("chapter_name")
        content = data.get("content")
        chapter_number = data.get("chapter_number")

        chapter = Chapters.query.filter_by(chapter_id=chapter_id).first()
        if not chapter:
            return jsonify({"error": "Chapter not found"}), 404

        if chapter_name:
            chapter.chapter_name = chapter_name
        if content:
            chapter.content = content
        if chapter_number:
            chapter.chapter_number = chapter_number

        db.session.commit()

        return jsonify({"message": "Chapter updated successfully", "chapter": chapter.to_dict()}), 200

    # GET method
    chapters = Chapters.query.all()
    chapter_data = [chapter.to_dict() for chapter in chapters]
    return render_template("chapters.html", chapters=chapter_data)


@app.route('/upload_chapter', methods=['POST', "GET"])
def upload_chapter():
    data = request.get_json()
    print("Received Data:", data)

    try:
        novel_id = data.get('novel_id')
        novel_title = data.get('novel_title')
        chapter_name = data.get('chapter_name')
        content = data.get('content')
        chapter_number = data.get('chapter_number')

        if not all([novel_id, novel_title, chapter_name, content, chapter_number]):
            return jsonify({'message': 'Missing data'}), 400

        # Check for duplicate chapter number for this novel
        existing_number = Chapters.query.filter_by(
            novel_id=novel_id,
            chapter_number=chapter_number
        ).first()

        if existing_number:
            return jsonify({'message': 'This chapter number already exists for this novel.'}), 409

        # Optional: Check for duplicate chapter name too
        existing_name = Chapters.query.filter_by(
            novel_id=novel_id,
            chapter_name=chapter_name
        ).first()

        if existing_name:
            return jsonify({'message': 'This chapter name already exists for this novel.'}), 409

        # Save new chapter
        new_chapter = Chapters(
            novel_id=novel_id,
            novel_title=novel_title,
            chapter_name=chapter_name,
            content=content,
            chapter_number=chapter_number
        )
        db.session.add(new_chapter)
        db.session.commit()

        return jsonify({'message': 'Chapter uploaded successfully', 'chapter_id': new_chapter.chapter_id})

    except Exception as e:
        db.session.rollback()
        print("UPLOAD ERROR:", e)
        return jsonify({'message': 'Error uploading chapter', 'error': str(e)}), 500


@app.route('/my_booklist', methods=["GET", "POST"])
def my_booklist():
    if "user_id" not in session:
        # Redirect to login if user is not logged in
        return redirect(url_for('login'))
    user_id = session["user_id"]
    saved = BookList.query.filter_by(user_id=user_id).all()
    novels = [entry.novel for entry in saved]
    return render_template("booksList.html", novels=novels)


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
