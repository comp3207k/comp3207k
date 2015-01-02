"""
Request handlers for non-static pages go here.
"""

import os

import webapp2
import jinja2

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.join(os.path.dirname(__file__), 'templates')),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)


class RootHandler(webapp2.RequestHandler):
    
    def render(self, template, vars):
        template = JINJA_ENVIRONMENT.get_template(template)
        self.response.write(template.render(vars))



class Index(RootHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.write('Hello, World!')


class Login(RootHandler):
    def get(self):
        self.render('index.html', {})


class Import(RootHandler):
    def get(self):
        import importer_cineworld
        i = importer_cineworld.CineWorldImporter()
        i.import_data()
        
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.write('Done')

application = webapp2.WSGIApplication([
    ('/', Index),
    ('/login', Login),
    ('/import', Import),
], debug=True)




        


