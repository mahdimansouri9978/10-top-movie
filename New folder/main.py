from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import requests


api_key = "1cf2f6bad1b13bd43cadb1ebcc99fb76"
IP_Address = "2605:6440:4015:6000::5b9"
url_get = "https://api.themoviedb.org/3/search/multi"


app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap(app)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///new-books-collection.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=True)
    year = db.Column(db.String(250), unique=True)
    description = db.Column(db.String(1500), unique=True)
    rating = db.Column(db.String(250), unique=True)
    ranking = db.Column(db.String(250), unique=True, nullable=False)
    review = db.Column(db.String(250), unique=True)
    img_url = db.Column(db.String(250), unique=True)

    def __repr__(self):
        return f'<Book {self.title}>'


# db.create_all()


class RateMovieForm(FlaskForm):
    rate = StringField("Your Rating Out of 10 e.g. 7.5", validators=[DataRequired()])
    review = StringField("Your Review", validators=[DataRequired()])
    submit = SubmitField("Done")


class AddMovie(FlaskForm):
    title = StringField("movies name", validators=[DataRequired()])
    submit = SubmitField("Add Movie")


@app.route("/")
def home():
    movies = Movie.query.all()
    return render_template("index.html", movies=movies)


@app.route("/edit", methods=["GET", "POST"])
def rate_movie():
    form = RateMovieForm()
    movie_id = request.args.get("id")
    movie = Movie.query.get(movie_id)
    if form.validate_on_submit():
        movie.rating = form.rate.data
        movie.review = form.review.data
        db.session.commit()
        return redirect(url_for('home'))
    return render_template("edit.html", movie=movie, form=form)


@app.route("/add", methods=["POST", "GET"])
def add():
    add_form = AddMovie()
    if add_form.validate_on_submit():
        movie_title = add_form.title.data
        params = {"api_key": api_key, "query": movie_title}
        req = requests.get(url=url_get, params=params)
        results = req.json()["results"]
        return render_template("select.html", movies=results)
    return render_template("add.html", form=add_form)


@app.route("/select")
def select():
    movie_id = request.args.get("id")
    url_detail = f"https://api.themoviedb.org/3/movie/{movie_id}"
    params = {"api_key": api_key}
    req = requests.get(url=url_detail, params=params)
    print(req.json())
    new_movie = Movie(
        title=req.json()['original_title'],
        year=req.json()['release_date'][0:4],
        description=req.json()["overview"],
        rating="None",
        ranking=req.json()['vote_average'],
        review="None",
        img_url=f"https://image.tmdb.org/t/p/w500{req.json()['poster_path']}"
    )
    db.session.add(new_movie)
    db.session.commit()
    return redirect(url_for("rate_movie"))


@app.route("/delete")
def delete():
    movie_id = request.args.get("id")
    movie = Movie.query.get(movie_id)
    db.session.delete(movie)
    db.session.commit()
    return redirect(url_for("home"))


if __name__ == '__main__':
    app.run(debug=True, port=4000)
