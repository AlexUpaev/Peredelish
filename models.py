# Листинг кода А.3 – Маршруты приложения (routes.py)

# Задача файла: Обработка запросов и определение маршрутов для веб-приложения Flask.

# Переменные:
# app: Экземпляр класса Flask, представляющий основное приложение.
# db: Экземпляр SQLAlchemy для работы с базой данных.
# login_required: Декоратор для защиты маршрутов от неавторизованных пользователей.
# current_user: Объект текущего пользователя, предоставленный flask_login.
# logout_user: Функция для выхода пользователя из системы.
# login_user: Функция для входа пользователя в систему.

# Процедуры (методы):
# login(): Обработка авторизации пользователя.
# register(): Регистрация нового пользователя.
# volunteer(): Добавление информации о волонтёре.
# index(): Отображение главной страницы.
# spisock(): Показ списка пропавших людей.
# logout(): Выход пользователя из системы.
# zayavka(): Создание заявки о пропавшем человеке.
# toggle_volunteer_link(post_id): Управление связью между волонтёром и пропавшим.
# update_status(post_id): Обновление статуса пропавшего человека.
# message(midding_id): Отправка сообщения о найденном пропавшем.
# database(): Отображение базы данных с возможностью фильтрации и сортировки.
# delete_data(table, id): Удаление записи из базы данных.
# edit_user(user_id): Редактирование данных пользователя.
# edit_volunteer(volunteer_id): Редактирование данных волонтёра.
# edit_midding(midding_id): Редактирование данных о пропавшем.
# edit_message(message_id): Редактирование сообщения.

from config import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

# Модель пользователя
class Us_user(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    N_name = db.Column(db.String(20), nullable=False)
    Surname = db.Column(db.String(20), nullable=False)
    Email = db.Column(db.String(100), unique=True, nullable=False)
    Password = db.Column(db.String(16), nullable=False)
    Role = db.Column(db.String(50), nullable=False)

    # Связи с каскадным удалением
    volunteers = db.relationship('Volunteer', backref='user', lazy=True, cascade="all, delete-orphan")
    applications = db.relationship('Application', backref='application_user', lazy=True, cascade="all, delete-orphan")
    messages = db.relationship('M_Message', backref='message_user', lazy=True, cascade="all, delete-orphan")

# Модель волонтера
class Volunteer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    Experience = db.Column(db.String(20), nullable=False)
    ContactInformation = db.Column(db.String(100), nullable=False)
    Interactions = db.Column(db.Boolean, nullable=False, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey('us_user.id'), nullable=False)
    us_user = db.relationship('Us_user')
    messages = db.relationship('M_Message', backref='message_volunteer', lazy=True, cascade="all, delete-orphan")
    poisk = db.relationship('Poisk', backref='poisk_volunteer', lazy=True, cascade="all, delete-orphan")

# Модель пропавшего
class Midding(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    Photo = db.Column(db.Text, nullable=False)
    Name = db.Column(db.String(20), nullable=False)
    Surname = db.Column(db.String(20), nullable=False)
    Patronymic = db.Column(db.String(20), nullable=True)
    DataOfBirth = db.Column(db.Date, nullable=False)
    Gender = db.Column(db.String(10), nullable=False)
    Description = db.Column(db.String(200), nullable=True)
    DataOfLastAppearance = db.Column(db.Date, nullable=False)
    PlaceOfLastAppearance = db.Column(db.String(50), nullable=False)
    Status = db.Column(db.String(20), nullable=False)
    applications = db.relationship('Application', backref='midding', lazy=True, cascade="all, delete-orphan")
    poisk = db.relationship('Poisk', backref='midding', lazy=True, cascade="all, delete-orphan")

# Модель заявки
class Application(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('us_user.id'), nullable=False)
    midding_id = db.Column(db.Integer, db.ForeignKey('midding.id'), nullable=False)

# Модель сообщения
class M_Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    Text_Message = db.Column(db.Text, nullable=False)
    DataOfDispatch = db.Column(db.Date, nullable=False)
    TimeOfDispatch = db.Column(db.Time, nullable=False)
    FromWhom = db.Column(db.String(100), nullable=False)
    Whom = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('us_user.id'), nullable=False)
    volunteer_id = db.Column(db.Integer, db.ForeignKey('volunteer.id'), nullable=False)

# Модель поиска
class Poisk(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    volunteer_id = db.Column(db.Integer, db.ForeignKey('volunteer.id'), nullable=False)
    midding_id = db.Column(db.Integer, db.ForeignKey('midding.id'), nullable=False)