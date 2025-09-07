from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from . import db, login_manager


class User(UserMixin, db.Model):
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True)   
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)  # ✅ хранение пароля
    role = db.Column(db.String(20), default="user")  # user, moderator, admin

    # связи
    likes = db.relationship("Like", back_populates="user", cascade="all, delete-orphan")
    videos = db.relationship("Video", back_populates="user", cascade="all, delete-orphan")  # ✅ добавил связь "пользователь → видео"

    # методы работы с паролем
    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    @property
    def is_admin(self) -> bool:
        return self.role == "admin"

    @property
    def is_moderator(self) -> bool:
        return self.role == "moderator"

    def __repr__(self):
        return f"<User {self.username} (role={self.role})>"


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


class Category(db.Model):
    __tablename__ = "category"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)

    videos = db.relationship("Video", back_populates="category", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Category {self.name}>"


class Video(db.Model):
    __tablename__ = "video"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, default="")
    filename = db.Column(db.String(255), nullable=False)
    thumbnail = db.Column(db.String(255), nullable=True)
    original_name = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    category_id = db.Column(db.Integer, db.ForeignKey("category.id"), nullable=False)
    category = db.relationship("Category", back_populates="videos")

    # 🔥 связь с автором
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    user = db.relationship("User", back_populates="videos")

    views = db.Column(db.Integer, default=0)

    likes = db.relationship("Like", back_populates="video", cascade="all, delete-orphan")

    def like_count(self):
        return Like.query.filter_by(video_id=self.id).count()

    def is_liked_by(self, user: User) -> bool:
        if not user or not user.is_authenticated:
            return False
        return db.session.query(Like.id).filter_by(user_id=user.id, video_id=self.id).first() is not None

    def __repr__(self):
        return f"<Video {self.title} (views={self.views})>"


class Like(db.Model):
    __tablename__ = "like"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=True)
    video_id = db.Column(db.Integer, db.ForeignKey("video.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    guest_id = db.Column(db.String(64), nullable=True, index=True)

    # связи
    user = db.relationship("User", back_populates="likes")
    video = db.relationship("Video", back_populates="likes")

    def __repr__(self):
        return f"<Like video={self.video_id} user={self.user_id} guest={self.guest_id}>"