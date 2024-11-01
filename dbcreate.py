from app import app, db
app.app_context().push()
db.drop_all()  # Удаляет все таблицы (включая volunteer)
db.create_all()  # Создаёт все таблицы заново