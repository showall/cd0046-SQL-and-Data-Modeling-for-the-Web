#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from jinja2.utils import markupsafe
from markupsafe import Markup
from flask import( 
  Flask, 
  render_template, 
  request, 
  Response, 
  flash, 
  redirect, 
  url_for,abort, 
  jsonify
)
from flask_migrate import Migrate
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
import config
import sys
from sqlalchemy.sql import text
import datetime
from models import Venue, db, Artist, Show
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
# (DONE): connect to a local postgresql database
app.config.from_object('config')
db.init_app(app)
migrate = Migrate(app, db)
engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])

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
  data = []
  venue = Venue.query.all()
  city_states = Venue.query.distinct(Venue.city, Venue.state).all()
  for city_state in city_states :
    data1 = {}
    data1["city"] = city_state.city
    data1["state"] = city_state.state
    result = db.session.query(Venue).filter(Venue.city == city_state.city).filter(Venue.city == city_state.city).all()
    _ = []
    for row in result:
      data12 = {}
      data12["id"] = row.id
      data12["name"] = row.name
      _.append(data12)
    data1["venues"] = _
    data.append(data1)
  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST',"GET"])
def search_venues():
  # DONE: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  search_term=request.form.get('search_term', '')
  data = []
  response= {}
  result = Venue.query.filter(Venue.name.ilike("%" + search_term + "%")).all()
  now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
  for row in result:
    data1 = {}
    data1["id"] = row.id
    data1["name"] = row.name
    data1["num_upcoming_shows"] = db.session.query(Venue,Show).filter(Venue.name.ilike("%" + search_term + "%")).filter(Show.start_time>now).all()
    data.append(data1)
  response["count"] = len(result)
  response["data"] = data
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  result  =  db.session.query(Venue).filter(Venue.id == venue_id).all()
  data1 = {} 
  now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')    
  for row in result:
    data1["id"] = row.id
    data1["name"] = row.name
    data1["genres"] = row.genres
    data1["city"] = row.city
    data1["state"] = row.state
    data1["address"] = row.address
    data1["phone"] = row.phone
    data1["image_link"] = row.image_link  
    data1["website"] = row.website
    data1["facebook_link"] = row.facebook_link 
    data1["seeking_talent"] = row.seeking_talent
    data1["seeking_description"] = row.seeking_description
    query = db.session.query(Artist, Show, Venue).join(Show, Venue.id == Show.venue_id).join(Artist).filter(Venue.id == venue_id).all()
    for row in query:
      shows_result = []       
      show_dict = {}
      show_dict["artist_id"] = row[0].id
      show_dict["artist_name"] = row[0].name
      show_dict["artist_image_link"] = row[0].image_link
      show_dict["start_time"] =  row[1].start_time.strftime("%Y-%m-%dT%H:%M:%S.%fZ")    
      shows_result.append(show_dict)
      if row[1].start_time <= datetime.datetime.now(): 
        data1["past_shows"] = shows_result
      else:
        data1["upcoming_shows"] = shows_result
    try:
      data1["past_shows_count"] = len(data1["past_shows"])
    except:
      data1["past_shows_count"] = 0
    try:
      data1["upcoming_shows_count"] = len(data1["upcoming_shows"])
    except:
      data1["upcoming_shows_count"] = 0

  data1 = list(filter(lambda d: d['id'] == venue_id, [data1]))[0]
  return render_template('pages/show_venue.html', venue=data1)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
#insert form data as a new Venue record in the db
# modify data to be the data object returned from db insertion
# on successful db insert, flash success
# on unsuccessful db insert, flash an error instead
# e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')

def create_venue_submission():
  error = False
  body = {}
  data1 = VenueForm(request.form)
  try:
    venue = Venue()
    for key in data1:
      if key == request.form:
          setattr(venue, key, request.form.getlist("genres"))
      elif key == "seeking_talent":
        if  request.form[key] == 'y':
          venue.seeking_talent = True
        else :
          venue.seeking_talent = False        
      else :
          setattr(venue, key, request.form[key])
    db.session.add(venue)
    db.session.commit()
    flash('Venue ' + request.form['name'] + ' was successfully listed!')  
  except:
    db.session.rollback()
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
    error = True
    print(sys.exc_info)
  finally:
    db.session.close()
  if error:
    abort(500)
  else:
    #    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    return render_template('pages/home.html')


@app.route('/venues/<venue_id>', methods=['DELETE','POST'])
#  Providing an endpoint for SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
def delete_venue(venue_id):
  error = False
  try:
    result = db.session.query(Venue).filter(Venue.id == venue_id).all()
    for row in result:
      db.session.delete(row)
      db.session.commit()
      flash(f'Venue Id:{venue_id} deleted !')
  except:
    db.session.rollback()
    error = True
  finally:
    db.session.close()
  if error:
    abort(500)
  else:
    return redirect(url_for('index'))

