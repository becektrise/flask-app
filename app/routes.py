# Store routes
from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for, make_response
from .models import Movies, Genre, Person, Trailer, Movie_Genre, Movie_Person
from . import db
from io import BytesIO
import io
import json
import csv
import pandas as pd
import matplotlib.pyplot as plt
import base64

routes = Blueprint('routes', __name__)

@routes.route('/')
def home():
    return render_template('home.html')

@routes.route('/database')
def database():
    movies = Movies.query.all()

    # Set directors, writers and actors names as a param for Person that is stored in Movie_Person table.
    # This is used to easier get access to people
    for movie in movies:
        movie.directors = {}
        movie.writers = {}
        movie.actors = {}

        moviePersons = Movie_Person.query.filter_by(movie_id=movie.id).all()
        for moviePerson in moviePersons:
            person = Person.query.filter_by(id=moviePerson.person_id).first()

            if moviePerson.role == 'Director':
                movie.directors[person.name] = person.name
            elif moviePerson.role == 'Writer':
                movie.writers[person.name] = person.name
            elif moviePerson.role == 'Actor':
                movie.actors[person.name] = person.name

    return render_template('database.html', movies=movies)

@routes.route('/add_entry', methods=['GET', 'POST'])
def addEntry():
    if request.method == 'POST':
        title = request.form.get('title')
        year = request.form.get('year')
        rated = request.form.get('rated')
        runtime = request.form.get('runtime')
        genre = request.form.get('genre')
        director = request.form.get('director')
        writer = request.form.get('writer')
        actors = request.form.get('actors')
        plot = request.form.get('plot')
        imdbRating = request.form.get('imdbRating')
        type = request.form.get('type')
        trailer = request.form.get('trailer')

        isValid = True

        if len(genre) > 0:
            for x in genre.split(','):
                if len(x.strip()) < 1:
                    flash('Žanrs ir pārāk īss', category='error')
                    isValid = False
                elif len(x.strip()) > 50:
                    flash('Žanrs ir pārāk garš', category='error')
                    isValid = False

        if len(writer) > 0:
            for x in writer.split(','):
                if len(x.strip()) < 1:
                    flash('Rakstnieka vārds ir pārāk īss', category='error')
                    isValid = False
                elif len(x.strip()) > 200:
                    flash('Rakstnieka vārds ir pārāk garš', category='error')
                    isValid = False

        if len(actors) > 0:
            for x in actors.split(','):
                if len(x.strip()) < 1:
                    flash('Akiera vārds ir pārāk īss', category='error')
                    isValid = False
                elif len(x.strip()) > 50:
                    flash('Akiera vārds ir pārāk garš', category='error')
                    isValid = False

        if len(director) > 0:
            for x in director.split(','):
                if len(x.strip()) < 1:
                    flash('Režisora vārds ir pārāk īss', category='error')
                    isValid = False
                elif len(x.strip()) > 200:
                    flash('Režisora vārds ir pārāk garš', category='error')
                    isValid = False

        movieExists = Movies.query.filter_by(title=title).first()
        if movieExists:
            flash('Filma ar šādu nosaukumu jau eksistē', category='error')
        elif len(title) < 1:
            flash('Nosaukums ir pārāk īss', category='error')
        elif len(title) > 200:
            flash('Nosaukums ir pārāk garš', category='error')
        elif year == '' or int(year) < 0:
            flash('Nepareizs gads', category='error')
        elif len(rated) < 1:
            flash('Klase ir pārāk īsa', category='error')
        elif len(rated) > 50:
            flash('Klase ir pārāk gara', category='error')
        elif len(runtime) < 1:
            flash('Ilgums ir pārāk īss', category='error')
        elif len(runtime) > 50:
            flash('Ilgums ir pārāk garš', category='error')
        elif len(genre) < 1:
            flash('Nav norādīts žanrs', category='error')
        elif len(director) < 1:
            flash('Nav norādīts režisors', category='error')
        elif len(writer) < 1:
            flash('Nav norādīts rakstnieks', category='error')
        elif len(plot) < 1:
            flash('Apraksts ir pārāk īss', category='error')
        elif len(plot) > 1000:
            flash('Apraksts ir pārāk garš', category='error')
        elif year == '' or float(imdbRating) < 0 or float(imdbRating) > 10:
            flash('IMDB vērtējums ir nepareizs', category='error')
        elif len(type) < 1:
            flash('Tips ir pārāk īss', category='error')
        elif len(type) > 50:
            flash('Tips ir pārāk garš', category='error')
        elif len(trailer) > 500:
            flash('Trailera saite ir pārāk gara', category='error')

        if isValid:
            # Create a new movie entry
            newMovie = Movies(
                title=title.strip(),
                year=int(year),
                rated=rated.strip(),
                runtime=runtime.strip(),
                plot=plot.strip(),
                imdb_rating=float(imdbRating),
                type=type.strip(),
            )
            db.session.add(newMovie)
            db.session.flush() # Get movie ID

            # Create a new genre entry/-ies
            genres = genre.split(',')
            for genre_name in genres:
                genre = Genre.query.filter_by(name=genre_name.strip()).first()
                if not genre:
                    genre = Genre(name=genre_name.strip())
                    db.session.add(genre)
                    db.session.flush()
                movie_genre = Movie_Genre(movie_id=newMovie.id, genre_id=genre.id)
                db.session.add(movie_genre)

            # Create a new people entry/-ies
            actors = actors.split(',')
            for actorName in actors:
                person = Person.query.filter_by(name=actorName.strip()).first()
                if not person:
                    person = Person(name=actorName.strip())
                    db.session.add(person)
                    db.session.flush()
                moviePerson = Movie_Person(movie_id=newMovie.id, person_id=person.id, role='Actor')
                db.session.add(moviePerson)

            directors = director.split(',')
            for directorName in directors:
                person = Person.query.filter_by(name=directorName.strip()).first()
                if not person:
                    person = Person(name=directorName.strip())
                    db.session.add(person)
                    db.session.flush()
                moviePerson = Movie_Person(movie_id=newMovie.id, person_id=person.id, role='Director')
                db.session.add(moviePerson)

            writers = writer.split(',')
            for writerName in writers:
                person = Person.query.filter_by(name=writerName.strip()).first()
                if not person:
                    person = Person(name=writerName.strip())
                    db.session.add(person)
                    db.session.flush()
                moviePerson = Movie_Person(movie_id=newMovie.id, person_id=person.id, role='Writer')
                db.session.add(moviePerson)

            # Create trailer
            newTrailer = Trailer(movie_id=newMovie.id, url=trailer)
            db.session.add(newTrailer)
            db.session.commit()

            flash('Ieraksts pievienots', category='success')
            return redirect(url_for('routes.database'))


    return render_template('add_entry.html')

