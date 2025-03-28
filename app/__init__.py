# Import libraries
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path

db = SQLAlchemy()
DB_NAME = "database.db"

# Creating app
def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'secret_key'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    db.init_app(app)

    from .routes import routes

    app.register_blueprint(routes, url_prefix='/')

    from .models import Movies, Genre, Person, Trailer, Movie_Genre, Movie_Person # Importing models
    create_database(app)

    return app

# Creating database if it does not exist
def create_database(app):
    with app.app_context():
        if not path.exists('./instance/' + DB_NAME):
            db.create_all()
            print('Created database!')
