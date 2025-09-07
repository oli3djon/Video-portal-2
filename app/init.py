import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SECRET_KEY'] = 'supersecret'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///videos.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Пути для загрузок
app.config['UPLOAD_FOLDER'] = os.path.join(app.static_folder, 'uploads')
app.config['THUMBNAIL_FOLDER'] = os.path.join(app.static_folder, 'thumbnails')

# Создаем папки, если нет
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['THUMBNAIL_FOLDER'], exist_ok=True)

db = SQLAlchemy(app)

from app import routes, models
with app.app_context():
    db.create_all()
