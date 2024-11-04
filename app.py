import base64
from datetime import datetime
from flask import Flask, render_template, url_for, request, redirect, flash
from flask_sqlalchemy import SQLAlchemy  # type: ignore
from flask_login import LoginManager, login_user, login_required, UserMixin
import os
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///poteryashki.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
login_manager = LoginManager(app)


# Модель пользователя
class Us_user(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    N_name = db.Column(db.String(50), nullable=False)
    Surname = db.Column(db.String(50), nullable=False)
    Email = db.Column(db.String(100), unique=True, nullable=False)
    Password = db.Column(db.String(100), nullable=False)
    Role = db.Column(db.String(50), nullable=False)

    # Связи с каскадным удалением
    volunteers = db.relationship('Volunteer', backref='user', lazy=True, cascade="all, delete-orphan")
    applications = db.relationship('Application', backref='application_user', lazy=True, cascade="all, delete-orphan")
    messages = db.relationship('Message', backref='message_user', lazy=True, cascade="all, delete-orphan")

# Модель волонтера
class Volunteer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    Experience = db.Column(db.String(20), nullable=False)
    ContactInformation = db.Column(db.String(100), nullable=False)
    Interactions = db.Column(db.Boolean, nullable=False, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey('us_user.id'), nullable=False)

    # Связь с моделью Us_user
    us_user = db.relationship('Us_user')  # Keep this without a backref

    # Связи с каскадным удалением
    messages = db.relationship('Message', backref='message_volunteer', lazy=True, cascade="all, delete-orphan")

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


    # Связи с каскадным удалением
    applications = db.relationship('Application', backref='midding', lazy=True, cascade="all, delete-orphan")

# Модель заявки
class Application(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('us_user.id'), nullable=False)
    midding_id = db.Column(db.Integer, db.ForeignKey('midding.id'), nullable=False)

# Модель сообщения
class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    Text = db.Column(db.Text, nullable=False)
    DataOfDispatch = db.Column(db.Date, nullable=False)
    TimeOfDispatch = db.Column(db.Time, nullable=False)
    FromWhom = db.Column(db.String(60), nullable=False)
    Whom = db.Column(db.String(60), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('us_user.id'), nullable=False)
    volunteer_id = db.Column(db.Integer, db.ForeignKey('volunteer.id'), nullable=False)


# Инициализация базы данных
with app.app_context():
    db.create_all()

@login_manager.user_loader
def load_user(user_id):
    return Us_user.query.get(int(user_id))

# Вход в систему
@app.route('/login', methods=['GET', 'POST'])
def login():
    email = request.form.get('Email')
    password = request.form.get('Password')

    if email and password:
        user = Us_user.query.filter_by(Email=email).first()

        if user and check_password_hash(user.Password, password):
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('index'))
        else:
            flash('Неверный логин или пароль', 'danger')
    else:
        flash('Введите логин и пароль', 'danger')

    return render_template('login.html')

@app.route("/register", methods=['POST', 'GET'])
def register():
    email = request.form.get('Email')
    password = request.form.get('Password')
    password2 = request.form.get('Password2')
    
    if request.method == 'POST':
        # Проверка на пустые поля
        if not (email and password and password2):
            flash('Введите логин и пароль', 'danger')
        # Проверка на совпадение паролей
        elif password != password2:
            flash('Пароли не совпадают', 'danger')
        # Проверка, существует ли email в базе данных
        elif Us_user.query.filter_by(Email=email).first():
            flash('Пользователь с таким email уже существует', 'danger')
        else:
            # Хеширование пароля
            hash_pwd = generate_password_hash(password, method='pbkdf2:sha256')
            role = request.form.get('Role')
            new_user = Us_user(
                N_name=request.form['N_name'],
                Surname=request.form['Surname'],
                Email=email,
                Password=hash_pwd,
                Role=role
            )
            # Добавление пользователя в базу данных
            db.session.add(new_user)
            db.session.commit()
            flash('Регистрация прошла успешно!', 'success')
            
            # Перенаправление на страницу в зависимости от роли
            if role == 'Волонтёр':
                return redirect(url_for('volunteer'))
            else:
                return redirect(url_for('login'))

    return render_template('register.html')

