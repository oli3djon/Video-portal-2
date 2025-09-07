from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, FileField, SubmitField, SelectField, PasswordField
from wtforms.validators import DataRequired, Length, Optional
from flask_wtf.file import FileAllowed
from .models import Category


class LoginForm(FlaskForm):
    """Форма авторизации"""
    username = StringField(
        "Имя пользователя",
        validators=[DataRequired(), Length(min=3, max=80)]
    )
    password = PasswordField("Пароль", validators=[DataRequired()])
    submit = SubmitField("Войти")


class UploadForm(FlaskForm):
    """Форма загрузки / редактирования видео"""
    title = StringField("Название", validators=[DataRequired(), Length(min=1, max=200)])
    description = TextAreaField("Описание", validators=[Length(max=500)])

    # Обложка (теперь необязательная)
    thumbnail = FileField(
        "Обложка",
        validators=[
            Optional(),
            FileAllowed(["jpg", "jpeg", "png"], "Только JPG или PNG!")
        ]
    )

    # Видео (теперь необязательное)
    video = FileField(
        "Видео",
        validators=[
            Optional(),
            FileAllowed(["mp4", "mov", "webm", "mkv"], "Только видеофайлы!")
        ]
    )

    category = SelectField("Категория", coerce=int, validators=[DataRequired()])

    submit = SubmitField("Сохранить")

    def set_category_choices(self):
        """Заполнение списка категорий динамически"""
        self.category.choices = [
            (c.id, c.name) for c in Category.query.order_by(Category.name).all()
        ]
