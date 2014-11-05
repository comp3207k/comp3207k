"""
Databstore models.
"""

from google.appengine.ext import ndb


# Parent key for all models except FilmTimes
parent_key = ndb.key('parent')

class Cinemas(ndb.Model):
    """
    Cineworld cinemas.
    """
    
    api_id = ndb.IntegerProperty()
    name = ndb.StringProperty()
    address = ndb.StringProperty()
    url = ndb.StringProperty()


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
    
    api_id = ndb.IntegerProperty()
    name = ndb.StringProperty()
    rating = ndb.StringProperty()
    release = ndb.StringProperty()
    length = ndb.StringProperty()
    director = ndb.StringProperty()
    synopsis = ndb.StringProperty()
    cast = ndb.StringProperty()
    url = ndb.StringProperty()
    poster = ndb.StringProperty()
    api_id = ndb.IntegerProperty()