# Маршрут для добавления волонтера
from flask_login import current_user

from flask_login import login_required, current_user

@app.route("/volunteer", methods=['POST', 'GET'])
@login_required  # Убедитесь, что пользователь вошел в систему
def volunteer():
    if request.method == 'POST':
        # Получение данных из формы
        experience = request.form.get('Experience')
        contact_info = request.form.get('ContactInformation')
        
        # Проверка на заполнение обязательных полей
        if not experience or not contact_info:
            flash('Пожалуйста, заполните все поля', 'danger')
        else:
            # Создание записи о волонтере с Interactions = False
            new_volunteer = Volunteer(
                Experience=experience,
                ContactInformation=contact_info,
                Interactions=False,
                user_id=current_user.id  # Установите user_id текущего пользователя
            )
            try:
                db.session.add(new_volunteer)
                db.session.commit()
                flash('Данные волонтера успешно сохранены!', 'success')
                return redirect(url_for('index'))  # Перенаправление на страницу входа
            except Exception as e:
                db.session.rollback()  # Откат изменений в случае ошибки
                flash('Произошла ошибка при сохранении данных: ' + str(e), 'danger')

    return render_template('volunteer.html')

# Главная страница
@app.route("/index")
@app.route("/") 
def index():
    return render_template("index.html")

# Список заявок
@app.route("/spisock")
def spisock():
    db.session.expire_all()  # Обнуление кэша сессии
    posts = Midding.query.all()
    return render_template('spisock.html', posts=posts)



@app.route("/update_status/<int:post_id>", methods=['POST'])
@login_required
def update_status(post_id):
    new_status = request.form.get('status')
    print(f'Обновляем статус для поста {post_id}: {new_status}')  # Логирование нового статуса

    post = Midding.query.get(post_id)

    if post:
        post.Status = new_status  # Обновляем статус
        try:
            db.session.commit()  # Сохраняем изменения в БД
            flash('Статус успешно обновлён!', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Ошибка при обновлении статуса: {str(e)}', 'danger')
            print(f'Ошибка базы данных: {str(e)}')  # Логирование ошибки
    else:
        flash('Пропавший не найден.', 'danger')

    return redirect(url_for('spisock'))  # Возврат к списку пропавших

# Создание заявки
@app.route("/zayavka", methods=['POST', 'GET'])
@login_required
def zayavka():
    if request.method == 'POST':
        try:
            # Обработка фото
            photo_file = request.files.get('Photo')
            photo = base64.b64encode(photo_file.read()).decode('utf-8') if photo_file else None

            # Данные о пропавшем человеке
            name = request.form['Name']
            surname = request.form['Surname']
            patronymic = request.form['Patronymic']
            data_of_birth = request.form['DataOfBirth']
            gender = request.form['Gender']
            description = request.form['Description']
            data_of_last_appearance = request.form['DataOfLastAppearance']
            place_of_last_appearance = request.form['PlaceOfLastAppearance']

            # Создание записи о пропавшем
            post = Midding(
                Photo=photo, 
                Name=name, 
                Surname=surname, 
                Patronymic=patronymic,
                DataOfBirth=datetime.strptime(data_of_birth, '%Y-%m-%d'),
                Gender=gender, 
                Description=description,
                DataOfLastAppearance=datetime.strptime(data_of_last_appearance, '%Y-%m-%d'),
                PlaceOfLastAppearance=place_of_last_appearance,
                Status='Никто не ищет'
            )
            db.session.add(post)
            db.session.commit()

            # Проверяем, что Midding был успешно добавлен
            if post.id:
                flash(f'Пропавший добавлен с ID: {post.id}', 'info')
            else:
                flash('Ошибка добавления пропавшего', 'danger')
                return redirect('/zayavka')

            # Создаем запись в Application
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

@app.after_request
def redirect_to_signin(response):
    if response.status_code == 401:
        return redirect(url_for('login', next=request.url))
    
    return response

if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # Создание таблиц, если их еще нет
    app.run(debug=True)

#SNTP