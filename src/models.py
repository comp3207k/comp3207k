"""
Databstore models.
"""

import time
import webapp2_extras.appengine.auth.models
from google.appengine.ext import ndb
from webapp2_extras import security
from google.appengine.ext import ndb

class User(webapp2_extras.appengine.auth.models.User):
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

# Parent key for all models except FilmTimes
parent_key = ndb.Key('parent', 1)

class Cinemas(ndb.Model):
    """
    Cineworld cinemas.
    """
    
    api_id = ndb.StringProperty()
    name = ndb.StringProperty()
    address = ndb.StringProperty()
    url = ndb.StringProperty()
    
    @classmethod
    def get_by_api_id(self, id):
        """Returns a single result or None."""
        return Films.query(api_id=id).get()
    
    @classmethod
    def get_film_times(self):
        """Returns a list of FilmTime objects."""
        return FilmTimes.query(ancestor=self).fetch(1000)
    
    @classmethod
    def delete_film_times(self):
        """Deletes all the FilmTime objects for this cinema."""
        for t in self.get_film_times():
            t.key.delete


class FilmTimes(ndb.Model):
    """
    Film times. A Cinema object is used as
    a parent in the datastore.
    """
    
    film_key = ndb.KeyProperty()
    time = ndb.DateTimeProperty()


class Films(ndb.Model):
    """
    Film information.
    """
    
    api_id = ndb.StringProperty()
    name = ndb.StringProperty()
    rating = ndb.StringProperty()
    release = ndb.StringProperty()
    length = ndb.StringProperty()
    director = ndb.StringProperty()
    synopsis = ndb.StringProperty()
    cast = ndb.StringProperty()
    url = ndb.StringProperty()
    poster = ndb.StringProperty()
    
    @classmethod
    def get_by_api_id(self, id):
        """Returns a single result or None."""
        return Films.query(Films.api_id==id).get()

