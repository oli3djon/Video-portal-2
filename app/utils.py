import os, secrets
from flask import current_app
from werkzeug.utils import secure_filename
from functools import wraps
from flask import flash, redirect, url_for
from flask_login import current_user


def allowed_file(filename):
    ext = filename.rsplit('.', 1)[-1].lower()
    return '.' in filename and ext in current_app.config["ALLOWED_EXTENSIONS"]


def save_upload(file_storage):
    # генерация уникального имени и сохранение
    filename = secure_filename(file_storage.filename)
    base, ext = os.path.splitext(filename)
    unique = secrets.token_hex(8)
    final_name = f"{base}-{unique}{ext}"
    path = os.path.join(current_app.config["UPLOAD_FOLDER"], final_name)
    file_storage.save(path)
    return final_name


# --- Декоратор проверки роли ---
def role_required(*roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated or current_user.role not in roles:
                flash("У вас нет прав для доступа к этой странице.", "danger")
                return redirect(url_for("main.index"))
            return f(*args, **kwargs)
        return decorated_function
    return decorator
