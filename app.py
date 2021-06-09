#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
from os import name
import re
import dateutil.parser
from flask.templating import Environment
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from sqlalchemy.orm import backref, load_only
from sqlalchemy.sql.elements import and_
from forms import *
from flask_migrate import Migrate, current
from datetime import datetime
import sys

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# TODO: connect to a local postgresql database - DONE 31/05/21

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#


class Venue(db.Model):
    __tablename__ = 'Venue'

    venueid = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    city = db.Column(db.String(30), nullable=False)
    state = db.Column(db.String(2), db.ForeignKey(
        'States.state'), nullable=False)
    address = db.Column(db.String(50))
    phone = db.Column(db.String(12))
    website = db.Column(db.String(100))
    image_link = db.Column(db.String(200))
    facebook_link = db.Column(db.String(200))
    seeking_talent = db.Column(db.Boolean, nullable=False)
    seeking_description = db.Column(db.String(200))
    venue_shows = db.relationship('Shows', backref='Venue')
    genre_assoc = db.relationship('GenreAssoc', backref='Venue')

    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    def __repr__(self):
        return f'<Venue {self.venueid} {self.name} >'


class Artist(db.Model):
    __tablename__ = 'Artist'

    artistid = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    city = db.Column(db.String(30), nullable=False)
    state = db.Column(db.String(2), db.ForeignKey(
        'States.state'), nullable=False)
    phone = db.Column(db.String(12))
    website = db.Column(db.String(100))
    image_link = db.Column(db.String(200))
    facebook_link = db.Column(db.String(200))
    seeking_venue = db.Column(db.Boolean, nullable=False)
    seeking_description = db.Column(db.String(200))
    artist_shows = db.relationship('Shows', backref='Artist')
    genre_assoc = db.relationship('GenreAssoc', backref='Artist')

    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    def __repr__(self):
        return f'<Artist {self.artistid} {self.name} {self.city} {self.state}>'

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.


class Shows(db.Model):
    __tablename__ = 'Shows'

    showid = db.Column(db.Integer, primary_key=True)
    venueid = db.Column(db.Integer, db.ForeignKey(
        'Venue.venueid'), nullable=False)
    artistid = db.Column(db.Integer, db.ForeignKey(
        'Artist.artistid'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)

    def __repr__(self):
        return f'<Shows {self.showid} {self.start_time} >'


class Genres(db.Model):
    __tablename__ = 'Genres'

    genreid = db.Column(db.Integer, primary_key=True)
    genre = db.Column(db.String(20), nullable=False)
    genre_assoc = db.relationship('GenreAssoc', backref='Genres')

    def __repr__(self):
        return f'<Genres {self.genreid} {self.genre}>'


class GenreAssoc(db.Model):
    __tablename__ = 'GenreAssoc'

    genreassocid = db.Column(db.Integer, primary_key=True)
    genreid = db.Column(db.Integer, db.ForeignKey(
        'Genres.genreid'), nullable=False)
    venueid = db.Column(db.Integer, db.ForeignKey(
        'Venue.venueid'), nullable=True)
    artistid = db.Column(db.Integer, db.ForeignKey(
        'Artist.artistid'), nullable=True)

    def __repr__(self):
        return f'<GenreAssoc {self.genreassocid}>'


class States(db.Model):
    __tablename__ = 'States'

    state = db.Column(db.String(2), primary_key=True)
    venue = db.relationship('Venue', backref='states')
    artist = db.relationship('Artist', backref='states')

    def __repr__(self):
        return f'<State (abbr) {self.state}'

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#


def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(str(value))
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format, locale='en')


app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#


@app.route('/')
def index():
    return render_template('pages/home.html')


