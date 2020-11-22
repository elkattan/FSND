#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

from datetime import datetime
import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from sqlalchemy import func, between
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import logging
from logging import Formatter, FileHandler, log
from flask_wtf import FlaskForm
from sqlalchemy.sql.selectable import subquery
from forms import VenueForm, ArtistForm, ShowForm

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#


class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    shows = db.relationship("Show", backref="venue", cascade="all,delete")

    """
    {
        "city": "San Francisco",
        "state": "CA",
        "venues": [{
            "id": 1,
            "name": "The Musical Hop",
            "num_upcoming_shows": 0,
        }, {
            "id": 3,
            "name": "Park Square Live Music & Coffee",
            "num_upcoming_shows": 1,
        }]
    }
    """


class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    website = db.Column(db.String(120))
    facebook_link = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(500))
    shows = db.relationship("Show", backref="artist", cascade="delete,all")

    # Step 2: implement any missing fields, as a database migration using Flask-Migrate

    """
    {
        "id": 1,
        "name": "The Musical Hop",
        "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
        "address": "1015 Folsom Street",
        "city": "San Francisco",
        "state": "CA",
        "phone": "123-123-1234",
        "website": "https://www.themusicalhop.com",
        "facebook_link": "https://www.facebook.com/TheMusicalHop",
        "seeking_talent": True,
        "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
        "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
        "past_shows": [{
            "artist_id": 4,
            "artist_name": "Guns N Petals",
            "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
            "start_time": "2019-05-21T21:30:00.000Z"
        }],
        "upcoming_shows": [],
        "past_shows_count": 1,
        "upcoming_shows_count": 0,
    }
    """


# Step 1: Implement Show and Artist models,
# and complete all model relationships and properties,
# as a database migration.
# (Making it easier to figuer out relations and properties with other models)

class Show(db.Model):
    __tablename__ = 'Show'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'))
    venue_name = db.Column(db.String(120))
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id', ))
    artist_name = db.Column(db.String(120))
    artist_image_link = db.Column(db.String)
    start_time = db.Column(db.DateTime)

    """
    {
        "venue_id": 1,
        "venue_name": "The Musical Hop",
        "artist_id": 4,
        "artist_name": "Guns N Petals",
        "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
        "start_time": "2019-05-21T21:30:00.000Z"
    }
    """
#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#


def format_datetime(value, format='medium'):
    value = value if value is str else value.isoformat(" ")
    date = dateutil.parser.parse(value)
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format)


app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#


@app.route('/')
def index():
    recent_venues = Venue.query.limit(10).all()
    recent_artists = Artist.query.limit(10).all()
    return render_template('pages/home.html', recent_venues=recent_venues, recent_artists=recent_artists)


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
    data = []
    # Could not figuer out more effecient way since
    # SQLAlchemy does not support nested queries (venue list inside grouped Venues by city)

    # Grapping upcoming shows as subquery
    show_query = Show.query.with_entities(Show.id).filter(
        Show.start_time >= datetime.now()).subquery()
    # Grabbing all venues with aggregated `num_upcoming_shows` field
    venue_query = Venue.query.outerjoin(Venue.shows).with_entities(
        Venue.id.label("id"), Venue.name.label("name"), func.count(Show.id.in_(show_query)).label("num_upcoming_shows")).group_by(Venue.id)
    # Grabbing venues grouped by City and state
    venues = Venue.query.with_entities(
        Venue.city,
        Venue.state,
    ).group_by(Venue.city, Venue.state).all()
    # Mapping venues to their respective city and state
    # `venue_query` was not executed earlier to avoid loading big amount of data in the memory
    # the trade-off is making requests to the database for each venue
    # another solution would be sacrificing memory, loading all venues from `venue_query` and filtring manually
    for venue in venues:
        data.append({
            "city": venue.city,
            "state": venue.state,
            "venues": venue_query.filter(
                Venue.city == venue.city, Venue.state == venue.state).all()
        })
    return render_template('pages/venues.html', areas=data)


@app.route('/venues/search', methods=['POST'])
def search_venues():
    # implement search on artists with partial string search
    results = []
    search_term = request.form.get("search_term", None)
    if search_term:
        results = Venue.query.filter(
            Venue.name.ilike(f"%{search_term}%")).all()
    response = {
        "count": len(results),
        "data": results
    }
    return render_template('pages/search_venues.html', results=response, search_term=search_term)


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    # shows the venue page with the given venue_id
    data = Venue.query.get_or_404(venue_id)
    shows = Show.query.filter(Show.venue_id == venue_id).all()
    upcoming_shows = list(
        filter(lambda show: show.start_time >= datetime.now(), shows))
    past_shows = list(
        filter(lambda show: show.start_time < datetime.now(), shows))
    data.upcoming_shows = upcoming_shows
    data.past_shows = past_shows
    data.upcoming_shows_count = len(upcoming_shows)
    data.past_shows_count = len(past_shows)
    return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------


