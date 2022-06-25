#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from jinja2.utils import markupsafe
from markupsafe import Markup
from flask import Flask, render_template, request, Response, flash, redirect, url_for,abort, jsonify
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
import models
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
# (DONE): connect to a local postgresql database
app.config.from_object('config')
db = SQLAlchemy(app)
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
  now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
  city_state = engine.execute('SELECT city,state FROM "Venue"').fetchall()
  for city, state in set(city_state) :
    data1 = {}
    data1["city"] = city
    data1["state"] = state 
    result= engine.execute(f"""SELECT id,name FROM "Venue" WHERE city='{city}' and state='{state}' """).fetchall()
    _ = []
    for row in result:
      data12 = {}
      data12["id"] = row[0]
      data12["name"] = row[1]
      data12["num_upcoming_shows"] = engine.execute(f"""SELECT COUNT(*) FROM "Shows" AS S WHERE S.venue_id = {row[0]} and S.start_time > '{now}' """).fetchall()[0][0]
      _.append(data12)
    data1["venues"] = _ 
    data.append(data1)
  # sample_data=[{
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "venues": [{
  #     "id": 1,
  #     "name": "The Musical Hop",
  #     "num_upcoming_shows": 0,
  #   }, {
  #     "id": 3,
  #     "name": "Park Square Live Music & Coffee",
  #     "num_upcoming_shows": 1,
  #   }]
  # }, {
  #   "city": "New York",
  #   "state": "NY",
  #   "venues": [{
  #     "id": 2,
  #     "name": "The Dueling Pianos Bar",
  #     "num_upcoming_shows": 0,
  #   }]
  # }]
  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST',"GET"])
def search_venues():
  # DONE: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  search_term=request.form.get('search_term', '')
  data = []  
  response= {}
  result = engine.execute(f"""SELECT id,name FROM "Venue" WHERE LOWER(name) LIKE '%%{search_term}%%' """).fetchall()
  now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
  for row in result:
    data1 = {}    
    data1["id"] = row[0]
    data1["name"] = row[1]
    data1["num_upcoming_shows"] = engine.execute(f"""SELECT COUNT(*) FROM "Shows" AS S JOIN "Venue" AS V ON S.venue_id = V.id WHERE LOWER(V.name) LIKE '%%{search_term}%%'  and S.start_time > '{now}' """).fetchall()[0][0]
    data.append(data1)
  response["count"] = len(result)
  response["data"] = data
  response1={
    "count": 1,
    "data": [{
      "id": 2,
      "name": "The Dueling Pianos Bar",
      "num_upcoming_shows": 0,
    }]
  }
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
    data1["website"] = row.website_link
    data1["facebook_link"] = row.facebook_link 
    data1["seeking_talent"] = row.seeking_talent
    data1["seeking_description"] = row.seeking_description
    query = engine.execute(f""" SELECT S.artist_id, A.name, A.image_link, S.start_time FROM "Shows" AS S JOIN "Venue" AS V ON S.venue_id = V.id JOIN "Artist" AS A on S.artist_id = A.id  WHERE S.start_time < '{now}' """).fetchall()
    past_shows_result = []
    for row in set(query):
      show_dict = {}
      show_dict["artist_id"] = row[0]
      show_dict["artist_name"] = row[1]
      show_dict["artist_image_link"] = row[2]
      show_dict["start_time"] = row[3].strftime("%Y-%m-%dT%H:%M:%S.%fZ")    
      past_shows_result.append(show_dict)
    data1["past_shows"] = past_shows_result
    query = engine.execute(f"""SELECT S.artist_id, A.name, A.image_link, S.start_time FROM "Shows" AS S JOIN "Venue" AS V ON S.venue_id = V.id JOIN "Artist" AS A on S.artist_id = A.id  WHERE S.start_time > '{now}' """).fetchall()
    upcoming_shows_result = []
    for row in set(query):
      show_dict = {}
      show_dict["artist_id"] = row[0]
      show_dict["artist_name"] = row[1]
      show_dict["artist_image_link"] = row[2]
      show_dict["start_time"] = row[3].strftime("%Y-%m-%dT%H:%M:%S.%fZ")    
      upcoming_shows_result.append(show_dict)
    data1["upcoming_shows"] = upcoming_shows_result
    data1["past_shows_count"] = len(data1["past_shows"])
    data1["upcoming_shows_count"] = len(data1["upcoming_shows"])

  # sample_data1={
  #   "id": 1,
  #   "name": "The Musical Hop",
  #   "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
  #   "address": "1015 Folsom Street",
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "phone": "123-123-1234",
  #   "website": "https://www.themusicalhop.com",
  #   "facebook_link": "https://www.facebook.com/TheMusicalHop",
  #   "seeking_talent": True,
  #   "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
  #   "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
  #   "past_shows": [{
  #     "artist_id": 4,
  #     "artist_name": "Guns N Petals",
  #     "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
  #     "start_time": "2019-05-21T21:30:00.000Z"
  #   }],
  #   "upcoming_shows": [],
  #   "past_shows_count": 1,
  #   "upcoming_shows_count": 0,
  # }
  # sample_data2={
  #   "id": 2,
  #   "name": "The Dueling Pianos Bar",
  #   "genres": ["Classical", "R&B", "Hip-Hop"],
  #   "address": "335 Delancey Street",
  #   "city": "New York",
  #   "state": "NY",
  #   "phone": "914-003-1132",
  #   "website": "https://www.theduelingpianos.com",
  #   "facebook_link": "https://www.facebook.com/theduelingpianos",
  #   "seeking_talent": False,
  #   "image_link": "https://images.unsplash.com/photo-1497032205916-ac775f0649ae?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=750&q=80",
  #   "past_shows": [],
  #   "upcoming_shows": [],
  #   "past_shows_count": 0,
  #   "upcoming_shows_count": 0,
  # }

  data = list(filter(lambda d: d['id'] == venue_id, [data1]))[0]
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
  data1 = request.form
  try:
      venue = Venue()
      keylist=[]
      for key in data1:
        if key == "genres":
          setattr(venue, key, data1.getlist("genres"))
        elif key == "seeking_talent":
          if  data1[key] == 'y':
            setattr(venue, key, True)
          else :
            setattr(venue, key, False)            
        else :
          setattr(venue, key, data1[key])
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
      flash(f'{venue_id} deleted !')
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
      flash(f'{artist_id} deleted !')
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
  result= engine.execute(f"""SELECT id,name FROM "Artist" """).fetchall()
  _ = []
  for row in result:
    data12 = {}
    data12["id"] = row[0]
    data12["name"] = row[1]
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
  result = engine.execute(f"""SELECT id,name FROM "Artist" WHERE LOWER(name) LIKE '%%{search_term}%%' """).fetchall()
  now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')   
  for row in result:
    data1 = {}
    data1["id"] = row[0]
    data1["name"] = row[1]
    data1["num_upcoming_shows"] = engine.execute(f"""SELECT COUNT(*) FROM "Shows" AS S WHERE S.artist_id = {row[0]} and S.start_time > '{now}' """).fetchall()[0][0]
    data.append(data1)
  response["count"] = len(result)
  response["data"] = data
  response1={
    "count": 1,
    "data": [{
      "id": 4,
      "name": "Guns N Petals",
      "num_upcoming_shows": 0,
    }]
  }
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
  query= engine.execute(f""" SELECT S.venue_id, V.name, V.image_link, S.start_time FROM "Shows" AS S JOIN "Venue" AS V ON S.venue_id = V.id JOIN "Artist" AS A on S.artist_id = A.id  WHERE S.start_time < '{now}' """).fetchall()
  past_shows_result = []
  for row in set(query):
    show_dict = {}
    show_dict["venue_id"] = row[0]
    show_dict["venue_name"] = row[1]
    show_dict["venue_image_link"] = row[2]
    show_dict["start_time"] = row[3].strftime("%Y-%m-%dT%H:%M:%S.%fZ")    
    past_shows_result.append(show_dict)
  data1["past_shows"] = past_shows_result
  query= engine.execute(f""" SELECT S.venue_id, V.name, V.image_link, S.start_time FROM "Shows" AS S JOIN "Venue" AS V ON S.venue_id = V.id JOIN "Artist" AS A on S.artist_id = A.id  WHERE S.start_time > '{now}' """).fetchall()
  upcoming_shows_result = []
  for row in set(query):
    show_dict = {}
    show_dict["venue_id"] = row[0]
    show_dict["venue_name"] = row[1]
    show_dict["venue_image_link"] = row[2]
    show_dict["start_time"] = row[3].strftime("%Y-%m-%dT%H:%M:%S.%fZ")    
    upcoming_shows_result.append(show_dict)
  data1["upcoming_shows"] = upcoming_shows_result
  data1["past_shows_count"] = len(data1["past_shows"])
  data1["upcoming_shows_count"] = len(data1["upcoming_shows"])
  # sample_data={
  #   "id": 4,
  #   "name": "Guns N Petals",
  #   "genres": ["Rock n Roll"],
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "phone": "326-123-5000",
  #   "website": "https://www.gunsnpetalsband.com",
  #   "facebook_link": "https://www.facebook.com/GunsNPetals",
  #   "seeking_venue": True,
  #   "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
  #   "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
  #   "past_shows": [{
  #     "venue_id": 1,
  #     "venue_name": "The Musical Hop",
  #     "venue_image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
  #     "start_time": "2019-05-21T21:30:00.000Z"
  #   }],
  #   "upcoming_shows": [],
  #   "past_shows_count": 1,
  #   "upcoming_shows_count": 0,
  # }
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
  data1 = request.form
  try:
      artist = Artist.query.get(artist_id)
      keylist=[]
      setattr(artist, "seeking_venue", False)        
      for key in data1: 
        if key == "genres":
          setattr(artist, key, data1.getlist("genres"))          
        elif key == "seeking_venue":
          if  data1[key] == 'y':
            setattr(artist, key, True)
          else :
            setattr(artist, key, False)            
        else :
          setattr(artist, key, data1[key])
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
  form = VenueForm()
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
      "website": row.website_link,
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
  data1 = request.form
  try:
      venue = Venue.query.get(venue_id)
      keylist=[]
      setattr(venue, "seeking_talent", False)        
      for key in data1:
        if key == "genres":
          setattr(venue, key, data1.getlist("genres"))
        elif key == "seeking_talent":
          if  data1[key] == 'y':
            setattr(venue, key, True)
          else :
            setattr(venue, key, False)            
        else :
          setattr(venue, key, data1[key])
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
  form = ArtistForm()
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
  data1 = request.form
  try:
      artist  = Artist()
      keylist=[]
      for key in data1:
        if key == "genres":
          setattr(artist, key, data1.getlist(key))
        elif key == "seeking_venue":
          if  data1[key] == 'y':
            setattr(artist, key, True)
          else :
            setattr(artist, key, False)            
        else :
          setattr(artist, key, data1[key])
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
  result= engine.execute(f"""SELECT S.venue_id, V.name, S.artist_id, A.name, A.image_link, S.start_time FROM "Shows" AS S JOIN "Venue" AS V ON S.venue_id = V.id JOIN "Artist" AS A on S.artist_id = A.id   """).fetchall()
  _ = []
  for row in result:
    data12 = {}
    data12["venue_id"] = row[0]
    data12["venue_name"] = row[1]
    data12["artist_id"] = row[2]
    data12["artist_name"] = row[3]
    data12["artist_image_link"] = row[4]
    data12["start_time"] = row[5].strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    _.append(data12)
  data = _     
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
  data1 = request.form
  try:
    engine.execute(f"""INSERT INTO "Shows"(artist_id, venue_id,start_time) VALUES ({data1["artist_id"]},{data1["venue_id"]},'{data1["start_time"]}') """)
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
