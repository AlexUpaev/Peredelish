# Листинг кода А.4 – Маршруты приложения (routes.py)

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

from flask import redirect, url_for, flash, render_template, request
from flask_login import login_required, current_user, logout_user, login_user
from config import app, db
from models import Us_user, Volunteer, Midding, Application, M_Message, Poisk
from utils import validate, get_users_data, get_volunteers_data, get_middings_data, get_applications_data, get_messages_data, get_poisk_data, get_user_counts
import base64
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash


# Маршрут для авторизации
@app.route('/login', methods=['GET', 'POST'])
def login():
    email = request.form.get('Email')
    password = request.form.get('Password')
    if email and password:
        user = Us_user.query.filter_by(Email=email).first()  # Поиск пользователя по email
        if user and check_password_hash(user.Password, password):  # Проверка пароля
            login_user(user)  # Вход пользователя
            next_page = request.args.get('next')  # Получение следующей страницы
            return redirect(next_page) if next_page else redirect(url_for('index'))  # Перенаправление на страницу после авторизации в противном случае на главную страницу
        else:
            flash('Неверный логин или пароль', 'danger')
    return render_template('login.html')

# Маршрут для регистрации
@app.route("/register", methods=['POST', 'GET'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))  # Перенаправление на главную страницу
    email = request.form.get('Email')
    password = request.form.get('Password')
    password2 = request.form.get('Password2')
    name = request.form.get('Name')
    surname = request.form.get('Surname')
    role = request.form.get('Role')
    if request.method == 'POST':
        if not (email and password and password2 and name and surname and role):
            flash('Заполните все поля', 'danger')
        elif password != password2:
            flash('Пароли не совпадают', 'danger')
        elif Us_user.query.filter_by(Email=email).first():
            flash('Пользователь с таким аккаунтом уже существует', 'danger')
        elif not validate(password):
            flash('Пароль должен содержать от 4 до 16 символов, включать заглавные буквы и цифры, и не содержать символов: * & { } | +', 'danger')
        else:
            hash_pwd = generate_password_hash(password, method='pbkdf2:sha256')
            new_user = Us_user(
                N_name=name,
                Surname=surname,
                Email=email,
                Password=hash_pwd,
                Role=role
            )
            db.session.add(new_user)
            db.session.commit()
            flash('Регистрация прошла успешно!', 'success')
            if role == 'Волонтёр':
                return redirect(url_for('volunteer'))
            else:
                return redirect(url_for('login'))
    return render_template('register.html')

# Маршрут для добавления волонтера
@app.route("/volunteer", methods=['POST', 'GET'])
@login_required
def volunteer():
    if request.method == 'POST':
        experience = request.form.get('Experience')
        contact_info = request.form.get('ContactInformation')
        if not experience or not contact_info:
            flash('Пожалуйста, заполните все поля', 'danger')
        else:
            new_volunteer = Volunteer(
                Experience=experience,
                ContactInformation=contact_info,
                Interactions=False,
                user_id=current_user.id
            )
            db.session.add(new_volunteer)
            db.session.commit()
            flash('Волонтер успешно добавлен!', 'success')
            return redirect(url_for('index'))
    return render_template('volunteer.html')

# Главная страница
@app.route("/index")
@app.route("/")
def index():
    return render_template("index.html")

# Страница со списком пропавших
@app.route("/spisock")
@login_required
def spisock():
    db.session.expire_all()
    posts = Midding.query.all()
    midding_count = len(posts)
    for post in posts:
        post.is_linked = Poisk.query.filter_by(midding_id=post.id).first() is not None
    return render_template('spisock.html', posts=posts, midding_count=midding_count)

# Выход из аккаунта
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Вы вышли из аккаунта', 'success')
    return redirect(url_for('index'))

# Создание заявки о пропавшем
@app.route("/zayavka", methods=['POST', 'GET'])
@login_required
def zayavka():
    if request.method == 'POST':
        try:
            name = request.form['Name']
            surname = request.form['Surname']
            patronymic = request.form['Patronymic']
            data_of_birth = request.form['DataOfBirth']
            gender = request.form['Gender']
            description = request.form['Description']
            data_of_last_appearance = request.form['DataOfLastAppearance']
            place_of_last_appearance = request.form['PlaceOfLastAppearance']

            if not all([name, surname, data_of_birth, gender, description, data_of_last_appearance, place_of_last_appearance]):
                flash('Пожалуйста, заполните все поля', 'danger')
                return redirect(url_for('zayavka'))

            try:
                data_of_birth_dt = datetime.strptime(data_of_birth, '%Y-%m-%d')
                data_of_last_appearance_dt = datetime.strptime(data_of_last_appearance, '%Y-%m-%d')
            except ValueError:
                flash('Неверный формат даты. Используйте формат YYYY-MM-DD.', 'danger')
                return redirect(url_for('zayavka'))

            photo_file = request.files.get('Photo')
            photo = base64.b64encode(photo_file.read()).decode('utf-8') if photo_file else None

            post = Midding(
                Photo=photo,
                Name=name,
                Surname=surname,
                Patronymic=patronymic,
                DataOfBirth=data_of_birth_dt,
                Gender=gender,
                Description=description,
                DataOfLastAppearance=data_of_last_appearance_dt,
                PlaceOfLastAppearance=place_of_last_appearance,
                Status='Никто не ищет'
            )
            db.session.add(post)
            db.session.commit()

            if post.id:
                flash(f'Пропавший добавлен с ID: {post.id}', 'info')
            else:
                flash('Ошибка добавления пропавшего', 'danger')

            application = Application(
                user_id=current_user.id,
                midding_id=post.id
            )
            db.session.add(application)
            db.session.commit()
            flash("Заявка и запись поиска успешно добавлены!", "success")
            return redirect('/')
        except Exception as e:
            db.session.rollback()
            flash(f'При добавлении заявки произошла ошибка: {str(e)}', 'danger')
            return redirect('/zayavka')
    else:
        return render_template('zayavka.html')

