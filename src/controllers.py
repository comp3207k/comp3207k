"""
Request handlers for non-static pages go here.
"""

import os

import webapp2
import jinja2
from google.appengine.api import taskqueue

from handlers import *
import search
import models

config = {
  'webapp2_extras.auth': {
    'user_model': 'models.User',
    'user_attributes': ['name']
  },
  'webapp2_extras.sessions': {
    'secret_key': 'YOUR_SECRET_KEY'
  }
}



logging.getLogger().setLevel(logging.DEBUG)


JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.join(os.path.dirname(__file__), 'views')),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)


class RootHandler(webapp2.RequestHandler):
    
    def render(self, template, vars):
        template = JINJA_ENVIRONMENT.get_template(template)
        self.response.write(template.render(vars))








class Import(RootHandler):
    """
    Kicks off the ImportWorker.
    """
    
    def get(self):
        taskqueue.add(url='/import_worker', retry_options=taskqueue.TaskRetryOptions(task_retry_limit=0))
        
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.write('Task started (check status at http://localhost:8000/taskqueue or https://appengine.google.com/)')

class ImportWorker(RootHandler):
    """
    A task that import CineWorld data.
    """
    
    def post(self):
        import importer_cineworld
        i = importer_cineworld.CineWorldImporter()
        i.import_data()
        
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.write('Done')

class Index(RootHandler):
    """
    Kicks off the IndexWorker.
    """
    
    def get(self):
        taskqueue.add(url='/index_worker', retry_options=taskqueue.TaskRetryOptions(task_retry_limit=0))
        
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.write('Task started (check status at http://localhost:8000/taskqueue or https://appengine.google.com/)')

class IndexWorker(RootHandler):
    """
    A task that adds new cinemas and films to the index.
    """
    
    def post(self):
        cinemas = models.Cinemas.query().fetch(1000)
        
        for c in cinemas:
            search.import_cinema(c)
        
        films = models.Films.query().fetch(1000)
        
        for f in films:
            search.import_film(f)


class SearchAJAX(RootHandler):
    """Returns JSON based on search query"""
    
    def get(self):
        query = self.request.get('q')[:100].strip()
        
        if len(query) == 0:
            self.response.write('')
            return
        
        cinemas, films = search.query(query)
        
        self.response.headers['Content-Type'] = 'application/json'
        
        self.render('search_ajax.json', {
            'n_cinemas': cinemas.number_found,
            'results_cinemas': cinemas.results,
            'n_films': films.number_found,
            'results_films': films.results,
        })
        



application = webapp2.WSGIApplication([
    webapp2.Route('/', MainHandler, name='home'),
    webapp2.Route('/signup', SignupHandler),
    webapp2.Route('/<type:v|p>/<user_id:\d+>-<signup_token:.+>',
      handler=VerificationHandler, name='verification'),
    webapp2.Route('/password', SetPasswordHandler),
    webapp2.Route('/login', LoginHandler, name='login'),
    webapp2.Route('/logout', LogoutHandler, name='logout'),
    webapp2.Route('/forgot', ForgotPasswordHandler, name='forgot'),
    webapp2.Route('/authenticated', AuthenticatedHandler, name='authenticated'),
    webapp2.Route('/import', Import),
    webapp2.Route('/import_worker', ImportWorker),
    webapp2.Route('/index', Index),
    webapp2.Route('/index_worker', IndexWorker),
    webapp2.Route('/about', AboutHandler),
	webapp2.Route('/profile', ProfileHandler),
    webapp2.Route('/contact', ContactHandler),
    webapp2.Route('/search', SearchHandler),
    webapp2.Route('/search_ajax', SearchAJAX),
    webapp2.Route('/cinemas', CinemaHandler),
    webapp2.Route('/movie', MovieHandler),
], debug=True, config=config)


        


