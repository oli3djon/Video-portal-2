# 🎬 Ваш корпоративный видеоцентр

Веб-приложение на **Flask**, позволяющее хранить, публиковать и просматривать видео внутри компании.  
Поддерживает роли пользователей, категории, лайки и удобную админку.

---

## 🚀 Возможности
- 🔑 Авторизация через логин/пароль (роли: **admin**, **moderator**, **user**).  
- 📂 Загрузка видео (поддержка форматов `mp4`, `mov`, `webm`, `mkv`).  
- 🖼 Превью (обложки видео).  
- 🗂 Категории видео.  
- 👀 Счётчик просмотров.  
- 👍 Лайки (для авторизованных и гостей).  
- ⚙️ Админка для управления категориями и видео.  

---

## 🛠 Установка и запуск

### 1. Клонировать проект
```bash
git clone <repo-url>
cd flask_video_portal_with_thumbnails_final
```

### 2. Создать виртуальное окружение
```bash
python -m venv .venv
source .venv/bin/activate   # Linux/macOS
.venv\Scripts\activate      # Windows
```

### 3. Установить зависимости
```bash
pip install -r requirements.txt
```

### 4. Инициализировать базу
```bash
flask --app manage.py init-db
```

### 5. Создать администратора
```bash
flask --app manage.py create-admin
```

### 6. Запуск
```bash
flask --app manage.py run
```

Приложение будет доступно на:  
👉 [http://127.0.0.1:5000](http://127.0.0.1:5000)

---

## 👥 Роли пользователей
- **Admin** → управление категориями и видео.  
- **Moderator** → загрузка/редактирование видео.  
- **User** → просмотр и лайки.  

---

## 📂 Структура проекта
```
flask_video_portal_with_thumbnails_final/
│── app/
│   ├── init.py      # создание Flask-приложения
│   ├── routes.py        # основные страницы и админка
│   ├── auth.py          # авторизация (login/logout)
│   ├── models.py        # модели SQLAlchemy
│   ├── forms.py         # формы (логин, загрузка видео)
│   ├── utils.py         # утилиты и декораторы
│   ├── templates/       # HTML-шаблоны (Jinja2)
│   └── static/          # стили, JS, изображения
│── manage.py            # команды управления (init-db, create-admin)
│── videos.db            # база данных SQLite
│── requirements.txt     # зависимости
```

---

## 🖼 Скриншоты (пример)
<img width="1165" height="932" alt="image" src="https://github.com/user-attachments/assets/5c423281-7136-4114-9655-15593152586d" />
<img width="910" height="789" alt="image" src="https://github.com/user-attachments/assets/bb0f30ef-d72d-4586-a13e-2115ea21ccbe" />
<img width="880" height="592" alt="image" src="https://github.com/user-attachments/assets/f06aeac6-13aa-4ca1-bb59-8e80b6d6b60e" />
<img width="850" height="715" alt="image" src="https://github.com/user-attachments/assets/a520dd68-8381-40de-aa1c-3ee461c91c9b" />
<img width="845" height="559" alt="image" src="https://github.com/user-attachments/assets/2308c4bb-9c83-47f0-b00c-75d01caba8da" />
<img width="867" height="770" alt="image" src="https://github.com/user-attachments/assets/58d205f6-598c-4d1b-b185-c579625d2788" />

---

## 🔮 Будущие улучшения
- 🌐 Поддержка **PostgreSQL/MySQL** вместо SQLite для продакшена.  
- 📡 REST API для интеграции с другими сервисами.  
- 🔍 Поиск и фильтрация видео по тегам и категориям.  
- 💬 Комментарии под видео.  
- 📊 Статистика просмотров (графики, аналитика).  
- 🏷 Поддержка **тегов** для видео.  
- 👤 Регистрация пользователей через e-mail.  
- 🛡 Двухфакторная авторизация (2FA).  
- ☁️ Хранение видео в **облаке (S3/MinIO)** вместо локальных файлов.   
- 🎨 Более современный UI (Bootstrap/Tailwind).  