@app.route('/testdata')
def testOutput():
    finaldata = []
    venue_id = 1
    maindata = db.session.query(Venue).filter_by(venueid=venue_id).all()
    print(maindata)
    # finaldata = maindata
    db.session.close()
    return render_template('pages/test.html', testdata=maindata)


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
    # TODO: replace with real venues data.
    #       num_shows should be aggregated based on number of upcoming shows per venue.
    # data = [{
    #     "city": "San Francisco",
    #     "state": "CA",
    #     "venues": [{
    #         "id": 1,
    #         "name": "The Musical Hop",
    #         "num_upcoming_shows": 0,
    #     }, {
    #         "id": 3,
    #         "name": "Park Square Live Music & Coffee",
    #         "num_upcoming_shows": 1,
    #     }]
    # }, {
    #     "city": "New York",
    #     "state": "NY",
    #     "venues": [{
    #         "id": 2,
    #         "name": "The Dueling Pianos Bar",
    #         "num_upcoming_shows": 0,
    #     }]
    # }]
    finaldata = []
    listdata = {}
    outerdata = db.session.query(Venue.city, Venue.state).distinct().all()
    for data in outerdata:
        innerdata = db.session.query(
            Venue.venueid, Venue.name).filter_by(city=data.city).all()
        venueslist = []
        venuesdata = {}
        for venue in innerdata:
            showcount = db.session.query(Shows).filter(
                datetime.today() < Shows.start_time).filter_by(venueid=venue.venueid).count()
            venuesdata = {
                "id": venue.venueid,
                "name": venue.name,
                "num_upcoming_shows": showcount
            }
            venueslist.append(venuesdata)
        listdata = {
            "city": data.city,
            "state": data.state,
            "venues": venueslist
        }
        finaldata.append(listdata)
        db.session.close()
    return render_template('pages/venues.html', areas=finaldata)