@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    form = None
    try:
        venue = Venue()
        form = VenueForm()
        # make sure form is valid
        # if not, raise an error
        assert(form.validate_on_submit())
        form.populate_obj(venue)
        db.session.add(venue)
        db.session.commit()
        # on successful db insert, flash success
        flash('Venue ' + request.form['name'] + ' was successfully listed!')
    except Exception as err:
        print(err, form.errors)
        # In case of Database error or form validation error
        # alert the user and return the same form data
        flash('An error occurred. Venue ' +
              request.form['name'] + ' could not be listed.', 'error')
        return render_template('forms/new_venue.html', form=form)
    return render_template('pages/home.html')


@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    # Step 3: Complete this endpoint for taking a venue_id, and using
    # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
    try:
        venue = Venue.query.get_or_404(venue_id)
        db.session.delete(venue)
        db.session.commit()
        flash('Venue ID ' + venue_id + ' deleted successfully.', 'info')
        return Response(status=202)
    except:
        flash('An error occurred. Venue ID ' +
              venue_id + ' could not be deleted.', 'error')
        # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
        # clicking that button delete it from the db then redirect the user to the homepage
    return Response(status=400)

#  Artists
#  ----------------------------------------------------------------


@app.route('/artists')
def artists():
    # Step 3: replace with real data returned from querying the database
    data = Artist.query.with_entities(Artist.id, Artist.name).all()
    return render_template('pages/artists.html', artists=data)


@app.route('/artists/search', methods=['POST'])
def search_artists():
    # implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
    # search for "band" should return "The Wild Sax Band".
    results = []
    search_term = request.form.get('search_term', None)
    if search_term:
        results = Artist.query.join(Artist.shows).with_entities(
            Artist.id,
            Artist.name,
            func.count(Show.id).label("num_upcoming_shows")
        ).filter(Artist.name.ilike(search_term))\
            .group_by(Artist.id, Artist.name).all()
    response = {
        "count": len(results),
        "data": results
    }
    return render_template('pages/search_artists.html', results=response, search_term=search_term)


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    # shows the Artist page with the given artist_id
    # Step 5: replace with real Artist data from the Artists table, using artist_id
    data = Artist.query.get_or_404(artist_id)
    print(type(data.genres))
    data.genres = data.genres.split(",")
    shows = Show.query.filter(Show.artist_id == artist_id).all()
    upcoming_shows = list(
        filter(lambda show: show.start_time >= datetime.now(), shows))
    past_shows = list(
        filter(lambda show: show.start_time < datetime.now(), shows))
    data.upcoming_shows = upcoming_shows
    data.past_shows = past_shows
    data.upcoming_shows_count = len(upcoming_shows)
    data.past_shows_count = len(past_shows)
    return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------


@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    form = ArtistForm()
    artist = Artist.query.get_or_404(artist_id)
    return render_template('forms/edit_artist.html', form=form, artist=artist)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    artist = Artist.query.get_or_404(artist_id)

    form = ArtistForm(formdata=request.form, obj=artist)
    if form.validate_on_submit():
        form.populate_obj(artist)
        db.session.commit()

    return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    form = VenueForm()
    venue = Venue.query.get_or_404(venue_id)
    return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    venue = Venue.query.get_or_404(venue_id)

    form = VenueForm(formdata=request.form, obj=venue)
    if form.validate_on_submit():
        form.populate_obj(venue)
        db.session.commit()
    return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------


@app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)


@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    form = None
    try:
        artist = Artist()
        form = ArtistForm()
        # make sure form is valid
        # if not, raise an error
        assert(form.validate_on_submit())
        form.populate_obj(artist)
        artist.genres = ",".join(request.form.getlist("genres"))
        db.session.add(artist)
        db.session.commit()
        # on successful db insert, flash success
        flash('Artist ' + request.form['name'] + ' was successfully listed!')
    except Exception as err:
        print(err, form.errors)
        # In case of Database error or form validation error
        # alert the user and return the same form data
        flash('An error occurred. Artist ' +
              request.form['name'] + ' could not be listed.', 'error')
        return render_template('forms/new_artist.html', form=form)
    return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    # displays list of shows at /shows
    data = Show.query.all()
    return render_template('pages/shows.html', shows=data)


@app.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    form = None
    try:
        show = Show()
        form = ShowForm()
        # make sure form is valid
        # if not, raise an error
        assert(form.validate_on_submit())
        form.populate_obj(show)
        db.session.add(show)
        db.session.commit()
        # on successful db insert, flash success
        flash('Show was successfully listed!')
    except:
        # In case of Database error or form validation error
        # alert the user and return the same form data
        flash('An error occurred. Show could not be listed.', 'error')
        return render_template('forms/new_show.html', form=form)
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
