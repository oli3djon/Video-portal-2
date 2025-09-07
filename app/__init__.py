import os
from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager # type: ignore
from flask_migrate import Migrate
from werkzeug.middleware.proxy_fix import ProxyFix

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
login_manager.login_view = "auth.login"

# Изменяем стандартное сообщение Flask-Login
login_manager.login_message = "Авторизация обязательна для доступа к этой странице."
login_manager.login_message_category = "warning"


def create_app():
    app = Flask(__name__)
    app.wsgi_app = ProxyFix(app.wsgi_app)

    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret-key-change-me")
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(os.path.dirname(BASE_DIR), "videos.db")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    app.config["UPLOAD_FOLDER"] = os.path.join(os.path.dirname(BASE_DIR), "uploads")
    app.config["MAX_CONTENT_LENGTH"] = int(os.environ.get("UPLOAD_MAX_MB", "200")) * 1024 * 1024
    app.config["ALLOWED_EXTENSIONS"] = set(os.environ.get("ALLOWED_EXTENSIONS", "mp4,mov,webm,mkv").split(","))

    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    # ✅ Инициализация расширений
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    # 📌 Импортируем блюпринты
    from .routes import bp as main_bp
    from .auth import bp as auth_bp
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix="/auth")

    # ==============================
    # 🔹 Обработчики ошибок
    # ==============================
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template("404.html"), 404

    @app.errorhandler(500)
    def internal_error(e):
        return render_template("500.html"), 500

    @app.errorhandler(403)
    def forbidden(e):
        return render_template("403.html"), 403

    # ==============================
    # 🔹 Кеширование
    # ==============================
    @app.after_request
    def add_cache_headers(response):
        """
        Добавляем заголовки кеша для статики и медиа
        """
        # Статика (CSS, JS, картинки, обложки)
        if "static" in request.path or "thumbnails" in request.path:
            response.headers["Cache-Control"] = "public, max-age=2592000"  # 30 дней

        # Видео
        if "uploads" in request.path:
            response.headers["Cache-Control"] = "public, max-age=604800"  # 7 дней

        return response

    return app
