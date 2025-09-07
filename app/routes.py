import os
import uuid
from flask import (
    Blueprint, render_template, redirect, url_for, request, flash, jsonify,
    send_from_directory, current_app, session, make_response
)
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from .models import Video, Category, Like, db
from .forms import UploadForm
from .utils import role_required  # ✅ декоратор для ролей


bp = Blueprint("main", __name__)

# ---------- ХЕЛПЕРЫ ----------

def save_file(file, folder, prefix_uuid=True):
    """Сохраняет файл в указанную папку, возвращает новое имя."""
    os.makedirs(folder, exist_ok=True)
    filename = secure_filename(file.filename)
    if prefix_uuid:
        filename = f"{uuid.uuid4().hex}_{filename}"
    filepath = os.path.join(folder, filename)
    file.save(filepath)
    return filename


# ---------- КОНТЕКСТ ----------

@bp.app_context_processor
def inject_categories():
    categories = Category.query.order_by(Category.name.asc()).all()
    return dict(all_categories=categories)


# ---------- ПУБЛИЧНЫЕ СТРАНИЦЫ ----------

@bp.route("/", methods=["GET"])
def index():
    page = request.args.get("page", 1, type=int)
    query = request.args.get("q", "").strip()

    videos_query = Video.query.order_by(Video.created_at.desc())
    if query:
        videos_query = videos_query.filter(Video.title.ilike(f"%{query}%"))

    videos = videos_query.paginate(page=page, per_page=6, error_out=False)
    return render_template("index.html", videos=videos, selected_category=None, search_query=query)


@bp.route("/category/<int:category_id>")
def videos_by_category(category_id):
    category = Category.query.get_or_404(category_id)
    page = request.args.get("page", 1, type=int)
    query = request.args.get("q", "").strip()

    videos_query = Video.query.filter_by(category_id=category.id).order_by(Video.created_at.desc())
    if query:
        videos_query = videos_query.filter(Video.title.ilike(f"%{query}%"))

    videos = videos_query.paginate(page=page, per_page=6, error_out=False)
    return render_template("index.html", videos=videos, selected_category=category, search_query=query)


# ---------- ОТДАЧА ФАЙЛОВ (видео + превью) ----------

@bp.route("/uploads/<path:filename>")
def uploaded_file(filename):
    """Отдаёт видео из static/uploads с кешированием"""
    upload_dir = os.path.join(current_app.static_folder, "uploads")
    response = make_response(send_from_directory(upload_dir, filename))
    response.headers["Cache-Control"] = "public, max-age=604800"  # 7 дней
    return response


@bp.route("/thumbnails/<path:filename>")
def uploaded_thumbnail(filename):
    """Отдаёт превью (обложки) из static/thumbnails с кешированием"""
    thumb_dir = os.path.join(current_app.static_folder, "thumbnails")
    response = make_response(send_from_directory(thumb_dir, filename))
    response.headers["Cache-Control"] = "public, max-age=2592000"  # 30 дней
    return response


# ---------- ЗАГРУЗКА ВИДЕО (админ + модератор) ----------

@bp.route("/upload", methods=["GET", "POST"])
@login_required
@role_required("admin", "moderator")
def upload_video():
    form = UploadForm()
    form.set_category_choices()

    if form.validate_on_submit():
        upload_dir = os.path.join(current_app.static_folder, "uploads")
        video_filename = save_file(form.video.data, upload_dir, prefix_uuid=True)

        video = Video(
            title=form.title.data,
            description=form.description.data or "",
            filename=video_filename,
            original_name=form.video.data.filename,
            category_id=form.category.data,
            user_id=current_user.id
        )

        if form.thumbnail.data:
            thumb_dir = os.path.join(current_app.static_folder, "thumbnails")
            thumb_filename = save_file(form.thumbnail.data, thumb_dir)
            video.thumbnail = thumb_filename

        db.session.add(video)
        db.session.commit()

        flash("Видео успешно загружено!", "success")
        return render_template("upload_success.html", video=video)

    return render_template("upload.html", form=form)


# ---------- ПРОСМОТР ВИДЕО + ЛАЙКИ + ПОХОЖИЕ ----------

@bp.route("/video/<int:video_id>")
def video_detail(video_id):
    video = Video.query.get_or_404(video_id)

    # увеличиваем просмотры
    video.views = (video.views or 0) + 1
    db.session.commit()

    # проверка лайка
    if current_user.is_authenticated:
        liked = video.is_liked_by(current_user)
    else:
        guest_id = session.get("guest_id")
        liked = False
        if guest_id:
            liked = Like.query.filter_by(video_id=video.id, guest_id=guest_id).first() is not None

    # показываем до 8 похожих видео
    related_videos = (
        Video.query.filter(Video.category_id == video.category_id, Video.id != video.id)
        .order_by(Video.created_at.desc())
        .limit(8)
        .all()
    )

    return render_template("video_detail.html", video=video, liked=liked, related_videos=related_videos)


