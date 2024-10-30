#hzcbsdnziuzjn
import base64
from datetime import datetime
from flask import Flask, render_template, url_for, request, redirect, flash
from flask_sqlalchemy import SQLAlchemy  # type: ignore
from flask_login import LoginManager, login_user, login_required
import os
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///poteryashki.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Модель пользователя
class Us_user(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    N_name = db.Column(db.String(20), nullable=False)
    Surname = db.Column(db.String(20), nullable=False)
    Email = db.Column(db.String(50), unique=True, nullable=False)
    Password = db.Column(db.String(128), nullable=False)
    Role = db.Column(db.String(20), nullable=False)

# Модель заявки
class Midding(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    Photo = db.Column(db.Text, nullable=False)
    Name = db.Column(db.String(20), nullable=False)
    Surname = db.Column(db.String(20), nullable=False)
    Patronymic = db.Column(db.String(20), nullable=True)
    DataOfBirth = db.Column(db.Date, nullable=False)
    Gender = db.Column(db.String(10), nullable=False)
    Description = db.Column(db.Text, nullable=True)
    DataOfLastAppearance = db.Column(db.Date, nullable=False)
    PlaceOfLastAppearance = db.Column(db.String(50), nullable=False)

# Настройка Flask-Login
# Настройка Flask-Login
login_manager = LoginManager(app)

@login_manager.user_loader
def load_user(user_id):
    return Us_user.query.get(int(user_id))

# Вход в систему
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')  # Получаем email
        password = request.form.get('password')  # Получаем пароль

        # Логирование для отладки
        print(f"Email: {email}")  # Для отладки
        print(f"Password: {password}")  # Для отладки

        # Проверяем, что email и пароль не пустые
        if not email or not password:
            flash('Email и пароль обязательны.', 'danger')
            return render_template('login.html')

        # Поиск пользователя по email в базе данных
        user = Us_user.query.filter_by(Email=email).first()

        # Проверка наличия пользователя и правильности пароля
        if user and check_password_hash(user.Password, password):  # Проверяем пароль
            login_user(user)  # Вход в систему
            flash('Успешный вход!', 'success')  # Успешное сообщение
            return redirect(url_for('index'))  # Перенаправление на главную страницу
        
        flash('Неверный email или пароль.', 'danger')

    return render_template('login.html')


# Регистрация нового пользователя
@app.route("/register", methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        email = request.form['Email']
        password = request.form['Password']
        confirm_password = request.form['confirm_password']
        
        if password != confirm_password:
            flash('Пароли не совпадают. Пожалуйста, попробуйте снова.', 'danger')
            return render_template('register.html', 
                                   name=request.form['N_name'], 
                                   surname=request.form['Surname'],
                                   email=email, role=request.form['Role'])
        
        existing_user = Us_user.query.filter_by(Email=email).first()
        if existing_user:
            flash('Аккаунт с данным email уже зарегистрирован.', 'danger')
            return render_template('register.html', 
                                   name=request.form['N_name'], 
                                   surname=request.form['Surname'],
                                   email=email, role=request.form['Role'])

        try:
            name = request.form['N_name']
            surname = request.form['Surname']
            role = request.form['Role']
            hashed_password = generate_password_hash(password)

            new_user = Us_user(
                N_name=name,
                Surname=surname,
                Email=email,
                Password=hashed_password,
                Role=role
            )

            db.session.add(new_user)
            db.session.commit()
            flash('Регистрация прошла успешно!', 'success')
            return redirect('/')
        except Exception as e:
            db.session.rollback()
            flash(f'Ошибка при регистрации: {str(e)}', 'danger')
            return render_template('register.html', 
                                   name=request.form['N_name'], 
                                   surname=request.form['Surname'],
                                   email=email, role=request.form['Role'])
    else:
        return render_template('register.html')

# Создание заявки
@app.route("/zayavka", methods=['POST', 'GET'])
def zayavka():
    if request.method == 'POST':
        try:
            photo_file = request.files.get('Photo')
            photo = base64.b64encode(photo_file.read()).decode('utf-8') if photo_file else None

            name = request.form['Name']
            surname = request.form['Surname']
            patronymic = request.form['Patronymic']
            data_of_birth = request.form['DataOfBirth']
            gender = request.form['Gender']
            description = request.form['Description']
            data_of_last_appearance = request.form['DataOfLastAppearance']
            place_of_last_appearance = request.form['PlaceOfLastAppearance']

            post = Midding(
                Photo=photo, 
                Name=name, 
                Surname=surname, 
                Patronymic=patronymic,
                DataOfBirth=datetime.strptime(data_of_birth, '%Y-%m-%d'),
                Gender=gender, 
                Description=description,
                DataOfLastAppearance=datetime.strptime(data_of_last_appearance, '%Y-%m-%d'),
                PlaceOfLastAppearance=place_of_last_appearance
            )

            db.session.add(post)
            db.session.commit()
            flash('Заявка успешно добавлена!', 'success')
            return redirect('/')
        
        except Exception as e:
            db.session.rollback()
            flash(f'При добавлении заявки произошла ошибка: {str(e)}', 'danger')
            return redirect('/zayavka')
    else:
        return render_template('zayavka.html')

# Главная страница
@app.route("/index")
@app.route("/") 
def index():
    return render_template("index.html")

# Список заявок
@app.route("/spisock")
def spisock():
    posts = Midding.query.all()
    return render_template('spisock.html', posts=posts)

if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # Создание таблиц, если их еще нет
    app.run(debug=True)
