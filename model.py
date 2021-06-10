from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

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