@routes.route('/delete_movie', methods=['POST'])
def deleteMovie():
    movie = json.loads(request.data)
    movieId = movie['movieId']
    movie = Movies.query.get(movieId)
    if movie:
        # Delete references from Movie_Person table
        movie_people = Movie_Person.query.filter_by(movie_id=movieId).all()
        for movie_person in movie_people:
            db.session.delete(movie_person)

        # Delete references from Movie_Genre table
        movie_genres = Movie_Genre.query.filter_by(movie_id=movieId).all()
        for movie_genre in movie_genres:
            db.session.delete(movie_genre)

        # Delete trailer
        trailer = Trailer.query.filter_by(movie_id=movieId).first()
        if trailer:
            db.session.delete(trailer)

        # Delete movie
        db.session.delete(movie)
        db.session.commit()

    return jsonify({})

@routes.route('/import_data', methods=['POST'])
def importData():
    movieData = Movies.query.first()
    if movieData:
        flash('Datubāze nav tukša', category='error')
    else:
        for i in range(1, 101):
            filename = f'{i}.json'
            with open('./data/' + filename, 'r') as file:
                data = json.load(file)

            # Create a new movie entry
            movie = Movies(
                title=data['Title'],
                year=int(data['Year']),
                rated=data['Rated'],
                runtime=data['Runtime'],
                plot=data['Plot'],
                imdb_rating=float(data['imdbRating']),
                type=data['Type']
            )
            db.session.add(movie)
            db.session.flush() # Get the movie ID

            # Create genres
            genres = data['Genre'].split(',')
            for genre_name in genres:
                genre = Genre.query.filter_by(name=genre_name.strip()).first()
                if not genre:
                    genre = Genre(name=genre_name.strip())
                    db.session.add(genre)
                    db.session.flush()
                movie_genre = Movie_Genre(movie_id=movie.id, genre_id=genre.id)
                db.session.add(movie_genre)

            # Create people
            people = data['Actors'].split(',')
            for person_name in people:
                person = Person.query.filter_by(name=person_name.strip()).first()
                if not person:
                    person = Person(name=person_name.strip())
                    db.session.add(person)
                    db.session.flush()
                movie_person = Movie_Person(movie_id=movie.id, person_id=person.id, role='Actor')
                db.session.add(movie_person)

            people = data['Director'].split(',')
            for person_name in people:
                person = Person.query.filter_by(name=person_name.strip()).first()
                if not person:
                    person = Person(name=person_name.strip())
                    db.session.add(person)
                    db.session.flush()
                movie_person = Movie_Person(movie_id=movie.id, person_id=person.id, role='Director')
                db.session.add(movie_person)

            people = data['Writer'].split(',')
            for person_name in people:
                person = Person.query.filter_by(name=person_name.strip()).first()
                if not person:
                    person = Person(name=person_name.strip())
                    db.session.add(person)
                    db.session.flush()
                movie_person = Movie_Person(movie_id=movie.id, person_id=person.id, role='Writer')
                db.session.add(movie_person)

            # Create trailer
            trailer = Trailer(movie_id=movie.id, url=data['0']['trailer'])
            db.session.add(trailer)

        db.session.commit()
        flash('Datubāze aizpildīta ar datiem', category='success')

    return redirect(url_for('routes.database'))