@app.route('/venues/search', methods=['POST'])
def search_venues():
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for Hop should return "The Musical Hop".
    # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
    # response = {
    #     "count": 1,
    #     "data": [{
    #         "id": 2,
    #         "name": "The Dueling Pianos Bar",
    #         "num_upcoming_shows": 0,
    #     }]
    # }
    search_term = request.form.get('search_term', '')
    response = {}
    searchResult = db.session.query(Venue.venueid, Venue.name).filter(
        Venue.name.ilike(f'%{search_term}%')).all()
    countResult = len(searchResult)
    venueList = []
    venueData = {}
    for venue in searchResult:
        upcomingShowsCount = db.session.query(Shows).filter(
            datetime.today() < Shows.start_time).filter_by(venueid=venue.venueid).count()
        venueData = {
            "id": venue.venueid,
            "name": venue.name,
            "num_upcoming_shows": upcomingShowsCount
        }
        venueList.append(venueData)
    response = {
        "count": countResult,
        "data": venueList
    }
    db.session.close()
    return render_template('pages/search_venues.html', results=response, search_term=search_term)


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    # shows the venue page with the given venue_id
    # TODO: replace with real venue data from the venues table, using venue_id
    # data1 = {
    #     "id": 1,
    #     "name": "The Musical Hop",
    #     "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
    #     "address": "1015 Folsom Street",
    #     "city": "San Francisco",
    #     "state": "CA",
    #     "phone": "123-123-1234",
    #     "website": "https://www.themusicalhop.com",
    #     "facebook_link": "https://www.facebook.com/TheMusicalHop",
    #     "seeking_talent": True,
    #     "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
    #     "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
    #     "past_shows": [{
    #         "artist_id": 4,
    #         "artist_name": "Guns N Petals",
    #         "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
    #         "start_time": "2019-05-21T21:30:00.000Z"
    #     }],
    #     "upcoming_shows": [],
    #     "past_shows_count": 1,
    #     "upcoming_shows_count": 0,
    # }
    # data2 = {
    #     "id": 2,
    #     "name": "The Dueling Pianos Bar",
    #     "genres": ["Classical", "R&B", "Hip-Hop"],
    #     "address": "335 Delancey Street",
    #     "city": "New York",
    #     "state": "NY",
    #     "phone": "914-003-1132",
    #     "website": "https://www.theduelingpianos.com",
    #     "facebook_link": "https://www.facebook.com/theduelingpianos",
    #     "seeking_talent": False,
    #     "image_link": "https://images.unsplash.com/photo-1497032205916-ac775f0649ae?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=750&q=80",
    #     "past_shows": [],
    #     "upcoming_shows": [],
    #     "past_shows_count": 0,
    #     "upcoming_shows_count": 0,
    # }
    # data3 = {
    #     "id": 3,
    #     "name": "Park Square Live Music & Coffee",
    #     "genres": ["Rock n Roll", "Jazz", "Classical", "Folk"],
    #     "address": "34 Whiskey Moore Ave",
    #     "city": "San Francisco",
    #     "state": "CA",
    #     "phone": "415-000-1234",
    #     "website": "https://www.parksquarelivemusicandcoffee.com",
    #     "facebook_link": "https://www.facebook.com/ParkSquareLiveMusicAndCoffee",
    #     "seeking_talent": False,
    #     "image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
    #     "past_shows": [{
    #         "artist_id": 5,
    #         "artist_name": "Matt Quevedo",
    #         "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
    #         "start_time": "2019-06-15T23:00:00.000Z"
    #     }],
    #     "upcoming_shows": [{
    #         "artist_id": 6,
    #         "artist_name": "The Wild Sax Band",
    #         "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    #         "start_time": "2035-04-01T20:00:00.000Z"
    #     }, {
    #         "artist_id": 6,
    #         "artist_name": "The Wild Sax Band",
    #         "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    #         "start_time": "2035-04-08T20:00:00.000Z"
    #     }, {
    #         "artist_id": 6,
    #         "artist_name": "The Wild Sax Band",
    #         "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    #         "start_time": "2035-04-15T20:00:00.000Z"
    #     }],
    #     "past_shows_count": 1,
    #     "upcoming_shows_count": 1,
    # }
    # data = list(filter(lambda d: d['id'] ==
    #             venue_id, [data1, data2, data3]))[0]

    selected_venue = Venue.query.get(venue_id)
    genres = db.session.query(GenreAssoc).filter_by(venueid=venue_id).all()
    genrelist = []
    for genre in genres:
        genrelist.append(genre.Genres.genre)
    pastshows = db.session.query(Shows).filter(
        Shows.start_time < datetime.today()).filter_by(venueid=venue_id).all()
    pastshowslist = []
    for show in pastshows:
        pastshowsdetails = {
            "artist_id": show.Artist.artistid,
            "artist_name": show.Artist.name,
            "artist_image_link": show.Artist.image_link,
            "start_time": show.start_time
        }
        pastshowslist.append(pastshowsdetails)
    pastshowscount = len(pastshows)
    upcomingshows = db.session.query(Shows).filter(
        Shows.start_time > datetime.today()).filter_by(venueid=venue_id).all()
    upcomingshowslist = []
    for show in upcomingshows:
        upcomingshowsdetails = {
            "artist_id": show.Artist.artistid,
            "artist_name": show.Artist.name,
            "artist_image_link": show.Artist.image_link,
            "start_time": show.start_time
        }
        upcomingshowslist.append(upcomingshowsdetails)
    upcomingshowscount = len(upcomingshows)
    data = {
        "id": selected_venue.venueid,
        "name": selected_venue.name,
        "genres": genrelist,
        "address": selected_venue.address,
        "city": selected_venue.city,
        "state": selected_venue.state,
        "phone": selected_venue.phone,
        "website": selected_venue.website,
        "facebook_link": selected_venue.facebook_link,
        "seeking_talent": selected_venue.seeking_talent,
        "seeking_description": selected_venue.seeking_description,
        "image_link": selected_venue.image_link,
        "past_shows": pastshowslist,
        "upcoming_shows": upcomingshowslist,
        "past_shows_count": pastshowscount,
        "upcoming_shows_count": upcomingshowscount
    }
    db.session.close()
    return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------


