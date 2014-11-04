""""
importer_cineworld.py

Defines the CineWorldImporter class.
"""


from xml.dom import minidom
import urllib2

import importer


class CineWorldImporter(importer.Importer):
    
    BASE_URL = 'http://www.cineworld.co.uk/syndication/'
    CINEMAS = 'cinemas.xml'
    FILMS = 'film_times.xml'
    
    def import_data(self):
        pass
    
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



