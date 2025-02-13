# Листинг кода А.5 – Вспомогательные функции (utils.py)

# Задача файла: Определение вспомогательных функций для работы с данными и валидацией.

# Переменные:
# db: Экземпляр SQLAlchemy для работы с базой данных.

# Процедуры (методы):
# validate(password): Проверка пароля на соответствие требованиям безопасности.
# get_users_data(sort_column='Surname', sort_order='asc'): Получение списка пользователей с возможностью сортировки.
# get_volunteers_data(): Получение списка волонтёров вместе с их связанными пользователями.
# get_middings_data(): Получение списка пропавших людей.
# get_applications_data(): Получение списка заявок вместе с информацией о пользователях и пропавших.
# get_messages_data(): Получение списка сообщений вместе с информацией о волонтёрах и пользователях.
# get_poisk_data(): Получение списка поисковых операций вместе с информацией о волонтёрах и пропавших.
# get_user_counts(): Подсчёт количества пользователей по ролям.

import re
from sqlalchemy import func
from config import db

# Функция валидации пароля
def validate(password):
    Vozvrat = True
    if not (4 <= len(password) <= 16):
        Vozvrat = False
    if re.search(r'[*&{}|+]', password):
        Vozvrat = False
    if not re.search(r'[A-Z]', password):
        Vozvrat = False
    if not re.search(r'\d', password):
        Vozvrat = False
    return Vozvrat

# Функции для извлечения данных из базы данных
def get_users_data(sort_column='Surname', sort_order='asc'):
    from models import Us_user
    query = Us_user.query
    if sort_column.lower() == 'surname':
        sort_column = 'Surname'
    if sort_order == 'asc':
        query = query.order_by(getattr(Us_user, sort_column).asc())
    else:
        query = query.order_by(getattr(Us_user, sort_column).desc())
    return query.all()

def get_volunteers_data():
    from models import Volunteer, Us_user
    return db.session.query(Volunteer, Us_user).join(Us_user, Volunteer.user_id == Us_user.id).all()

def get_middings_data():
    from models import Midding
    return Midding.query.all()

def get_applications_data():
    from models import Application, Us_user, Midding
    return db.session.query(Application, Us_user, Midding). \
        join(Us_user, Application.user_id == Us_user.id). \
        join(Midding, Application.midding_id == Midding.id). \
        all()

def get_messages_data():
    from models import M_Message, Volunteer, Us_user
    return db.session.query(M_Message, Volunteer, Us_user). \
        join(Volunteer, M_Message.volunteer_id == Volunteer.id). \
        join(Us_user, M_Message.user_id == Us_user.id). \
        all()

def get_poisk_data():
    from models import Poisk, Midding, Volunteer
    return db.session.query(Poisk, Midding, Volunteer). \
        join(Volunteer, Poisk.volunteer_id == Volunteer.id). \
        join(Midding, Poisk.midding_id == Midding.id). \
        all()

def get_user_counts():
    from models import Us_user
    counts = {}
    result = db.session.query(Us_user.Role, func.count(Us_user.id)).group_by(Us_user.Role).all()
    for role, count in result:
        counts[role] = count
    return counts