@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    genredom = db.session.query(Genres).order_by(Genres.genre).all()
    genrechoices = []
    for item in genredom:
        genreitem = (item.genreid, item.genre)
        genrechoices.append(genreitem)
    form.genres.choices = genrechoices
    statedom = db.session.query(States).order_by(States.state).all()
    form.state.choices = [(item.state, item.state) for item in statedom]
    db.session.close()
    return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    # TODO: insert form data as a new Venue record in the db, instead
    # TODO: modify data to be the data object returned from db insertion
    try:
        newVenue = Venue(
            name=request.form['name'],
            city=request.form['city'],
            state=request.form['state'],
            address=request.form['address']
        )
        newVenue.phone = request.form['phone'] if request.form['phone'] is not None else None
        newVenue.facebook_link = request.form['facebook_link'] if request.form['facebook_link'] is not None else None
        newVenue.image_link = request.form['image_link'] if request.form['image_link'] is not None else None
        newVenue.website = request.form['website_link'] if request.form['website_link'] is not None else None
        newVenue.seeking_talent = True if request.form.get(
            'seeking_talent') else False
        newVenue.seeking_description = request.form['seeking_description'] if request.form[
            'seeking_description'] is not None else None
        db.session.add(newVenue)
        db.session.flush()
        for selectedgenre in request.form.getlist('genres'):
            newGenre = GenreAssoc(
                genreid=int(selectedgenre), venueid=newVenue.venueid)
            db.session.add(newGenre)
        db.session.commit()
        # on successful db insert, flash success
        flash('Venue ' + request.form['name'] + ' was successfully listed!')
    except:
        # TODO: on unsuccessful db insert, flash an error instead.
        # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
        # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
        db.session.rollback()
        flash('There was a problem listing ' +
              request.form['name'] + '. ' + str(sys.exc_info()))
    finally:
        db.session.close()
    return render_template('pages/home.html')


@app.route('/venues/<int:venue_id>/deletevenue', methods=['GET', 'DELETE'])
def delete_venue(venue_id):
    # TODO: Complete this endpoint for taking a venue_id, and using
    # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
    try:
        shows = Shows.query.filter_by(venueid=venue_id).all()
        for show in shows:
            db.session.delete(show)
        genres = GenreAssoc.query.filter_by(venueid=venue_id).all()
        for genre in genres:
            db.session.delete(genre)
        venue = Venue.query.get(venue_id)
        db.session.delete(venue)
        db.session.commit()
    except:
        db.session.rollback()
        flash('There was a problem deleting this venue.')
    finally:
        db.session.close()
    # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
    # clicking that button delete it from the db then redirect the user to the homepage
    return render_template('pages/home.html')

#  Artists
#  ----------------------------------------------------------------


@app.route('/artists')
def artists():
    # TODO: replace with real data returned from querying the database
    # data = [{
    #     "id": 4,
    #     "name": "Guns N Petals",
    # }, {
    #     "id": 5,
    #     "name": "Matt Quevedo",
    # }, {
    #     "id": 6,
    #     "name": "The Wild Sax Band",
    # }]
    artistdata = db.session.query(Artist.artistid, Artist.name).all()
    data = []
    for artist in artistdata:
        artistout = {
            "id": artist.artistid,
            "name": artist.name
        }
        data.append(artistout)
    db.session.close()
    return render_template('pages/artists.html', artists=data)


