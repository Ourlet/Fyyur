#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#
import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from flask_migrate import Migrate
from forms import *
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Connect to a local postgresql database
migrate = Migrate(app, db)
#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

from models import *

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

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
  # replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  
  data_areas = []

  # Get areas
  areas = Venue.query \
        .with_entities(Venue.city, Venue.state) \
        .group_by(Venue.city, Venue.state) \
        .all()
  

  # Iterate over each area

  for area in areas:
    data_venues = []

    # Get Venues by areas

    venues = Venue.query \
      .filter_by(state=area.state) \
      .filter_by(city=area.city) \
      .all()

    # Iterate over each venue
    for venue in venues:
      upcoming_shows = db.session \
        .query(Show) \
        .filter(Show.venue_id == venue.id) \
        .filter(Show.date > datetime.now()) \
        .all()

      # Map venues
      data_venues.append({
        'id': venue.id,
        'name': venue.name,
        'num_upcoming_shows': len(upcoming_shows)
      })

    # Map areas
    data_areas.append({
      'city': area.city,
      'state': area.state,
      'venues': data_venues
    })

  return render_template('pages/venues.html', areas=data_areas);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  #: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  
  # Prepare Search data
  search_term = request.form.get('search_term','')
  search = "%{}%".format(search_term)
  search_result = db.session.query(Venue)\
    .filter(Venue.name.ilike(search))\
    .all()
  
  data = []

  for result in search_result:
      data.append({
        'id': result.id,
        'name': result.name,
        'num_upcoming_shows': len(db.session \
      .query(Show) \
      .filter(Show.venue_id == result.id) \
      .filter(Show.date > datetime.now()) \
      .all())
      })

  response = {
    "count": len(search_result),
    "data": data
  }

  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # replace with real venue data from the venues table, using venue_id
   
  data_venue = Venue.query.get(venue_id)

  upcoming_shows = db.session.query(Show).join(Artist)\
    .filter(Show.venue_id == venue_id)\
    .filter(Show.date > datetime.now())\
    .all()

  if len(upcoming_shows) > 0: 
    data_upcoming_shows = []

    for upcoming_show in upcoming_shows:
   
      data_upcoming_shows.append({
        "artist_id": upcoming_show.artist_id,
        "artist_name": upcoming_show.artist.name,
        "artist_image_link": upcoming_show.artist.image_link,
        "start_time" : str(upcoming_show.date),
      })

    data_venue.upcoming_shows = data_upcoming_shows
    data_venue.upcoming_shows_count = len(data_upcoming_shows)

  past_shows = db.session.query(Show).join(Artist)\
    .filter(Show.venue_id == venue_id)\
    .filter(Show.date < datetime.now())\
    .all()

  if len(past_shows) > 0:
    data_past_shows = []

    for past_show in past_shows:

      data_past_shows.append({
        "artist_id": past_show.artist_id,
        "artist_name": past_show.artist.name,
        "artist_image_link": past_show.artist.image_link,
        "start_time": str(past_show.date),
    })

    data_venue.past_shows = data_past_shows
    data_venue.past_shows_count = len(data_past_shows)

  return render_template('pages/show_venue.html', venue=data_venue)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # insert form data as a new Venue record in the db, instead
  # modify data to be the data object returned from db insertion

  error = False
  try:
      name = request.form['name']
      city = request.form['city']
      state = request.form['state']
      address = request.form['address']
      phone = request.form['phone']
      genres = request.form.getlist('genres')
      facebook_link = request.form['facebook_link']
      image_link = request.form['image_link']
      website = request.form['website_link']
      seeking_talent = True if 'seeking_talent' in request.form else False
      seeking_description = request.form['seeking_description']

      venue = Venue(name=name, city=city, state=state, address=address, phone=phone, genres=genres, facebook_link=facebook_link, image_link=image_link, website=website, seeking_talent=seeking_talent, seeking_description=seeking_description)

      db.session.add(venue)
      db.session.commit()

  except():
      error = True
      db.session.rollback()
      print(sys.exc_info)   

  # on successful db insert, flash success
  finally:
      db.session.close()
      flash('Venue ' + request.form['name'] + ' was successfully listed!')

  # on unsuccessful db insert, flash an error instead.
  if error:
        abort(500)
        flash('An error occurred. Venue ' + data.name + ' could not be listed.')

  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  else:
      return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
    error : False
    try:
        venue = Venue.query.get(venue_id)
        db.session.delete(venue)
        db.commit()
    
    except():
        error = True
        db.session.rollback()
    finally:
        db.session.close()
    if error:
        abort(500)
    else:
      
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
      return jsonify({'success': True})


