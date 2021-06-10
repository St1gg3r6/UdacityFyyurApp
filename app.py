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
from model import Venue, Shows, GenreAssoc, Genres, States, Artist

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
# moved to model.py

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
    finaldata = []
    listdata = {}
    # SQL: SELECT DISTINCT city, state FROM "Venue";
    outerdata = db.session.query(Venue.city, Venue.state).distinct().all()
    for data in outerdata:
        # SQL: SELECT venueid, name FROM "Venue" WHERE city = ?;
        innerdata = db.session.query(
            Venue.venueid, Venue.name).filter_by(city=data.city).all()
        venueslist = []
        venuesdata = {}
        for venue in innerdata:
            # SQL: SELECT COUNT(*) FROM "Shows" WHERE start_time > DATETIME(today()) AND venueid = ?;
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
    search_term = request.form.get('search_term', '')
    response = {}
    # SQL: SELECT venueid, name FROM "Venue" WHERE UPPER(name) like UPPER('%'+?+'%');
    searchResult = db.session.query(Venue.venueid, Venue.name).filter(
        Venue.name.ilike(f'%{search_term}%')).all()
    countResult = len(searchResult)
    venueList = []
    venueData = {}
    for venue in searchResult:
        # SQL: SELECT COUNT(*) FROM "Shows" WHERE start_time > DATETIME(today()) AND venueid = ?;
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
    selected_venue = Venue.query.get(venue_id)
    # SQL: SELECT * FROM "GenreAssoc" WHERE venueid = ?;
    genres = db.session.query(GenreAssoc).filter_by(venueid=venue_id).all()
    genrelist = []
    for genre in genres:
        genrelist.append(genre.Genres.genre)
    # SQL: SELECT COUNT(*) FROM "Shows" WHERE start_time < DATETIME(today()) AND venueid = ?;
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
    # SQL: SELECT COUNT(*) FROM "Shows" WHERE start_time > DATETIME(today()) AND venueid = ?;
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
    # SQL: SELECT * FROM "Genres" ORDER BY genre;
    genredom = db.session.query(Genres).order_by(Genres.genre).all()
    genrechoices = []
    for item in genredom:
        genreitem = (item.genreid, item.genre)
        genrechoices.append(genreitem)
    form.genres.choices = genrechoices
    # SQL: SELECT * FROM "States" ORDER BY state;
    statedom = db.session.query(States).order_by(States.state).all()
    form.state.choices = [(item.state, item.state) for item in statedom]
    db.session.close()
    return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
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
        # SQL: INSERT INTO "Venue" (<Venue Fields>) VALUES (<Venue Values>);
        db.session.add(newVenue)
        db.session.flush()
        for selectedgenre in request.form.getlist('genres'):
            newGenre = GenreAssoc(
                genreid=int(selectedgenre), venueid=newVenue.venueid)
            # SQL: INSERT INTO "GenreAssoc" (<GenreAssoc Fields>) VALUES (<GenreAssoc Values>);
            db.session.add(newGenre)
        db.session.commit()
        # on successful db insert, flash success
        flash('Venue ' + request.form['name'] + ' was successfully listed!')
    except:
        db.session.rollback()
        flash('There was a problem listing ' +
              request.form['name'] + '. ' + str(sys.exc_info()))
    finally:
        db.session.close()
    return render_template('pages/home.html')


@app.route('/venues/<int:venue_id>/deletevenue', methods=['GET', 'DELETE'])
def delete_venue(venue_id):
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
    return render_template('pages/home.html')

#  Artists
#  ----------------------------------------------------------------


@app.route('/artists')
def artists():
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