@app.route('/artists/search', methods=['POST'])
def search_artists():
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
    # search for "band" should return "The Wild Sax Band".
    # response = {
    #     "count": 1,
    #     "data": [{
    #         "id": 4,
    #         "name": "Guns N Petals",
    #         "num_upcoming_shows": 0,
    #     }]
    # }
    search_term = request.form.get('search_term', '')
    response = {}
    searchResult = db.session.query(Artist.artistid, Artist.name).filter(
        Artist.name.ilike(f'%{search_term}%')).all()
    countResult = len(searchResult)
    artistList = []
    artistData = {}
    for artist in searchResult:
        upcomingShowsCount = db.session.query(Shows).filter(
            datetime.today() < Shows.start_time).filter_by(artistid=artist.artistid).count()
        artistData = {
            "id": artist.artistid,
            "name": artist.name,
            "num_upcoming_shows": upcomingShowsCount
        }
        artistList.append(artistData)
    response = {
        "count": countResult,
        "data": artistList
    }
    db.session.close()
    return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    # shows the artist page with the given artist_id
    # TODO: replace with real artist data from the artist table, using artist_id
    # data1 = {
    #     "id": 1,
    #     "name": "Guns N Petals",
    #     "genres": ["Rock n Roll"],
    #     "city": "San Francisco",
    #     "state": "CA",
    #     "phone": "326-123-5000",
    #     "website": "https://www.gunsnpetalsband.com",
    #     "facebook_link": "https://www.facebook.com/GunsNPetals",
    #     "seeking_venue": True,
    #     "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
    #     "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
    #     "past_shows": [{
    #         "venue_id": 1,
    #         "venue_name": "The Musical Hop",
    #         "venue_image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
    #         "start_time": "2019-05-21T21:30:00.000Z"
    #     }],
    #     "upcoming_shows": [],
    #     "past_shows_count": 1,
    #     "upcoming_shows_count": 0,
    # }
    # data2 = {
    #     "id": 5,
    #     "name": "Matt Quevedo",
    #     "genres": ["Jazz"],
    #     "city": "New York",
    #     "state": "NY",
    #     "phone": "300-400-5000",
    #     "facebook_link": "https://www.facebook.com/mattquevedo923251523",
    #     "seeking_venue": False,
    #     "image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
    #     "past_shows": [{
    #         "venue_id": 3,
    #         "venue_name": "Park Square Live Music & Coffee",
    #         "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
    #         "start_time": "2019-06-15T23:00:00.000Z"
    #     }],
    #     "upcoming_shows": [],
    #     "past_shows_count": 1,
    #     "upcoming_shows_count": 0,
    # }
    # data3 = {
    #     "id": 6,
    #     "name": "The Wild Sax Band",
    #     "genres": ["Jazz", "Classical"],
    #     "city": "San Francisco",
    #     "state": "CA",
    #     "phone": "432-325-5432",
    #     "seeking_venue": False,
    #     "image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    #     "past_shows": [],
    #     "upcoming_shows": [{
    #         "venue_id": 3,
    #         "venue_name": "Park Square Live Music & Coffee",
    #         "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
    #         "start_time": "2035-04-01T20:00:00.000Z"
    #     }, {
    #         "venue_id": 3,
    #         "venue_name": "Park Square Live Music & Coffee",
    #         "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
    #         "start_time": "2035-04-08T20:00:00.000Z"
    #     }, {
    #         "venue_id": 3,
    #         "venue_name": "Park Square Live Music & Coffee",
    #         "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
    #         "start_time": "2035-04-15T20:00:00.000Z"
    #     }],
    #     "past_shows_count": 0,
    #     "upcoming_shows_count": 3,
    # }
    # data = list(filter(lambda d: d['id'] ==
    #             artist_id, [data1, data2, data3]))[0]

    selected_artist = Artist.query.get(artist_id)
    genres = db.session.query(GenreAssoc).filter_by(artistid=artist_id).all()
    genrelist = []
    for genre in genres:
        genrelist.append(genre.Genres.genre)
    pastshows = db.session.query(Shows).filter(
        Shows.start_time < datetime.today()).filter_by(artistid=artist_id).all()
    pastshowslist = []
    for show in pastshows:
        pastshowsdetails = {
            "venue_id": show.Venue.venueid,
            "venue_name": show.Venue.name,
            "venue_image_link": show.Venue.image_link,
            "start_time": show.start_time
        }
        pastshowslist.append(pastshowsdetails)
    pastshowscount = len(pastshows)
    upcomingshows = db.session.query(Shows).filter(
        Shows.start_time > datetime.today()).filter_by(artistid=artist_id).all()
    upcomingshowslist = []
    for show in upcomingshows:
        upcomingshowsdetails = {
            "venue_id": show.Venue.venueid,
            "venue_name": show.Venue.name,
            "venue_image_link": show.Venue.image_link,
            "start_time": show.start_time
        }
        upcomingshowslist.append(upcomingshowsdetails)
    upcomingshowscount = len(upcomingshows)
    data = {
        "id": selected_artist.artistid,
        "name": selected_artist.name,
        "genres": genrelist,
        "city": selected_artist.city,
        "state": selected_artist.state,
        "phone": selected_artist.phone,
        "seeking_venue": selected_artist.seeking_venue,
        "seeking_description": selected_artist.seeking_description if selected_artist.seeking_description is not None else None,
        "image_link": selected_artist.image_link,
        "past_shows": pastshowslist,
        "upcoming_shows": upcomingshowslist,
        "past_shows_count": pastshowscount,
        "upcoming_shows_count": upcomingshowscount
    }
    db.session.close()
    return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------


