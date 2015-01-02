"""
Databstore models.
"""

from google.appengine.ext import ndb


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

