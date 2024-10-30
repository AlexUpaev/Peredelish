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
db = SQLAlchemy(app)
login_manager = LoginManager(app)

# Модель пользователя
class Us_user(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    N_name = db.Column(db.String(20), nullable=False)
    Surname = db.Column(db.String(20), nullable=False)
    Email = db.Column(db.String(70), nullable=False, unique=True)
    Password = db.Column(db.String(128), nullable=False)
    Role = db.Column(db.String(20), nullable=False)

# Модель пропавшего
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

# Регистрация нового пользователя
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
            new_user = Us_user(
                N_name=request.form['N_name'],
                Surname=request.form['Surname'],
                Email=email,
                Password=hash_pwd,
                Role=request.form['Role']
            )
            # Добавление пользователя в базу данных
            db.session.add(new_user)
            db.session.commit()
            flash('Регистрация прошла успешно!', 'success')
            return redirect(url_for('login'))

    return render_template('register.html')


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

# Создание заявки
@app.route("/zayavka", methods=['POST', 'GET'])
@login_required
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
 
@app.after_request
def redirect_to_signin(response):
    if response.status_code == 401:
        return redirect(url_for('login', next=request.url))
    
    return response

if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # Создание таблиц, если их еще нет
    app.run(debug=True)
