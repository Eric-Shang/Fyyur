from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

db= SQLAlchemy()

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    genres = db.Column(db.ARRAY(db.String))
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    website = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean, nullable=False, default = False)
    seeking_description = db.Column(db.String(500))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    shows = db.relationship('Show', backref='Venue', cascade="all, delete-orphan", lazy="dynamic")

    def info(self):
      return {
            'id': self.id,
            'name': self.name,
            'genres': self.genres,
            'address': self.address,
            'city': self.city,
            'state': self.state,
            'phone': self.phone,
            'website': self.website,
            'facebook_link': self.facebook_link,
            'seeking_talent': self.seeking_talent,
            'seeking_description': self.seeking_description,
            'image_link': self.image_link
      }

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    genres = db.Column(db.ARRAY(db.String))
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    website = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean, nullable=False, default = False)
    seeking_description = db.Column(db.String(500))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    shows = db.relationship('Show', backref='Artist', cascade="all, delete-orphan", lazy="dynamic")

    def info(self):
      return{
        'id': self.id,
        'name': self.name,
        'genres': self.genres,
        'city': self.city,
        'state': self.state,
        'phone': self.phone,
        'website': self.website,
        'facebook_link': self.facebook_link,
        'seeking_venue': self.seeking_venue,
        'seeking_description': self.seeking_description,
        'image_link': self.image_link
      }

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
class Show(db.Model):
  __tablename__ = 'Show'
  id = db.Column(db.Integer, primary_key=True)
  venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)
  artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable=False)
  start_time = db.Column(db.DateTime, nullable=False)


  def info(self):
    return{
      'venue_id': self.venue_id,
      'venue_name': self.Venue.name,
      'artist_id': self.artist_id,
      'artist_name': self.Artist.name,
      'artist_image_link': self.Artist.image_link,
      'start_time': self.start_time
    }

  def artist_info(self):
    return{
      'artist_id': self.artist_id,
      'artist_name': self.Artist.name,
      'artist_image_link': self.Artist.image_link,
      'start_time': self.start_time
    }

  def venue_info(self):
    return{
      'venue_id': self.venue_id,
      'venue_name': self.Venue.name,
      'venue_image_link': self.Venue.image_link,
      'start_time': self.start_time
    }

