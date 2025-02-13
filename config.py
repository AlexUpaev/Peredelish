# Листинг кода А.2 – Конфигурация приложения (config.py)

# Задача файла: Настройка основных параметров работы веб-приложения Flask.

# Переменные:
# app: Экземпляр класса Flask, представляющий основное приложение.
# db: Экземпляр SQLAlchemy для работы с базой данных.
# login_manager: Менеджер аутентификации пользователей через flask_login.
# Процедуры (методы):
# load_user(user_id): Загрузка пользователя по его идентификатору для аутентификации.

# Структура файла:
# Импорт необходимых компонентов:
# Flask: Основной фреймворк для создания веб-приложения.
# SQLAlchemy: ORM для работы с базой данных.
# LoginManager: Инструмент для управления аутентификацией пользователей.
# os: Для генерации секретного ключа.

# Инициализация основных компонентов приложения:
# Создание экземпляра Flask.
# Генерация случайного секретного ключа для защиты сессий.
# Настройка подключения к базе данных SQLite (sqlite:///poteryashki.db).
# Отключение отслеживания изменений SQLAlchemy для оптимизации производительности.
# Включение логирования SQL-запросов для отладки.

# Инициализация расширений:
# SQLAlchemy для работы с базой данных.
# LoginManager для управления аутентификацией пользователей.
# Реализация метода load_user:
# Метод используется для загрузки пользователя по его идентификатору из базы данных.

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Генерация случайного ключа для сессий
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///poteryashki.db'  # Настройка базы данных
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True  # Включение логирования SQL-запросов

db = SQLAlchemy(app)  # Инициализация SQLAlchemy
login_manager = LoginManager(app)  # Инициализация менеджера входа

@login_manager.user_loader
def load_user(user_id):
    from models import Us_user
    return Us_user.query.get(int(user_id))