@routes.route('/clear_data', methods=['POST'])
def claerData():
    # Delete all movie_person relationships
    Movie_Person.query.delete()

    # Delete all movie_genre relationships
    Movie_Genre.query.delete()

    # Delete all trailers
    Trailer.query.delete()

    # Delete all movies
    Movies.query.delete()

    # Delete all people
    Person.query.delete()

    # Delete all genres
    Genre.query.delete()

    db.session.commit()

    flash('Datubāze iztīrīta', category='success')

    return redirect(url_for('routes.database'))

@routes.route('/download_csv', methods=['POST'])
def downloadCsv():
    # Preparing movie data
    movies = Movies.query.all()

    # Check if there are movies in database
    if not movies:
        flash('Nav atrasta neviena filma', category='error')
        return redirect(url_for('routes.database'))

    # Set directors, writers and actors names as a param for Person that is stored in Movie_Person table.
    # This is used to easier get access to people
    for movie in movies:
        movie.directors = []
        movie.writers = []
        movie.actors = []

        moviePersons = Movie_Person.query.filter_by(movie_id=movie.id).all()
        for moviePerson in moviePersons:
            person = Person.query.filter_by(id=moviePerson.person_id).first()

            if moviePerson.role == 'Director':
                movie.directors.append(person.name)
            elif moviePerson.role == 'Writer':
                movie.writers.append(person.name)
            elif moviePerson.role == 'Actor':
                movie.actors.append(person.name)

    output = io.StringIO()
    writer = csv.writer(output)

    # Writing columns
    writer.writerow([
        'MovieId',
        'Title',
        'Year',
        'Rated',
        'Runtime',
        'Genres',
        'Directors',
        'Writers',
        'Actors',
        'Plot',
        'imdbRating',
        'Type',
        'TrailerLink'
    ])

    # Writing the rows
    for movie in movies:
        genres = ', '.join([genre.name for genre in movie.genres])
        directors = ', '.join(movie.directors)
        writers = ', '.join(movie.writers)
        actors = ', '.join(movie.actors)

        trailerLink = ''
        if movie.trailers[0].url:
            trailerLink = stripAfterChar(movie.trailers[0].url, ';')

        writer.writerow([
            movie.id,
            movie.title,
            movie.year,
            movie.rated,
            movie.runtime,
            genres,
            directors,
            writers,
            actors,
            movie.plot,
            movie.imdb_rating,
            movie.type,
            trailerLink
        ])

    # Marking response and setting headers
    output = make_response(output.getvalue())
    output.headers["Content-Disposition"] = "attachment; filename=movies.csv"
    output.headers["Content-type"] = "text/csv"

    return output

