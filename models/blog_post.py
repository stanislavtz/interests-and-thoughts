from sqlalchemy.orm import relationship

from config.db_config import db


# CONFIGURE TABLE
class BlogPost(db.Model):
    __tablename__ = 'blog_posts'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=True, nullable=False)
    subtitle = db.Column(db.String(250), nullable=False)
    date = db.Column(db.String(250), nullable=False)
    body = db.Column(db.Text, nullable=False)
    img_url = db.Column(db.String(250), nullable=False)
    author_name = db.Column(db.String(250), nullable=False)

    # Create reference to the User object, the "posts" refers to the posts property in the User class.
    author = relationship("User", back_populates="posts")
    # Create Foreign Key, "users.id" the users refers to the tabel name of User.
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))

    comments = relationship("Comment", back_populates="comment_post")
