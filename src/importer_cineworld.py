""""
importer_cineworld.py

Defines the CineWorldImporter class.
"""


from xml.dom import minidom
import urllib2
import datetime
import logging

from google.appengine.ext import ndb

import importer
import models


class CineWorldImporter(importer.Importer):
    
    BASE_URL = 'http://crick.eu/'   #'http://www.cineworld.co.uk/syndication/'
    CINEMAS = 'all-performances.xml'
    
    def needs_updating(self):
        """
        Checks if the CineWorld Mega XML File Of Doom has
        been modfied since the last update.
        """
        
        s = self._get_lastmod(self.BASE_URL + self.CINEMAS)
        d = models.LastUpdate.get_updated()
        
        return d != s
        
        
    
    def import_data(self):
        """
        Downloads, parses and imports cinemas, films
        and film times into the datastore.
        """
        
        cinemas, films, filmtimes, mod = self._get_cinemas()
        
        self._import_cinemas_films(cinemas, films)
        self._import_filmtimes(filmtimes)
        
        models.LastUpdate.set_updated(mod)
    
    @ndb.transactional
    def _import_cinemas_films(self, cinemas, films):
        for film in films:
            f = models.Films.get_by_api_id(film['api_id'])
            
            if f is None:   
                f = models.Films(parent=models.parent_key)
            
            f.populate(**film)
            f.put()
        
        for cinema in cinemas:
            c = models.Cinemas.get_by_api_id(cinema['api_id'])
            
            if c is None:
                c = models.Cinemas(parent=models.parent_key)
            
            c.populate(**cinema)
            c.put()
    
    @ndb.transactional
    def _import_filmtimes(self, filmtimes):
        logging.info('Deleting film times')
        # Delete all film times because there is no id to use
        models.FilmTimes.delete_all()
        
        logging.info('Creating film times')
        n = 0
        
        for ft in filmtimes:
            c = models.Cinemas.get_by_api_id(ft['cinema_api_id']).key
            f = models.Films.get_by_api_id(ft['film_api_id']).key
            
            nf = models.FilmTimes(parent=c, film_key=f, time=ft['time'])
            nf.put()
            n += 1
            if n % 100 == 0:
                logging.info(n)
    
    def _get_cinemas(self):
        """
        Downloads and parses XML into python objects.
        Returns a tuple (cinemas, films, filmtimes, lastmod).
        """
        
        d = self._get_dom(self.BASE_URL + self.CINEMAS)
        mod = self._get_lastmod(self.BASE_URL + self.CINEMAS)
        r = d.childNodes[0] # <cinemas>
        cinema_nodes = r.childNodes # <cinema> array
        
        cinemas = []
        films = []
        filmtimes = []
        edis = []
        
        for cn in cinema_nodes:
            attrs = cn.attributes
            
            try:
                c = {
                    'api_id': attrs['id'].value,
                    'name' : attrs['name'].value,
                    'address': attrs['address'].value + ' ' + attrs['postcode'].value,
                    'url': attrs['root'].value + attrs['url'].value,
                }
                
                c_api_id = attrs['id'].value
            except KeyError:
                raise importer.ImporterException()
            
            cinemas.append(c)
            
            root = attrs['root'].value
            
            try:
                film_nodes = cn.firstChild.childNodes
            except AttributeError:
                continue
            
            for fn in film_nodes:
                attrs = fn.attributes
                
                try:
                    edi = attrs['edi'].value
                except KeyError:
                   continue # Not interested in films with no edi
               
               # Get show times
                show_nodes = fn.firstChild.childNodes
                
                for sn in show_nodes:
                    try:
                        t = datetime.datetime.strptime(
                            sn.attributes['date'].value + ' ' + sn.attributes['time'].value, '%a %d %b %H:%M'
                        )
                    except KeyError, ValueError:
                        raise importer.ImporterException()
                
                    filmtimes.append({
                        'cinema_api_id': c_api_id,
                        'film_api_id': edi,
                        'time': t
                    })
                
                # Get film info
                if edi in edis:
                    continue    # We already have film info
                
                edis.append(edi)
                
                try:
                    f = {
                        'api_id': edi,
                        'title': attrs['title'].value,
                        'rating': attrs['rating'].value,
                        'release': attrs['release'].value,
                        'length': attrs['length'].value,
                        'director': attrs['director'].value,
                        'synopsis': attrs['synopsis'].value,
                        'cast': attrs['cast'].value,
                        'url': root + attrs['url'].value,
                        'poster': root + attrs['poster'].value
                    }
                except KeyError:
                    raise importer.ImporterException()
                
                films.append(f)
        
        return cinemas, films, filmtimes, mod
                
    
    def _get_dom(self, url):
        """Returns DOM tree of XML page."""
        req = urllib2.urlopen(url)
        info = req.info()
        
        if info['Content-Type'] != 'text/xml':
            raise importer.ImporterException()
        
        return minidom.parse(req)
    
    
    def _get_lastmod(self, url):
        """
        Makes a HTTP HEAD request and returns the last
        modified header.
        """
        
        req = urllib2.urlopen(HeadRequest(url))
        info = req.info()
        
        return info['Last-Modified']


class HeadRequest(urllib2.Request):
    """Allows urllib2 to make a HEAD request."""
    
    def get_methd(self):
        return 'HEAD'



