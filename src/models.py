"""
models.py
Databstore models.
"""

import time
import logging

import webapp2_extras.appengine.auth.models
from google.appengine.ext import ndb
from webapp2_extras import security


class User(webapp2_extras.appengine.auth.models.User):
  """
  Many of the method here have been copied from the webapp2 core
  because dolphin.
  """
  
  def set_password(self, raw_password):
    """Sets the password for the current user

    :param raw_password:
        The raw password which will be hashed and stored
    """
    self.password = security.generate_password_hash(raw_password, length=12)

  @classmethod
  def get_by_auth_token(cls, user_id, token, subject='auth'):
    """Returns a user object based on a user ID and token.

    :param user_id:
        The user_id of the requesting user.
    :param token:
        The token string to be verified.
    :returns:
        A tuple ``(User, timestamp)``, with a user object and
        the token timestamp, or ``(None, None)`` if both were not found.
    """
    token_key = cls.token_model.get_key(user_id, subject, token)
    user_key = ndb.Key(cls, user_id)
    # Use get_multi() to save a RPC call.
    valid_token, user = ndb.get_multi([token_key, user_key])
    if valid_token and user:
        timestamp = int(time.mktime(valid_token.created.timetuple()))
        return user, timestamp

    return None, None

# Parent key for Cinemas and Films
parent_key = ndb.Key('parent', 1)


class LastUpdate(ndb.Model):
    """
    Stores the last 'Date-Updated' value
    of the CineWorld Mega XML File Of Doom.
    """
    
    updated = ndb.StringProperty()
    
    @classmethod
    def get_updated(self):
        l = LastUpdate.get_or_insert('last_update', parent=parent_key)
        return l.updated
    
    @classmethod
    def set_updated(self, u):
        l = LastUpdate.get_or_insert('last_update', parent=parent_key)
        l.updated = u
        l.put()
    
    

class Cinemas(ndb.Model):
    """
    Cineworld cinemas.
    Mimicks the XML attributes of <cinema>.
    """
    
    api_id = ndb.StringProperty()   # id
    name = ndb.StringProperty()
    address = ndb.StringProperty()  # address + postcode + phone
    url = ndb.StringProperty()      # root + url
    
    @classmethod
    def get_by_api_id(self, id):
        """Returns a single result or None."""
        return Cinemas.query(ancestor=parent_key).filter(Cinemas.api_id == id).get()
    
    @classmethod
    def get_film_times_cinema(self, cinema, film):
        """Returns a list of film times for a partiular film."""
        
        return FilmTimes.query(ancestor=cinema.key).filter(FilmTimes.film_key == film.key).fetch()
    
    def get_film_times(self):
        """Returns a list of FilmTime objects."""
        return FilmTimes.query(ancestor=self.key).fetch(1000)
    
    def get_films(self):
        """Returns a list of Films showing at this cinema."""
        filmtimes = FilmTimes.query(ancestor=self.key).fetch(100)
        films = []
        
        for f in filmtimes:
            if f.film_key not in films:
                films.append(f.film_key)
        
        return ndb.get_multi(films)
    
    @classmethod
    def delete_film_times(self):
        """Deletes all the FilmTime objects for this cinema."""
        for t in self.get_film_times():
            t.key.delete
    
    @classmethod
    def get_all_keys(self):
        return Cinemas.query(ancestor=parent_key).fetch(100000, keys_only=True)


class FilmTimes(ndb.Model):
    """
    Film times. A Cinema object is used as
    a parent in the datastore.
    Mimicks the XML attributes of <show>
    """
    
    film_key = ndb.KeyProperty()
    time = ndb.DateTimeProperty()   # Parsed date and time
    ad = ndb.BooleanProperty(default=False)      # audioType="audio described"
    
    @classmethod
    def delete_all(self):
        cinemas = Cinemas.get_all_keys()
        
        for c in cinemas:
            fts = FilmTimes.query(ancestor=c).fetch(keys_only=True)
            ndb.delete_multi(fts)


class Films(ndb.Model):
    """
    Film information.
    Mimicks the XML attributes of <film>
    """
    
    api_id = ndb.StringProperty()   # edi
    title = ndb.StringProperty()
    rating = ndb.StringProperty()
    release = ndb.StringProperty()
    length = ndb.StringProperty()
    director = ndb.StringProperty()
    synopsis = ndb.TextProperty()
    cast = ndb.StringProperty()
    url = ndb.StringProperty()      # cinema.root + url
    poster = ndb.StringProperty()   # cinema.root + poster
    
    @classmethod
    def get_by_api_id(self, id):
        """Returns a single result or None."""
        return Films.query(ancestor=parent_key).filter(Films.api_id == id).get()

