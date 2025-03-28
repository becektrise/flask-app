# Store DB models
from . import db # importing db defined in __init__

# Movies table
class Movies(db.Model):
    __tablename__ = 'movies'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    year = db.Column(db.Integer, nullable=True)
    rated = db.Column(db.String(50), nullable=True)
    runtime = db.Column(db.String(50), nullable=True)
    plot = db.Column(db.String(1000), nullable=True)
    imdb_rating = db.Column(db.Float, nullable=True)
    type = db.Column(db.String(50), nullable=True)
    genres = db.relationship('Genre', secondary='movie_genres', backref='movies')
    people = db.relationship('Person', secondary='movie_people', backref='movies')
    trailers = db.relationship('Trailer', backref='movie')

# Genre table
class Genre(db.Model):
    __tablename__ = 'genres'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))

# Person table
class Person(db.Model):
    __tablename__ = 'people'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200))

# Table with M:M relation for Movies and Genres
class Movie_Genre(db.Model):
    __tablename__ = 'movie_genres'
    id = db.Column(db.Integer, primary_key=True)
    movie_id = db.Column(db.Integer, db.ForeignKey('movies.id'))
    genre_id = db.Column(db.Integer, db.ForeignKey('genres.id'))

# Table with M:M relation for Movies and Person
class Movie_Person(db.Model):
    __tablename__ = 'movie_people'
    id = db.Column(db.Integer, primary_key=True)
    movie_id = db.Column(db.Integer, db.ForeignKey('movies.id'))
    person_id = db.Column(db.Integer, db.ForeignKey('people.id'))
    role = db.Column(db.String(50))

# Table tailers with 1:1 relation for Movie
class Trailer(db.Model):
    __tablename__ = 'trailers'
    id = db.Column(db.Integer, primary_key=True)
    movie_id = db.Column(db.Integer, db.ForeignKey('movies.id'))
    url = db.Column(db.String(500))