@bp.route("/video/<int:video_id>/like", methods=["POST"])
def like_video(video_id):
    video = Video.query.get_or_404(video_id)

    if current_user.is_authenticated:
        like = Like.query.filter_by(user_id=current_user.id, video_id=video.id).first()
        if like:
            db.session.delete(like)
            liked = False
        else:
            db.session.add(Like(user_id=current_user.id, video_id=video.id))
            liked = True
    else:
        if "guest_id" not in session:
            session["guest_id"] = str(uuid.uuid4())
        guest_id = session["guest_id"]

        like = Like.query.filter_by(guest_id=guest_id, video_id=video.id).first()
        if like:
            db.session.delete(like)
            liked = False
        else:
            db.session.add(Like(guest_id=guest_id, video_id=video.id))
            liked = True

    db.session.commit()
    return jsonify({"liked": liked, "count": video.like_count()})


# ---------- АДМИН: КАТЕГОРИИ ----------

@bp.route("/admin/categories")
@login_required
@role_required("admin")
def admin_categories():
    categories = Category.query.order_by(Category.name.asc()).all()
    return render_template("admin/categories.html", categories=categories)


@bp.route("/admin/categories/add", methods=["POST"])
@login_required
@role_required("admin")
def admin_add_category():
    name = request.form.get("name", "").strip()
    if not name:
        flash("Имя категории не может быть пустым.", "warning")
    elif Category.query.filter_by(name=name).first():
        flash("Такая категория уже существует.", "warning")
    else:
        db.session.add(Category(name=name))
        db.session.commit()
        flash("Категория добавлена.", "success")
    return redirect(url_for("main.admin_categories"))


@bp.route("/admin/categories/delete/<int:category_id>")
@login_required
@role_required("admin")
def admin_delete_category(category_id):
    category = Category.query.get_or_404(category_id)
    if category.videos:
        flash("Нельзя удалить категорию: в ней есть видео!", "danger")
    else:
        db.session.delete(category)
        db.session.commit()
        flash("Категория удалена!", "success")
    return redirect(url_for("main.admin_categories"))


@bp.route("/admin/categories/edit/<int:category_id>", methods=["GET", "POST"])
@login_required
@role_required("admin")
def admin_edit_category(category_id):
    category = Category.query.get_or_404(category_id)

    if request.method == "POST":
        new_name = request.form.get("name", "").strip()
        if not new_name:
            flash("Имя категории не может быть пустым.", "warning")
        elif Category.query.filter(Category.name == new_name, Category.id != category.id).first():
            flash("Такая категория уже существует!", "warning")
        else:
            category.name = new_name
            db.session.commit()
            flash("Категория обновлена!", "success")
            return redirect(url_for("main.admin_categories"))

    return render_template("admin/edit_category.html", category=category)


# ---------- АДМИН: ВИДЕО ----------

@bp.route("/admin/videos")
@login_required
@role_required("admin")
def admin_videos():
    page = request.args.get("page", 1, type=int)
    pagination = Video.query.order_by(Video.created_at.desc()).paginate(page=page, per_page=9, error_out=False)
    return render_template("admin/dashboard.html", pagination=pagination)


@bp.route("/admin/videos/delete/<int:video_id>", methods=["POST"])
@login_required
@role_required("admin")
def admin_delete_video(video_id):
    video = Video.query.get_or_404(video_id)

    # удаление видеофайла
    if video.filename:
        video_path = os.path.join(current_app.static_folder, "uploads", video.filename)
        if os.path.exists(video_path):
            try:
                os.remove(video_path)
            except PermissionError:
                flash(f"Не удалось удалить файл {video.filename}, он занят.", "warning")

    # удаление превью
    if video.thumbnail:
        thumb_path = os.path.join(current_app.static_folder, "thumbnails", video.thumbnail)
        if os.path.exists(thumb_path):
            try:
                os.remove(thumb_path)
            except PermissionError:
                flash(f"Не удалось удалить превью {video.thumbnail}, оно занято.", "warning")

    # удаляем запись из БД
    db.session.delete(video)
    db.session.commit()

    flash("Видео удалено!", "success")
    return redirect(url_for("main.admin_videos"))


@bp.route("/admin/videos/edit/<int:video_id>", methods=["GET", "POST"])
@login_required
@role_required("admin")
def admin_edit_video(video_id):
    video = Video.query.get_or_404(video_id)
    form = UploadForm(obj=video)
    form.set_category_choices()

    if form.validate_on_submit():
        video.title = form.title.data
        video.description = form.description.data
        video.category_id = form.category.data

        if form.video.data:
            upload_dir = os.path.join(current_app.static_folder, "uploads")
            new_video_filename = save_file(form.video.data, upload_dir, prefix_uuid=True)

            old_path = os.path.join(upload_dir, video.filename)
            if video.filename and os.path.exists(old_path):
                os.remove(old_path)

            video.filename = new_video_filename
            video.original_name = form.video.data.filename

        if form.thumbnail.data:
            thumb_dir = os.path.join(current_app.static_folder, "thumbnails")
            new_thumb_filename = save_file(form.thumbnail.data, thumb_dir)

            if video.thumbnail:
                old_thumb_path = os.path.join(thumb_dir, video.thumbnail)
                if os.path.exists(old_thumb_path):
                    os.remove(old_thumb_path)

            video.thumbnail = new_thumb_filename

        db.session.commit()
        flash("Видео обновлено!", "success")
        return redirect(url_for("main.admin_videos"))

    return render_template("admin/edit_video.html", form=form, video=video)

# ---------- КОНТАКТЫ ----------

@bp.route("/contacts")
def contacts():
    return render_template("Contacts.html")

# ---------- О ПРОЕКТЕ ----------

@bp.route("/about")
def about():
    return render_template("about.html")