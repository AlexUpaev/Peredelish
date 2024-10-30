from flask_login import UserMixin
from app import db  # Замените на ваш импорт базы данных

class Us_user(db.Model, UserMixin):  # Наследование от UserMixin
    __tablename__ = 'users'  # Имя вашей таблицы

    id = db.Column(db.Integer, primary_key=True)
    Email = db.Column(db.String(150), unique=True, nullable=False)
    Password = db.Column(db.String(200), nullable=False)
    # Добавьте другие поля, если необходимо

    @property
    def is_active(self):
        return True  # Или добавьте логику для проверки активности пользователя

    @property
    def is_authenticated(self):
        return True  # Пользователь считается аутентифицированным

    @property
    def is_anonymous(self):
        return False  # Обычно возвращает False для реальных пользователей