#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # replace with real data returned from querying the database
  
  data = []

  artists = Artist.query.all()

  for artist in artists:
    data.append({
      "id": artist.id,
      "name": artist.name
    })
  
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".

  search_term = request.form.get('search_term')
  search = '%{}%'.format(search_term)
  search_result = db.session.query(Artist)\
    .filter(Artist.name.ilike(search))\
    .all()

  data = []

  for result in search_result:
    data.append({
    "id": result.id,
    "name": result.name,
    "num_upcoming_shows": len(db.session \
      .query(Show) \
      .filter(Show.artist_id == result.id) \
      .filter(Show.date > datetime.now()) \
      .all())
    })

  response={
    "count": len(search_result),
    "data": data
  }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # replace with real artist data from the artist table, using artist_id

  data_artist = Artist.query.get(artist_id)

  upcoming_shows = db.session.query(Show).join(Venue)\
    .filter(Show.artist_id == artist_id)\
    .filter(Show.date > datetime.now())\
    .all()

  if len(upcoming_shows) > 0:
    data_upcoming_shows = []

    for upcoming_show in upcoming_shows:
 
      data_upcoming_shows.append({
        "venue_id": upcoming_show.venue_id,
        "venue_name": upcoming_show.venue.name,
        "venue_image_link": upcoming_show.venue.image_link,
        "start_time": str(upcoming_show.date)
      })
    
    data_artist.upcoming_shows = data_upcoming_shows
    data_artist.upcoming_shows_count = len(upcoming_shows)

  past_shows = db.session.query(Show).join(Venue)\
    .filter(Show.artist_id == artist_id)\
    .filter(Show.date < datetime.now())\
    .all()

  if len(past_shows) > 0:
    data_past_shows = []

    for past_show in past_shows:

      data_past_shows.append({
        "venue_id": past_show.venue_id,
        "venue_name": past_show.venue.name,
        "venue_image_link": past_show.venue.image_link,
        "start_time": str(past_show.date)
      })

    data_artist.past_shows = data_past_shows
    data_artist.past_shows_count = len(past_shows)
      
  return render_template('pages/show_artist.html', artist=data_artist)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist = Artist.query.get(artist_id)
  if request.method == 'GET':
      form.name.data = artist.name
      form.city.data = artist.city
      form.state.data = artist.state
      form.phone.data = artist.phone
      form.genres.data = artist.genres
      form.facebook_link.data = artist.facebook_link
      form.image_link.data = artist.image_link
      form.website_link.data = artist.website
      form.seeking_venue.data = artist.seeking_venue
      form.seeking_description.data = artist.seeking_description
    
  # populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes

  error = False
  try:
      name = request.form['name']
      city = request.form['city']
      state = request.form['state']
      phone = request.form['phone']
      genres = request.form.getlist('genres')
      facebook_link = request.form['facebook_link']
      image_link = request.form['image_link']
      website = request.form['website_link']
      seeking_venue = True if 'seeking_venue' in request.form else False
      seeking_description = request.form['seeking_description']

      artist = Artist.query.get(artist_id)
      artist.name = name
      artist.city = city
      artist.genres = genres
      artist.state = state
      artist.phone = phone
      artist.image_link = image_link
      artist.facebook_link = facebook_link
      artist.website = website
      artist.seeking_venue = seeking_venue
      artist.seeking_description = seeking_description
    
      db.session.commit()

  except():
      db.rollback()
      error = True
      print(sys.exc_info())
  if error:
      abort(500)
  else:
      return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue = Venue.query.get(venue_id)
  if request.method == 'GET':
      form.name.data = venue.name
      form.genres.data = venue.genres
      form.address.data = venue.address
      form.city.data = venue.city
      form.state.data = venue.state
      form.phone.data = venue.phone
      form.website_link.data = venue.website
      form.facebook_link.data = venue.facebook_link
      form.seeking_talent.data = venue.seeking_talent
      form.seeking_description.data = venue.seeking_description
      form.image_link.data = venue.image_link
  
  # populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes

  error = False
  try:
      name = request.form['name']
      genres = request.form.getlist('genres')
      address = request.form['address']
      city = request.form['city']
      state = request.form['state']
      phone = request.form['phone']
      website = request.form['website_link']
      facebook_link = request.form['facebook_link']
      seeking_talent = True if 'seeking_talent' in request.form else False
      seeking_description = request.form['seeking_description']
      image_link = request.form['image_link']

      venue = Venue.query.get(venue_id)
      venue.name = name
      venue.genres = genres
      venue.city = city
      venue.state = state
      venue.phone = phone
      venue.image_link = image_link
      venue.facebook_link = facebook_link
      venue.website = website
      venue.seeking_talent = seeking_talent
      venue.seeking_description = seeking_description
    
      db.session.commit()

  except():
      db.rollback()
      error = True
      print(sys.exc_info())
  if error:
      abort(500)
  else:
      return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # insert form data as a new Venue record in the db, instead
  # modify data to be the data object returned from db insertion

  error = False
  try: 
      name = request.form['name']
      city = request.form['city']
      state = request.form['state']
      phone = request.form['phone']
      genres = request.form.getlist('genres')
      facebook_link = request.form['facebook_link']
      image_link = request.form['image_link']
      website = request.form['website_link']
      seeking_venue = True if 'seeking_venue' in request.form else False
      seeking_description = request.form['seeking_description']

      artist = Artist(name=name, city=city, state=state, phone=phone, genres=genres, facebook_link=facebook_link, image_link=image_link, website=website, seeking_venue=seeking_venue, seeking_description=seeking_description)

      db.session.add(artist)
      db.session.commit()

  except():
      error = True
      db.session.rollback()
      print(sys.exc_info) 

  # on successful db insert, flash success
  finally:
      db.session.close()
      flash('Artist ' + request.form['name'] + ' was successfully listed!')
  #  on unsuccessful db insert, flash an error instead.

  if error:
      abort(500)
      flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  else:
      return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  #  replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.

  data = []

  shows = Show.query.all()

  for show in shows:
    artist = Artist.query.filter(Artist.id == show.artist_id).first()
    venue = Venue.query.filter(Venue.id == show.venue_id).first()

    data.append({
      "venue_id": show.venue_id,
      "venue_name": venue.name,
      "artist_id": show.artist_id,
      "artist_name": artist.name,
      "artist_image_link": artist.image_link,
      "start_time": str(show.date)
    })

  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  #  insert form data as a new Show record in the db, instead
  
  error = False
  try: 
      artist_id = request.form['artist_id']
      venue_id = request.form['venue_id']
      start_time = request.form['start_time']

      show = Show(artist_id=artist_id, venue_id=venue_id, date=start_time)

      db.session.add(show)
      db.session.commit()

  except():
      error = True
      db.session.rollback()
      print(sys.exc_info)

  # on successful db insert, flash success
  finally:
      db.session.close()
      flash('Show was successfully listed!')

  
  # on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  
  if error:
      abort(500)
      flash('An error occurred. Show could not be listed.')
  
  else:
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