@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    form = ArtistForm()
    # artist = {
    #     "id": 4,
    #     "name": "Guns N Petals",
    #     "genres": ["Rock n Roll"],
    #     "city": "San Francisco",
    #     "state": "CA",
    #     "phone": "326-123-5000",
    #     "website": "https://www.gunsnpetalsband.com",
    #     "facebook_link": "https://www.facebook.com/GunsNPetals",
    #     "seeking_venue": True,
    #     "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
    #     "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80"
    # }
    # TODO: populate form with fields from artist with ID <artist_id>
    artistdata = Artist.query.get(artist_id)
    genres = db.session.query(GenreAssoc).filter_by(artistid=artist_id).all()
    genrelist = []
    for genre in genres:
        genretuple = (str(genre.Genres.genreid))
        genrelist.append(genretuple)
    artist = {
        "id": artistdata.artistid,
        "name": artistdata.name,
        "genres": genrelist,
        "city": artistdata.city,
        "state": artistdata.state,
        "phone": artistdata.phone,
        "website": artistdata.website,
        "facebook_link": artistdata.facebook_link,
        "seeking_venue": artistdata.seeking_venue,
        "seeking_description": artistdata.seeking_description,
        "image_link": artistdata.image_link
    }
    genredom = db.session.query(Genres).order_by(Genres.genre).all()
    genrechoices = []
    for item in genredom:
        genreitem = (item.genreid, item.genre)
        genrechoices.append(genreitem)
    form.genres.choices = genrechoices
    form.city.data = artistdata.city
    form.state.data = artistdata.state
    form.phone.data = artistdata.phone
    form.genres.data = genrelist
    form.facebook_link.data = artistdata.facebook_link
    form.image_link.data = artistdata.image_link
    form.website_link.data = artistdata.website
    form.seeking_venue.data = artistdata.seeking_venue
    form.seeking_description.data = artistdata.seeking_description
    form.name.data = artistdata.name
    db.session.close()
    return render_template('forms/edit_artist.html', form=form, artist=artist)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    # TODO: take values from the form submitted, and update existing
    # artist record with ID <artist_id> using the new attributes
    try:
        currentartist = Artist.query.get(artist_id)
        if (currentartist.name != request.form['name']):
            currentartist.name = request.form['name']
        if (currentartist.city != request.form['city']):
            currentartist.city = request.form['city']
        if (currentartist.state != request.form['state']):
            currentartist.state = request.form['state']
        if (currentartist.phone != request.form['phone']):
            currentartist.phone = request.form['phone']
        if (currentartist.facebook_link != request.form['facebook_link']):
            currentartist.facebook_link = request.form['facebook_link']
        if (currentartist.image_link != request.form['image_link']):
            currentartist.image_link = request.form['image_link']
        if (currentartist.website != request.form['website_link']):
            currentartist.website = request.form['website_link']
        if (currentartist.seeking_venue and request.form.get('seeking_venue') is None):
            currentartist.seeking_venue = False
        if (not currentartist.seeking_venue and request.form.get('seeking_venue')):
            currentartist.seeking_venue = True
        if (currentartist.seeking_description != request.form['seeking_description']):
            currentartist.seeking_description = request.form['seeking_description']
        oldgenres = GenreAssoc.query.filter_by(artistid=artist_id).all()
        for oldgenre in oldgenres:
            db.session.delete(oldgenre)
        for selectedgenre in request.form.getlist('genres'):
            newGenre = GenreAssoc(genreid=int(
                selectedgenre), artistid=artist_id)
            db.session.add(newGenre)
        db.session.commit()
    except:
        db.session.rollback()
    finally:
        db.session.close()
    return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    form = VenueForm()
    # venue = {
    #     "id": 1,
    #     "name": "The Musical Hop",
    #     "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
    #     "address": "1015 Folsom Street",
    #     "city": "San Francisco",
    #     "state": "CA",
    #     "phone": "123-123-1234",
    #     "website": "https://www.themusicalhop.com",
    #     "facebook_link": "https://www.facebook.com/TheMusicalHop",
    #     "seeking_talent": True,
    #     "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
    #     "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60"
    # }
    # TODO: populate form with values from venue with ID <venue_id>
    venuedata = Venue.query.get(venue_id)
    genres = db.session.query(GenreAssoc).filter_by(venueid=venue_id).all()
    genrelist = []
    for genre in genres:
        genrelist.append(str(genre.Genres.genreid))
    venue = {
        "id": venuedata.venueid,
        "name": venuedata.name,
        "genres": genrelist,
        "address": venuedata.address,
        "city": venuedata.city,
        "state": venuedata.state,
        "phone": venuedata.phone,
        "website": venuedata.website,
        "facebook_link": venuedata.facebook_link,
        "seeking_talent": venuedata.seeking_talent,
        "seeking_description": venuedata.seeking_description,
        "image_link": venuedata.image_link
    }
    genredom = db.session.query(Genres).order_by(Genres.genre).all()
    genrechoices = []
    for item in genredom:
        genreitem = (item.genreid, item.genre)
        genrechoices.append(genreitem)
    form.genres.choices = genrechoices
    form.city.data = venuedata.city
    form.state.data = venuedata.state
    form.address.data = venuedata.address
    form.phone.data = venuedata.phone
    form.image_link.data = venuedata.image_link
    form.genres.data = genrelist
    form.facebook_link.data = venuedata.facebook_link
    form.website_link.data = venuedata.website
    form.seeking_talent.data = venuedata.seeking_talent
    form.seeking_description.data = venuedata.seeking_description
    form.name.data = venuedata.name
    db.session.close()
    return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    # TODO: take values from the form submitted, and update existing
    # venue record with ID <venue_id> using the new attributes
    try:
        currentvenue = Venue.query.get(venue_id)
        if (currentvenue.name != request.form['name']):
            currentvenue.name = request.form['name']
        if (currentvenue.address != request.form['address']):
            currentvenue.address = request.form['address']
        if (currentvenue.city != request.form['city']):
            currentvenue.city = request.form['city']
        if (currentvenue.state != request.form['state']):
            currentvenue.state = request.form['state']
        if (currentvenue.phone != request.form['phone']):
            currentvenue.phone = request.form['phone']
        if (currentvenue.website != request.form['website_link']):
            currentvenue.website = request.form['website_link']
        if (currentvenue.facebook_link != request.form['facebook_link']):
            currentvenue.facebook_link = request.form['facebook_link']
        if (currentvenue.image_link != request.form['image_link']):
            currentvenue.image_link = request.form['image_link']
        if (currentvenue.seeking_talent and request.form.get('seeking_talent') is None):
            currentvenue.seeking_talent = False
        if (not currentvenue.seeking_talent and request.form.get('seeking_talent')):
            currentvenue.seeking_talent = True
        if (currentvenue.seeking_description != request.form['seeking_description']):
            currentvenue.seeking_description = request.form['seeking_description']
        oldgenres = GenreAssoc.query.filter_by(venueid=venue_id).all()
        for oldgenre in oldgenres:
            db.session.delete(oldgenre)
        for selectedgenre in request.form.getlist('genres'):
            newGenre = GenreAssoc(genreid=int(selectedgenre), venueid=venue_id)
            db.session.add(newGenre)
        db.session.commit()
    except:
        db.session.rollback()
    finally:
        db.session.close()
    return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------