def stripAfterChar(s, char):
    index = s.find(char)
    if index != -1:
        return s[:index]
    return s

@routes.route('/imdb_ratings')
def getImdbRatingsHistogram():
    # Getting data from database and preparing
    movies = Movies.query.all()
    data = {
        'imdbRating': [movie.imdb_rating for movie in movies],
        'Year': [movie.year for movie in movies]
    }

    # Preparing histogram
    df = pd.DataFrame(data)
    plt.figure(figsize=(10, 6))
    plt.hist(df['imdbRating'], bins=10, alpha=0.5, label='IMDB Vērtējumi', color='green', edgecolor='black')
    plt.xlabel('IMDB Vērtējums')
    plt.ylabel('Biežums')
    plt.title('IMDB vērtējumu sadalījums')
    plt.legend()

    # Preparing image
    img = BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    img_b64 = base64.b64encode(img.getvalue()).decode() # Encode to base64

    plt.close()  # Close to free up memory

    return render_template('imdb_ratings.html', image=img_b64)

@routes.route('/top_people')
def getTopPeople():
    # Getting data from database and preparing
    people = Person.query.all()
    data = {
        'Name': [person.name for person in people],
        'Movie Count': [len(person.movies) for person in people]
    }

    # Preparing barh chart
    df = pd.DataFrame(data)
    top_20_people = df.nlargest(20, 'Movie Count')
    plt.figure(figsize=(10, 8))
    plt.barh(top_20_people['Name'], top_20_people['Movie Count'])
    plt.xlabel('Filmu skaits')
    plt.ylabel('Vārds')
    plt.title('Top 20 cilvēki')
    plt.tight_layout()

    # Preparing image
    img = BytesIO()
    plt.savefig(img)
    img.seek(0)
    img_b64 = base64.b64encode(img.getvalue()).decode() # Encode to base64

    return render_template('top_people.html', image=img_b64)

@routes.route('/top_rated_old_movies')
def getTopRatedOldMovies():
    # Getting data from database and preparing
    movies = Movies.query.all()
    old_movies = [movie for movie in movies if movie.year < 2000]
    data = {
        'Title': [f"{movie.title} ({movie.year})" for movie in old_movies],
        'IMDB Rating': [movie.imdb_rating for movie in old_movies]
    }

    # Preparing bar chart
    df = pd.DataFrame(data)
    top_10_movies = df.nlargest(10, 'IMDB Rating')
    plt.figure(figsize=(10, 8))
    plt.bar(top_10_movies['Title'], top_10_movies['IMDB Rating'], color='purple')
    plt.xlabel('Filmas nosaukums')
    plt.ylabel('IMDB Vērtējums')
    plt.title('Top 10 vecākās novērtētākās filmas')
    plt.xticks(rotation=60)
    plt.ylim(8, 10)  # Set y-axis limits to 8 - 10
    plt.tight_layout()

    # Preparing image
    img = BytesIO()
    plt.savefig(img)
    img.seek(0)
    img_b64 = base64.b64encode(img.getvalue()).decode() # Encode to base64

    return render_template('top_rated_old_movies.html', image=img_b64)

@routes.route('/genre_frequency')
def getGenreFrequency():
    # Getting data from database and preparing
    movies = Movies.query.all()
    genres = []
    for movie in movies:
        for genre in movie.genres:
            genres.append(genre.name)
    data = {
        'Genre': genres
    }

    # Preparing pie chart
    df = pd.DataFrame(data)
    genre_counts = df['Genre'].value_counts()
    plt.figure(figsize=(10, 6))
    plt.pie(genre_counts.values, labels=genre_counts.index, autopct='%1.1f%%')
    plt.title('Žanri')
    plt.tight_layout()

    # Preparing image
    img = BytesIO()
    plt.savefig(img)
    img.seek(0)
    img_b64 = base64.b64encode(img.getvalue()).decode() # Encode to base64

    return render_template('genre_frequency.html', image=img_b64)