# Обработка переключения связи между волонтером и пропавшим
@app.route('/toggle_volunteer_link/<int:post_id>', methods=['POST'])
@login_required
def toggle_volunteer_link(post_id):
    volunteer_id = current_user.volunteers[0].id
    linked = request.form.get('linked') == 'on'

    link = Poisk.query.filter_by(volunteer_id=volunteer_id, midding_id=post_id).first()
    if linked:
        if not link:
            new_link = Poisk(volunteer_id=volunteer_id, midding_id=post_id)
            db.session.add(new_link)
            db.session.commit()
            flash('Вступление в поисковую группу успешно завершено!', 'success')
    else:
        if link:
            db.session.delete(link)
            db.session.commit()
            flash('Выход из поисковой группы успешно завершен!', 'success')
    return redirect(url_for('spisock'))

# Обновление статуса пропавшего
@app.route("/update_status/<int:post_id>", methods=['POST'])
@login_required
def update_status(post_id):
    new_status = request.form.get('status')
    post = Midding.query.get(post_id)
    if post:
        post.Status = new_status
        try:
            db.session.commit()
            flash('Статус успешно обновлён!', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Ошибка при обновлении статуса: {str(e)}', 'danger')
    else:
        flash('Пропавший не найден.', 'danger')

    if new_status == 'Обнаружен':
        return redirect(url_for('message', midding_id=post_id))
    else:
        return redirect(url_for('spisock'))

# Страница для отправки сообщения
@app.route("/message/<int:midding_id>", methods=['GET', 'POST'])
@login_required
def message(midding_id):
    if request.method == 'POST':
        try:
            text = request.form.get('text')
            data_of_dispatch = datetime.now().date()
            time_of_dispatch = datetime.now().time()

            if not text:
                flash('Пожалуйста, введите текст сообщения', 'danger')
                return render_template('message.html', midding_id=midding_id)

            application = Application.query.filter_by(midding_id=midding_id).first()
            if not application:
                flash('Заявка на пропавшего не найдена', 'danger')
                return redirect(url_for('spisock'))

            applicant_user = Us_user.query.get(application.user_id)
            if not applicant_user:
                flash('Пользователь, оставивший заявку, не найден', 'danger')
                return redirect(url_for('spisock'))

            volunteer = Volunteer.query.filter_by(user_id=current_user.id).first()
            if not volunteer:
                flash('Текущий пользователь не является волонтёром', 'danger')
                return redirect(url_for('spisock'))

            message_record = M_Message(
                Text_Message=text,
                DataOfDispatch=data_of_dispatch,
                TimeOfDispatch=time_of_dispatch,
                FromWhom=current_user.Email,
                Whom=applicant_user.Email,
                user_id=applicant_user.id,
                volunteer_id=volunteer.id
            )
            db.session.add(message_record)
            db.session.commit()
            flash('Сообщение отправлено!', 'success')
            return redirect(url_for('index'))
        except Exception as e:
            db.session.rollback()
            flash('Произошла ошибка при отправке сообщения: ' + str(e), 'danger')
    return render_template('message.html', midding_id=midding_id)

# Маршрут для отображения базы данных
@app.route("/database", methods=["GET"])
@login_required
def database():
    table_name = request.args.get('table', 'users')
    search_query = request.args.get('search', '')
    sort_column = request.args.get('sort_column', 'Surname')
    sort_order = request.args.get('sort_order', 'asc')

    allowed_tables = ['users', 'volunteers', 'middings', 'applications', 'messages', 'poisk', 'user_count']
    if table_name not in allowed_tables:
        table_name = 'users'

    data = {
        'users': get_users_data(sort_column, sort_order),
        'volunteers': get_volunteers_data(),
        'middings': get_middings_data(),
        'applications': get_applications_data(),
        'messages': get_messages_data(),
        'poisk': get_poisk_data(),
    }
    user_counts = get_user_counts()
    return render_template('database.html', table_name=table_name, data=data, user_counts=user_counts, search_query=search_query)

# Маршрут для удаления данных
@app.route("/delete_data/<string:table>/<int:id>", methods=["POST"])
@login_required
def delete_data(table, id):
    model_mapping = {
        'users': Us_user,
        'middings': Midding
    }
    model = model_mapping.get(table)
    if model:
        record = model.query.get(id)
        if record:
            if table == 'users':
                # Удаление связанных заявок для пользователей
                applications = Application.query.filter_by(user_id=id).all()
                for application in applications:
                    if application.midding:
                        db.session.delete(application.midding)  # Удаляем связанного пропавшего
                    db.session.delete(application)  # Удаляем саму заявку

            elif table == 'middings':
                # Удаление связанных заявок для пропавших
                applications = Application.query.filter_by(midding_id=id).all()
                for application in applications:
                    db.session.delete(application)  # Удаляем заявку

            # Удаление основной записи
            db.session.delete(record)

            db.session.commit()
            flash(f'Данные из таблицы {table.capitalize()} успешно удалены!', 'success')
        else:
            flash(f'Данные из таблицы {table.capitalize()} не найдены!', 'error')
    else:
        flash('Недопустимая таблица!', 'error')

    return redirect(url_for('database'))

# Редактирование пользователя
@app.route("/edit_user/<int:user_id>", methods=['GET', 'POST'])
@login_required
def edit_user(user_id):
    user = Us_user.query.get_or_404(user_id)
    if request.method == 'POST':
        user.N_name = request.form.get('N_name')
        user.Surname = request.form.get('Surname')
        user.Email = request.form.get('Email')
        password = request.form.get('Password')
        if password:
            user.Password = generate_password_hash(password, method='pbkdf2:sha256')
        user.Role = request.form.get('Role')
        try:
            db.session.commit()
            flash('Данные пользователя успешно обновлены!', 'success')
            return redirect(url_for('database'))
        except Exception as e:
            db.session.rollback()
            flash(f'Ошибка при обновлении данных: {str(e)}', 'danger')
    return render_template('edit_user.html', user=user)

# Редактирование волонтера
@app.route("/edit_volunteer/<int:volunteer_id>", methods=['GET', 'POST'])
@login_required
def edit_volunteer(volunteer_id):
    volunteer = Volunteer.query.get_or_404(volunteer_id)
    if request.method == 'POST':
        volunteer.Experience = request.form.get('Experience')
        volunteer.ContactInformation = request.form.get('ContactInformation')
        volunteer.Interactions = request.form.get('Interactions') == 'True'
        try:
            db.session.commit()
            flash('Данные волонтера успешно обновлены!', 'success')
            return redirect(url_for('database'))
        except Exception as e:
            db.session.rollback()
            flash(f'Ошибка при обновлении данных: {str(e)}', 'danger')
    return render_template('edit_volunteer.html', volunteer=volunteer)

# Редактирование пропавшего
@app.route("/edit_midding/<int:midding_id>", methods=['GET', 'POST'])
@login_required
def edit_midding(midding_id):
    midding = Midding.query.get_or_404(midding_id)
    if request.method == 'POST':
        try:
            midding.Name = request.form.get('Name')
            midding.Surname = request.form.get('Surname')
            midding.Patronymic = request.form.get('Patronymic')
            midding.DataOfBirth = datetime.strptime(request.form.get('DataOfBirth'), '%Y-%m-%d')
            midding.Gender = request.form.get('Gender')
            midding.Description = request.form.get('Description')
            midding.DataOfLastAppearance = datetime.strptime(request.form.get('DataOfLastAppearance'), '%Y-%m-%d')
            midding.PlaceOfLastAppearance = request.form.get('PlaceOfLastAppearance')
            midding.Status = request.form.get('Status')
            db.session.commit()
            flash('Данные о пропавшем успешно обновлены!', 'success')
            return redirect(url_for('database', table='middings'))
        except Exception as e:
            db.session.rollback()
            flash(f'Ошибка при обновлении данных: {str(e)}', 'danger')
    return render_template('edit_midding.html', midding=midding)

# Редактирование сообщения
@app.route("/edit_message/<int:message_id>", methods=['GET', 'POST'])
@login_required
def edit_message(message_id):
    message = M_Message.query.get_or_404(message_id)
    if request.method == 'POST':
        try:
            message.Text_Message = request.form.get('text_message')
            message.DataOfDispatch = datetime.strptime(request.form.get('date_of_dispatch'), '%Y-%m-%d')
            message.TimeOfDispatch = datetime.strptime(request.form.get('time_of_dispatch'), '%H:%M').time()
            message.FromWhom = request.form.get('author')
            message.Whom = request.form.get('recipient')
            db.session.commit()
            flash('Сообщение успешно обновлено!', 'success')
            return redirect(url_for('database', table_name='messages'))
        except Exception as e:
            db.session.rollback()
            flash(f'Ошибка при обновлении сообщения: {str(e)}', 'danger')
    return render_template('edit_message.html', message=message)

# Перенаправление на страницу авторизации
@app.after_request
def redirect_to_signin(response):
    if response.status_code == 401:
        return redirect(url_for('login', next=request.url))
    return response