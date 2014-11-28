""""
importer_cineworld.py

Defines the CineWorldImporter class.
"""


from xml.dom import minidom
import urllib2
import datetime

import importer
import models


class CineWorldImporter(importer.Importer):
    
    BASE_URL = 'http://www.cineworld.co.uk/syndication/'
    CINEMAS = 'all-performances.xml'
    
    def import_data(self):
        """
        Downloads, parses and imports cinemas, films
        and film times into the datastore.
        """
        
        cinemas, films = self._get_cinemas()
        
        for film in films:
            f = models.Film.get_by_api_id(film['api_id'])
            
            if f is None:   
                f = models.Film()
            
            f.populate(**film)
            f.put()
        
        for cinema in cinemas:
            c = models.Cinema.get_by_api_id(cinema['api_id'])
            
            if c is None:   
                c = models.Cinemas(parent=models.parent_key)
            
            c.populate(**cinema)
            c.put()
            ct = c.get_film_times()
    
    def _get_cinemas(self):
        """
        Downloads and parses cinemas, films and showing times.
        Returns a tuple (cinemas, films).
        """
        
        d = self._get_dom(self.BASE_URL + self.CINEMAS)
        r = d.childNodes[0] # <cinemas>
        cinema_nodes = r.childNodes # <cinema> array
        
        cinemas = []
        films = []
        edis = []
        
        for cn in cinema_nodes:
            attrs = cn.attributes
            
            try:
                c = {
                    'name' : attrs['name'].value,
                    'address': attrs['address'].value + ' ' + attrs['postcode'].value,
                    'url': attrs['root'].value + attrs['url'].value,
                    'api_id': attrs['id'].value,
                    'films': []
                }
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
                t = []
                show_nodes = fn.firstChild.childNodes
                
                for sn in show_nodes:
                    try:
                        t.append(
                            datetime.datetime.strptime(
                                sn.attributes['date'].value + ' ' + sn.attributes['time'].value,
                                '%a %d %b %H:%M'
                            )
                        )
                    except KeyError, ValueError:
                        raise importer.ImporterException()
                
                c['films'].append({
                    'api_id': edi,
                    'times': t
                })
                
                # Get film info
                if edi in edis:
                    continue    # We already have film info
                
                edis.append(edi)
                
                try:
                    f = {
                        'name': attrs['title'].value,
                        'rating': attrs['rating'].value,
                        'release': attrs['release'].value,
                        'length': attrs['length'].value,
                        'director': attrs['director'].value,
                        'synopsis': attrs['synopsis'].value,
                        'cast': attrs['cast'].value,
                        'api_id': edi,
                        'url': root + attrs['url'].value,
                        'poster': root + attrs['poster'].value
                    }
                except KeyError:
                    raise importer.ImporterException()
                
                films.append(f)
        
        return cinemas, films
                
    
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



