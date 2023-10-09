import os
from datetime import date

from flask import Flask, render_template, redirect, url_for, flash, abort
from flask_bootstrap import Bootstrap5
from flask_ckeditor import CKEditor
from functools import wraps

from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, current_user, logout_user, LoginManager

from config.db_config import db

from forms.create_post import CreatePost
from forms.login_user import LoginUser
from forms.register_user import RegisterUser
from forms.comment import CommentForm

from models.blog_post import BlogPost
from models.user import User
from models.comment import Comment

app = Flask(__name__)

# CONNECT TO DB
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DB_URI", "sqlite:///blog.db")
db.init_app(app)

with app.app_context():
    db.create_all()

# CONFIG WTFORMS
app.config['SECRET_KEY'] = os.environ.get('FLASK_KEY')
Bootstrap5(app)
ckeditor = CKEditor(app)

# CONFIGURATE LOGIN MANAGER
login_manager = LoginManager()
login_manager.init_app(app)


# There should be an import statement up top
from flask_gravatar import Gravatar

# For adding profile images to the comment section
gravatar = Gravatar(app,
                    size=100,
                    rating='g',
                    default='retro',
                    force_default=False,
                    force_lower=False,
                    use_ssl=False,
                    base_url=None)


def admin_only(function):
    @wraps(function)
    def wrapper_function(*args, **kwargs):
        if current_user.id != 1:
            return abort(403)
        return function(*args, **kwargs)
    return wrapper_function


def not_authenticated(function):
    @wraps(function)
    def wrapper_function(*args, **kwargs):
        if current_user.is_authenticated:
            return redirect(url_for("get_all_posts"))
        return function(*args, **kwargs)
    return wrapper_function


# CREATE user_loader callback
@login_manager.user_loader
def load_user(user_id):
    return db.get_or_404(User, user_id)


@app.route("/register", methods=["GET", "POST"])
@not_authenticated
def register():
    register_form = RegisterUser()
    if register_form.validate_on_submit():
        current_password = register_form.data.get("password")
        current_re_password = register_form.data.get("repeat_password")

        if current_password == current_re_password:
            hashed_and_salted_password = generate_password_hash(current_password, method="pbkdf2:sha256", salt_length=16)

            new_user = User(
                username=register_form.data.get("username"),
                email=register_form.data.get("email"),
                password=hashed_and_salted_password,
            )

            try:
                db.session.add(new_user)
                db.session.commit()

                login_user(new_user)
                return redirect(url_for("get_all_posts"))
            except Exception:
                flash("User already exist")
                return redirect(url_for("login"))
        else:
            flash("Password not match")

    return render_template("register-user.html", form=register_form)


@app.route("/login", methods=["GET", "POST"])
@not_authenticated
def login():
    login_form = LoginUser()
    if login_form.validate_on_submit():
        username = login_form.data.get("username")
        user_password = login_form.data.get("password")

        try:
            logging_user = db.session.execute(db.select(User).filter_by(username=username)).scalar_one()

            if check_password_hash(logging_user.password, user_password):
                login_user(logging_user)
                return redirect(url_for("get_all_posts"))
            else:
                flash("Incorrect username or password")

        except Exception:
            flash("Username or password doesn't exists")

    return render_template("login-user.html", form=login_form)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("get_all_posts"))


@app.route('/')
def get_all_posts():
    # TODO: Query the database for all the posts. Convert the data to a python list.
    result = db.session.execute(db.select(BlogPost)).scalars()
    posts = result.all()
    return render_template("index.html", all_posts=posts)


# TODO: Add a route so that you can click on individual posts.
@app.route('/show-post/<int:post_id>', methods=["GET", "POST"])
def show_post(post_id):
    # TODO: Retrieve a BlogPost from the database based on the post_id
    requested_post = db.get_or_404(BlogPost, post_id)
    comment_form = CommentForm()

    if comment_form.validate_on_submit():
        new_comment = Comment(
            text=comment_form.data.get("comment").replace("<p>", "").replace("</p>", ""),
            author_id=current_user.id,
            post_id=post_id
        )

        db.session.add(new_comment)
        db.session.commit()

        return redirect(url_for("show_post", post_id=post_id))
    return render_template("post.html", post=requested_post, form=comment_form)


# TODO: add_new_post() to create a new blog post
@app.route("/new-post", methods=["GET", "POST"])
@login_required
@admin_only
def add_new_post():
    form = CreatePost()
    if form.validate_on_submit():
        new_post = BlogPost(
            title=form.data.get("title"),
            subtitle=form.data.get("subtitle"),
            date=date.today().strftime("%B %d, %Y"),
            body=form.data.get("body_text"),
            author=current_user,
            img_url=form.data.get("img_url"),
            author_name = form.data.get("author_name"),
            author_id=current_user.id
        )

        db.session.add(new_post)
        db.session.commit()

        return redirect(url_for("get_all_posts"))
    return render_template("make-post.html", form=form)


# TODO: edit_post() to change an existing blog post
@app.route("/edit-post/<int:post_id>", methods=["GET", "POST"])
@login_required
@admin_only
def edit_post(post_id):
    post_to_edit = db.get_or_404(BlogPost, post_id)

    form = CreatePost(
        title=post_to_edit.title,
        subtitle=post_to_edit.subtitle,
        body_text=post_to_edit.body,
        author_name=post_to_edit.author_name,
        img_url=post_to_edit.img_url
    )

    if form.validate_on_submit():
        post_to_edit.title = form.title.data
        post_to_edit.subtitle = form.subtitle.data
        post_to_edit.body = form.body_text.data
        post_to_edit.author_name = form.author_name.data
        post_to_edit.img_url = form.img_url.data

        db.session.commit()

        return redirect(url_for("show_post", post_id=post_to_edit.id))
    return render_template("make-post.html", form=form, is_edit=True)


# TODO: delete_post() to remove a blog post from the database
@app.route("/delete-post/<post_id>")
@login_required
@admin_only
def delete_post(post_id):
    post_to_delete = db.get_or_404(BlogPost, post_id)
    db.session.delete(post_to_delete)
    db.session.commit()

    return redirect(url_for("get_all_posts"))


# Below is the code from previous lessons. No changes needed.
@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


if __name__ == "__main__":
    app.run(debug=False)
