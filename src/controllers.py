"""
Request handlers for non-static pages go here.
"""

import os

import webapp2
import jinja2
from google.appengine.api import taskqueue

from handlers import *

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
        taskqueue.add(url='/import_worker', retry_options=taskqueue.TaskRetryOptions(task_retry_limit=0))
        
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.write('Task started (check status at http://localhost:8000/taskqueue or https://appengine.google.com/)')

class ImportWorker(RootHandler):
    def post(self):
        import importer_cineworld
        i = importer_cineworld.CineWorldImporter()
        i.import_data()
        
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.write('Done')

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
    webapp2.Route('/about', AboutHandler),
    webapp2.Route('/contact', ContactHandler),
    webapp2.Route('/search', SearchHandler),
    webapp2.Route('/cinemas', CinemaHandler),
], debug=True, config=config)


        


