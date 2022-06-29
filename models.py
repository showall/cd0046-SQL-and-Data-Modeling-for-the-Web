#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#
from flask import (Flask, 
    render_template, 
    request, 
    Response, 
    flash, 
    redirect, 
    url_for,abort,
    jsonify)
from flask_migrate import Migrate
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
import config
import sys

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
app.config.from_object('config')
moment = Moment(app)
db = SQLAlchemy(app)
migrate = Migrate(app, db)

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#
# Done: implement Venue model fields, as a database migration using Flask-Migrate
class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    genres =db.Column(db.ARRAY(db.String), nullable=False)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    website = db.Column(db.String(500))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean)
    seeking_description = db.Column(db.String)
    seeking_description2 = db.Column(db.String)    
    show = db.relationship('Show', backref="Venue",lazy=True, cascade="all, delete")

# Done: implement  Artist models fields, as a database migration using Flask-Migrate
class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)    
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String), nullable=False)
    website = db.Column(db.String(500))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean)
    seeking_description = db.Column(db.String)
    show = db.relationship('Show', backref="Artist",lazy=True, cascade="all, delete")

class Show(db.Model):
    __tablename__ = 'Show'

    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column('artist_id', db.Integer, db.ForeignKey('Artist.id'))
    venue_id = db.Column('venue_id', db.Integer, db.ForeignKey('Venue.id'))
    start_time = db.Column('start_time', db.DateTime, nullable=False)