@app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    genredom = db.session.query(Genres).order_by(Genres.genre).all()
    genrechoices = []
    for item in genredom:
        genreitem = (item.genreid, item.genre)
        genrechoices.append(genreitem)
    form.genres.choices = genrechoices
    db.session.close()
    return render_template('forms/new_artist.html', form=form)


@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    # called upon submitting the new artist listing form
    # TODO: insert form data as a new Venue record in the db, instead
    # TODO: modify data to be the data object returned from db insertion
    try:
        newArtist = Artist(
            name=request.form['name'],
            city=request.form['city'],
            state=request.form['state']
        )
        newArtist.phone = request.form['phone'] if request.form['phone'] is not None else None
        newArtist.image_link = request.form['image_link'] if request.form['image_link'] is not None else None
        newArtist.facebook_link = request.form['facebook_link'] if request.form['facebook_link'] is not None else None
        newArtist.website = request.form['website'] if request.form['website'] is not None else None
        newArtist.seeking_venue = True if request.form.get(
            'seeking_venue') else False
        newArtist.seeking_description = request.form['seeking_description'] if request.form[
            'seeking_description'] is not None else None
        db.session.add(newArtist)
        db.session.flush()
        for selectedgenre in request.form.getlist('genres'):
            newGenre = GenreAssoc(genreid=int(
                selectedgenre), artistid=newArtist.artistid)
            db.session.add(newGenre)
        db.session.commit()
    # on successful db insert, flash success
        flash('Artist ' + request.form['name'] + ' was successfully listed!')
    except:
        # TODO: on unsuccessful db insert, flash an error instead.
        # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
        db.session.rollback()
        flash('There was a problem listing ' +
              request.form['name'] + '. ' + str(sys.exc_info()))
    finally:
        db.session.close()
    return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    # displays list of shows at /shows
    # TODO: replace with real venues data.
    #       num_shows should be aggregated based on number of upcoming shows per venue.
    # data = [{
    #     "venue_id": 1,
    #     "venue_name": "The Musical Hop",
    #     "artist_id": 4,
    #     "artist_name": "Guns N Petals",
    #     "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
    #     "start_time": "2019-05-21T21:30:00.000Z"
    # }, {
    #     "venue_id": 3,
    #     "venue_name": "Park Square Live Music & Coffee",
    #     "artist_id": 5,
    #     "artist_name": "Matt Quevedo",
    #     "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
    #     "start_time": "2019-06-15T23:00:00.000Z"
    # }, {
    #     "venue_id": 3,
    #     "venue_name": "Park Square Live Music & Coffee",
    #     "artist_id": 6,
    #     "artist_name": "The Wild Sax Band",
    #     "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    #     "start_time": "2035-04-01T20:00:00.000Z"
    # }, {
    #     "venue_id": 3,
    #     "venue_name": "Park Square Live Music & Coffee",
    #     "artist_id": 6,
    #     "artist_name": "The Wild Sax Band",
    #     "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    #     "start_time": "2035-04-08T20:00:00.000Z"
    # }, {
    #     "venue_id": 3,
    #     "venue_name": "Park Square Live Music & Coffee",
    #     "artist_id": 6,
    #     "artist_name": "The Wild Sax Band",
    #     "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    #     "start_time": "2035-04-15T20:00:00.000Z"
    # }]
    showsdata = db.session.query(Shows).all()
    data = []
    for show in showsdata:
        showout = {
            "venue_id": show.venueid,
            "venue_name": show.Venue.name,
            "artist_id": show.artistid,
            "artist_name": show.Artist.name,
            "artist_image_link": show.Artist.image_link,
            "start_time": show.start_time
        }
        data.append(showout)
    db.session.close()
    return render_template('pages/shows.html', shows=data)


@app.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    try:
        # called to create new shows in the db, upon submitting new show listing form
        # TODO: insert form data as a new Show record in the db, instead
        if (Venue.query.get(request.form['venue_id']) is not None
                and Artist.query.get(request.form['artist_id']) is not None):
            newShow = Shows(venueid=int(request.form['venue_id']), artistid=int(
                request.form['artist_id']), start_time=request.form['start_time'])
            db.session.add(newShow)
            db.session.commit()
            # on successful db insert, flash success
            flash('Show was successfully listed!')
        else:
            flash('One of either the Venue or Artist IDs is not valid.')
    except:
        # TODO: on unsuccessful db insert, flash an error instead.
        # e.g., flash('An error occurred. Show could not be listed.')
        # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
        db.session.rollback()
        flash('There was a problem listing this show. ', str(sys.exc_info()))
    finally:
        db.session.close()
    return render_template('pages/home.html')


@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
