"""
search.py

Contains functions to import Films into the search index,
and perform full text searches.
Uses the Google Search API.
"""

from google.appengine.api import search 


def import_film(film):
    """Adds a models.Films object into the index."""
    
    index = get_film_index()
    doc = index.get(generate_film_id(film))
    
    if doc is not None:
        return
    
    document = search.Document(
        doc_id = generate_film_id(film),
        fields = [
            search.TextField(name='title', value=film.title),
            search.TextField(name='synopsis', value=film.synopsis),
            search.AtomField(name='poster', value=film.poster),
            search.AtomField(name='api_id', value=film.api_id),
        ]
    )
    
    index.put(document)


def import_cinema(cinema):
    """Adds a models.Cinemas object into the index."""
    
    index = get_cinema_index()
    doc = index.get(generate_cinema_id(cinema))
    
    if doc is not None:
        return
    
    document = search.Document(
        doc_id = generate_cinema_id(cinema),
        fields = [
            search.TextField(name='name', value=cinema.name),
            search.AtomField(name='url', value=cinema.url),
            search.AtomField(name='api_id', value=cinema.api_id),
        ]
    )
    
    index.put(document)


def query(string):
    """
    Searches films and cinemas and returns (cinemas, films) as
    SearchResults objects.
    """
    
    return get_cinema_index().search(string), get_film_index().search(string)


# Methods below are private to this module

def get_film_index():
    return search.Index(name='films')

def get_cinema_index():
    return search.Index(name='cinemas')


def generate_film_id(film):
    """Generates a unique id for a models.Film object."""
    
    return film.api_id


def generate_cinema_id(cinema):
    """Generates a unique id for a models.Cinema object."""
    
    return cinema.api_id

    