@app.route('/artists/<artist_id>', methods=['DELETE','POST'])
#  Providing an endpoint for SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
def delete_artist(artist_id):
  error = False
  try:
    result = db.session.query(Artist).filter(Artist.id == artist_id).all()
    for row in result:
      db.session.delete(row)
      db.session.commit()
      flash(f'Artist Id:{artist_id} deleted !')
  except:
    db.session.rollback()
    error = True
  finally:
    db.session.close()
  if error:
    abort(500)
  else:
    return redirect(url_for('index'))

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  result= Artist.query.all()
  _ = []
  for row in result:
    data12 = {}
    data12["id"] = row.id
    data12["name"] = row.name
    _.append(data12)
  data = _ 
  # sample_data =[{
  #   "id": 4,
  #   "name": "Guns N Petals",
  # }, {
  #   "id": 5,
  #   "name": "Matt Quevedo",
  # }]
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST',"GET"])
def search_artists():
  # implement search on artists with partial string search. Ensure it is case-insensitive.
  # search for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  search_term=request.form.get('search_term', '')
  data = []  
  response= {}
  result = Artist.query.filter(Artist.name.ilike("%" + search_term + "%")).all()
  now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')   
  for row in result:
    data1 = {}
    data1["id"] = row.id
    data1["name"] = row.name
    data1["num_upcoming_shows"] = db.session.query(Artist,Show).filter(Artist.name.ilike("%" + search_term + "%")).filter(Show.start_time>now).filter(Show.artist_id == row.id).all()
    data.append(data1)
  response["count"] = len(result)
  response["data"] = data
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  result  =  db.session.query(Artist).filter(Artist.id == artist_id).all()
  data1 = {} 
  now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
  for row in result:
    data1["id"] = row.id
    data1["name"] = row.name
    data1["genres"] = row.genres
    data1["city"] = row.city
    data1["state"] = row.state
    data1["address"] = row.address
    data1["phone"] = row.phone
    data1["image_link"] = row.image_link  
    data1["website"] = row.website
    data1["facebook_link"] = row.facebook_link 
    data1["seeking_venue"] = row.seeking_venue
    data1["seeking_description"] = row.seeking_description
    query=db.session.query(Venue, Show, Artist).join(Show, Venue.id == Show.venue_id).join(Artist).filter(Artist.id == artist_id).all()
    for row in query:
      shows_result = []       
      show_dict = {}
      print (row[0].id)
      show_dict["venue_id"] = row[0].id
      show_dict["venue_name"] = row[0].name
      show_dict["venue_image_link"] = row[0].image_link
      show_dict["start_time"] = row[1].start_time.strftime("%Y-%m-%dT%H:%M:%S.%fZ")    
      shows_result.append(show_dict)
      if row[1].start_time <= datetime.datetime.now(): 
        data1["past_shows"] = shows_result
      else:
        data1["upcoming_shows"] = shows_result
    try:
      data1["past_shows_count"] = len(data1["past_shows"])
    except:
      data1["past_shows_count"] = 0
    try:
      data1["upcoming_shows_count"] = len(data1["upcoming_shows"])
    except:
      data1["upcoming_shows_count"] = 0
  data = list(filter(lambda d: d['id'] == artist_id, [data1]))[0]
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
#populate form with values from venue with ID <venue_id>
def edit_artist(artist_id):
  form = ArtistForm()
  result  =  db.session.query(Artist).filter(Artist.id == artist_id).all()
  for row in result:
    artist={
      "id": row.id,
      "name": row.name,
      "genres": row.genres,
      "address": row.address,
      "city": row.city,
      "state": row.state,
      "phone": row.phone,
      "website": row.website,
      "facebook_link": row.facebook_link,
      "seeking_venue": row.seeking_venue,
      "seeking_description": row.seeking_description,
      "image_link": row.image_link 
    }
    form.state.default = row.state
    form.genres.data = row.genres
    form.genres.default = row.genres
    form.process()
  # TODO: 
  return render_template('forms/edit_artist.html', form=form, artist=artist)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
  # take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
