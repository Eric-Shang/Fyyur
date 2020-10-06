#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, jsonify
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import sessionmaker
import logging
from logging import Formatter, FileHandler
from forms import *
from models import db, Venue, Artist, Show
from flask_migrate import Migrate

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
migrate = Migrate(app, db)
Session = sessionmaker(autoflush=False)

def create_app():
    app.config.from_object('config')
    db.init_app(app)
    return app

with app.app_context():
    db.init_app(app)

# TODO: connect to a local postgresql database


#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.

  data = []
  current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
  venue_query = Venue.query.group_by(Venue.id, Venue.city, Venue.state).all()

  if venue_query:
    for venue in venue_query:
      upcoming_shows = venue.shows.filter(Show.start_time > current_time).all()
      data.append({
        "city": venue.city,
        "state": venue.state,
        "venues": [{
          "id": venue.id,
          "name": venue.name,
          "num_upcoming_shows": len(upcoming_shows)
        }]
      })

  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  venue_query = Venue.query.filter(Venue.name.ilike('%' + request.form['search_term'] + '%')).all()
  venue_array = list()
  for venue in venue_query:
      info = {"id": venue.id, "name": venue.name}
      venue_array.append(info)

  response = {
      "count": len(venue_array),
      "data": venue_array
  }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id


  venue_query = Venue.query.get(venue_id)

  if venue_query:
    venue_info = Venue.info(venue_query)
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    new_shows_query = Show.query.options(db.joinedload('Artist')).filter(Show.venue_id == venue_id).filter(
      Show.start_time > current_time).all()
    new_show = list(map(Show.artist_info, new_shows_query))
    venue_info["upcoming_shows"] = new_show
    venue_info["upcoming_shows_count"] = len(new_show)
    past_shows_query = Show.query.options(db.joinedload('Artist')).filter(Show.venue_id == venue_id).filter(
      Show.start_time <= current_time).all()
    past_shows = list(map(Show.artist_info, past_shows_query))
    venue_info["past_shows"] = past_shows
    venue_info["past_shows_count"] = len(past_shows)

    # data = list(filter(lambda d: d['id'] == venue_id, [data1, data2, data3]))[0]
    return render_template('pages/show_venue.html', venue=venue_info)
  else:
    return render_template('errors/404.html')

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion

  data = request.form
  try:
    seeking_talent = False
    if 'seeking_talent' in request.form:
      seeking_talent = (request.form['seeking_talent'] == 'y')
    new_venue = Venue(
      genres=data.getlist("genres"),
      name=data.get("name"),
      address=data.get("address"),
      city=data.get("city"),
      state=data.get("state"),
      facebook_link=data.get("facebook_link"),
      phone=data.get("phone"),
      website=data.get("website_link"),
      image_link=data.get("image_link"),
      seeking_talent=seeking_talent,
      seeking_description=data.get("seeking_description")
    )
    db.session.add(new_venue)
    db.session.commit()
  # on successful db insert, flash success
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  except:
    db.session.rollback()
    flash('An error occurred. Venue ' + data['name'] + ' could not be listed.')
  finally:
    db.session.close()
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
 try:
  venue_query = Venue.query.get(venue_id)
  # clicking that button delete it from the db then redirect the user to the homepage

  #db.session.delete(venue_query)
  db.session.delete(venue_query)
  db.session.commit()
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  flash('Venue ' + venue_query.name + ' was successfully deleted!')
 except:
  db.session.rollback()
  flash('An error occurred. Venue ' + venue_query.name + ' could not be deleted.')
 finally:
  db.session.close()
 return jsonify()

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  data1=[{
    "id": 4,
    "name": "Guns N Petals",
  }, {
    "id": 5,
    "name": "Matt Quevedo",
  }, {
    "id": 6,
    "name": "The Wild Sax Band",
  }]

  data = []
  artist_query = Artist.query.all()

  if artist_query:
    for artist in artist_query:
      data.append({
          "id": artist.id,
          "name": artist.name,
      })

  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  artist_query = Artist.query.filter(Artist.name.ilike('%' + request.form['search_term'] + '%')).all()
  artist_array = list()
  for artist in artist_query:
      info = {"id": artist.id, "name": artist.name}
      artist_array.append(info)

  response = {
      "count": len(artist_array),
      "data": artist_array
  }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id



  artist_query = Artist.query.get(artist_id)

  if artist_query:
    artist_info = Artist.info(artist_query)
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    new_shows_query = Show.query.options(db.joinedload('Venue')).filter(Show.artist_id == artist_id).filter(
      Show.start_time > current_time).all()
    new_show = list(map(Show.venue_info, new_shows_query))
    artist_info["upcoming_shows"] = new_show
    artist_info["upcoming_shows_count"] = len(new_show)
    past_shows_query = Show.query.options(db.joinedload('Venue')).filter(Show.artist_id == artist_id).filter(
      Show.start_time <= current_time).all()
    past_shows = list(map(Show.venue_info, past_shows_query))
    artist_info["past_shows"] = past_shows
    artist_info["past_shows_count"] = len(past_shows)

    # data = list(filter(lambda d: d['id'] == venue_id, [data1, data2, data3]))[0]
    return render_template('pages/show_artist.html', artist=artist_info)
  else:
    return render_template('errors/404.html')

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):

  # TODO: populate form with fields from artist with ID <artist_id>
  form = ArtistForm()
  artist_query = Artist.query.get(artist_id)

  if artist_query:
      artist = Artist.info(artist_query)
      form.name.data = artist_query.name
      form.city.data = artist_query.city
      form.state.data = artist_query.state
      form.phone.data = artist_query.phone
      form.genres.data = artist_query.genres
      form.seeking_venue.data = artist_query.seeking_venue
      form.seeking_description.data = artist_query.seeking_description
      form.facebook_link.data = artist_query.facebook_link
      form.website_link.data = artist_query.website
      form.image_link.data = artist_query.image_link
      return render_template('forms/edit_artist.html', form=form, artist=artist)
  return render_template('errors/404.html')
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):

  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  artist_query = Artist.query.get(artist_id)
  data = request.form
  try:
      if artist_query:
          seeking_venue = False
          if 'seeking_venue' in request.form:
              seeking_venue = (request.form['seeking_venue'] == 'y')
          artist_query.genres = data.getlist("genres")
          artist_query.city = data.get("city")
          artist_query.state = data.get("state")
          artist_query.facebook_link = data.get("facebook_link")
          artist_query.phone = data.get("phone")
          artist_query.website = data.get("website_link")
          artist_query.image_link = data.get("image_link")
          artist_query.seeking_venue = seeking_venue
          artist_query.seeking_description = data.get("seeking_description")
          db.session.commit()
          flash('Artist ' + request.form['name'] + ' was successfully edited!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  except:
      db.session.rollback()
      flash('An error occurred. Artist ' + data['name'] + ' could not be edited.')
  finally:
      db.session.close()
      # artist record with ID <artist_id> using the new attributes
  return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue_query = Venue.query.get(venue_id)

  if venue_query:
    venue = Venue.info(venue_query)
    form.name.data = venue_query.name
    form.city.data = venue_query.city
    form.state.data = venue_query.state
    form.address.data = venue_query.address
    form.phone.data = venue_query.phone
    form.genres.data = venue_query.genres
    form.seeking_talent.data = venue_query.seeking_talent
    form.seeking_description.data = venue_query.seeking_description
    form.facebook_link.data = venue_query.facebook_link
    form.website_link.data = venue_query.website
    form.image_link.data = venue_query.image_link
  # TODO: opulate form with values from venue with ID <venue_id>
    return render_template('forms/edit_venue.html', form=form, venue=venue)
  return render_template('errors/404.html')

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitte
  # d, and update existing
 venue_query = Venue.query.get(venue_id)
 data = request.form
 try:
    if venue_query:
      seeking_talent = False
      if 'seeking_talent' in request.form:
         seeking_talent = (request.form['seeking_talent'] == 'y')
      venue_query.genres=data.getlist("genres")
      venue_query.city=data.get("city")
      venue_query.state=data.get("state")
      venue_query.facebook_link=data.get("facebook_link")
      venue_query.address=data.get("address")
      venue_query.phone=data.get("phone")
      venue_query.website=data.get("website_link")
      venue_query.image_link=data.get("image_link")
      venue_query.seeking_talent = seeking_talent
      venue_query.seeking_description=data.get("seeking_description")
      db.session.commit()
      flash('Venue ' + request.form['name'] + ' was successfully edited!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
 except:
  db.session.rollback()
  flash('An error occurred. Venue ' + data['name'] + ' could not be edited.')
 finally:
  db.session.close()
  # venue record with ID <venue_id> using the new attributes
 return redirect(url_for('show_venue', venue_id=venue_id))


#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  data = request.form
  try:
    seeking_venue = False
    if 'seeking_venue' in request.form:
      seeking_venue = (request.form['seeking_venue'] == 'y')
    new_artist = Artist(
      genres=data.getlist("genres"),
      name=data.get("name"),
      city=data.get("city"),
      state=data.get("state"),
      facebook_link=data.get("facebook_link"),
      phone=data.get("phone"),
      website=data.get("website_link"),
      image_link=data.get("image_link"),
      seeking_venue=seeking_venue,
      seeking_description=data.get("seeking_description")
    )
    db.session.add(new_artist)
    db.session.commit()
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion

  # on successful db insert, flash success
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
  except:
    db.session.rollback()
    flash('An error occurred. Artist ' + data['name'] + ' could not be listed.')
  # TODO: on unsuccessful db insert, flash an error instead.
  finally:
    db.session.close()
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  return render_template('pages/home.html')


#  Delete Artist
#  ----------------------------------------------------------------
@app.route('/artists/<artist_id>', methods=['DELETE'])
def delete_artist(artist_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
 try:
  artist_query = Artist.query.get(artist_id)
  # clicking that button delete it from the db then redirect the user to the homepage

  db.session.delete(artist_query)
  db.session.commit()

  flash('Venue ' + artist_query.name + ' was successfully deleted!')
 except:
  db.session.rollback()
  flash('An error occurred. Venue ' + artist_query.name + ' could not be deleted.')
 finally:
  db.session.close()
 return jsonify()
#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.

  show_query = Show.query.all()
  data = list(map(Show.info, show_query))
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  data = request.form
  try:
    new_show = Show(
      venue_id=data.get("venue_id"),
      artist_id=data.get("artist_id"),
      start_time=data.get("start_time")
    )

    db.session.add(new_show)
    db.session.commit()
  # on successful db insert, flash success
    flash('Show was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  except:
    flash('An error occurred. Show could not be listed.')
    db.session.rollback()
  finally:
    db.session.close()
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
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
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
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