def edit_artist_submission(artist_id):
  error = False
  ArtistForm(request.form)
  try:
      artist = Artist.query.get(artist_id)
      artist.seeking_venue = False
      for key in request.form:
        if key == "genres":
          setattr(artist, key, request.form.getlist("genres"))
        elif key == "seeking_venue":
          if  request.form[key] == 'y':
            artist.seeking_venue = True
          else :
            artist.seeking_venue = False         
        else :
          setattr(artist, key, request.form[key])
      db.session.add(artist)
      db.session.commit()
      flash('Artist ' + request.form['name'] + ' was successfully edited!')  
  except:
    db.session.rollback()
    flash('An error occurred. Artist ' + request.form['name'] + ' could not be edited.')
    error = True
    print(sys.exc_info)
  finally:
    db.session.close()
  return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm(request.form)
  result  =  db.session.query(Venue).filter(Venue.id == venue_id).all()
  data1 = {} 
  for row in result:
    venue={
      "id": row.id,
      "name": row.name,
      "genres": row.genres,
      "address": row.address,
      "city": row.city,
      "state": row.state,
      "phone": row.phone,
      "website": row.website,
      "facebook_link": row.facebook_link,
      "seeking_talent": row.seeking_talent,
      "seeking_description": row.seeking_description,
      "image_link": row.image_link 
    }
    form.state.default = row.state
    form.genres.data = row.genres
    form.genres.default = row.genres
    form.process()
    #print(form.genres.default)
  # TODO: populate form with values from venue with ID <venue_id> -DONE
  #print(venue)
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
# take values from the form submitted, and update existing
# artist record with ID <artist_id> using the new attributes
def edit_venue_submission(venue_id):
  data1 = VenueForm(request.form)
  try:
      venue = Venue.query.get(venue_id)
      venue.seeking_talent = False     
      for key in request.form:
        if key == "genres":
          setattr(venue, key, request.form.getlist("genres"))
        elif key == "seeking_talent":
          if  request.form[key] == 'y':
            venue.seeking_talent = True
          else :
            venue.seeking_talent = False         
        else :
          setattr(venue, key, request.form[key])
      db.session.add(venue)
      db.session.commit()
      flash('Venue ' + request.form['name'] + ' was successfully edited!')  
  except:
    db.session.rollback()
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be edited.')
    error = True
    print(sys.exc_info)
  finally:
    db.session.close()
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm(request.form)
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
# called upon submitting the new artist listing form
# insert form data as a new Venue record in the db, instead
# modify data to be the data object returned from db insertion
# on successful db insert, flash success
# flash('Artist ' + request.form['name'] + ' was successfully listed!')
# on unsuccessful db insert, flash an error instead.
# e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
def create_artist_submission():
  error = False
  ArtistForm(request.form)
  try:
      artist  = Artist()
      for key in request.form:
        if key == "genres":
          setattr(artist, key, request.form.getlist("genres"))
        elif key == "seeking_venue":
          if  request.form[key] == 'y':
            artist.seeking_venue = True
          else :
            artist.seeking_venue = False         
        else :
            setattr(artist, key, request.form[key])
      db.session.add(artist)
      db.session.commit()
      flash('Artist ' + request.form['name'] + ' was successfully listed!')  
  except:
    db.session.rollback()
    flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
    error = True
    print(sys.exc_info)
  finally:
    db.session.close()
  if error:
       abort(500)
  else:
      #    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  result= db.session.query(Venue, Show, Artist).join(Show, Venue.id == Show.venue_id).join(Artist).all()
  _ = []
  for row in result:
    data12 = {}
    data12["venue_id"] = row[1].venue_id
    data12["venue_name"] = row[0].name
    data12["artist_id"] = row[1].artist_id
    data12["artist_name"] = row[2].name
    data12["artist_image_link"] = row[2].image_link
    data12["start_time"] = row[1].start_time.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    _.append(data12)
  data = _ 
  print(data)    
  sample_data=[{
    "venue_id": 1,
    "venue_name": "The Musical Hop",
    "artist_id": 4,
    "artist_name": "Guns N Petals",
    "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
    "start_time": "2019-05-21T21:30:00.000Z"
  }, {
    "venue_id": 3,
    "venue_name": "Park Square Live Music & Coffee",
    "artist_id": 5,
    "artist_name": "Matt Quevedo",
    "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
    "start_time": "2019-06-15T23:00:00.000Z"
  }]
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  # called to create new shows in the db, upon submitting new show listing form insert form data as a new Show record in the db
  # on successful db insert, flash success
  # on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  error = False
  ShowForm(request.form)
  try:
    show = Show()
    for key in request.form:
      if key == "artist_id" or key == "venue_id":
        setattr(show,key,int(request.form[key]))
      else : 
        setattr(show, key,datetime.datetime.strptime(request.form[key],'%Y-%m-%d %H:%M:%S'))     
    db.session.add(show)
    db.session.commit()
    flash('Show was successfully listed!') 
  except:
    db.session.rollback()
    flash('An error occurred. Show'  + ' could not be listed.')
    error = True
    print(sys.exc_info)
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
  app.run(host='0.0.0.0', port=port,debug=True)
'''
