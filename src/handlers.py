"""
handlers.py
Request handlers.
Only the user_required() function and BaseHandler class contain
modified code, the rest of the file is original.
"""

from google.appengine.ext.webapp import template
from google.appengine.ext import ndb

import logging
import os.path
import webapp2
from models import Films
from models import Cinemas
from models import User
from webapp2_extras import auth
from webapp2_extras import sessions

from webapp2_extras.auth import InvalidAuthIdError
from webapp2_extras.auth import InvalidPasswordError



def user_required(handler):
    """
    Decorator which checks if the user is logged in.
    
    Derived from https://github.com/chrisgco/User-Auth-in-Google-App-Engine (GPL).
    """

    def check_login(self, *args, **kwargs):
        auth = self.auth
        if not auth.get_user_by_session():
            self.redirect(self.uri_for('login'), abort=True)
        else:
            return handler(self, *args, **kwargs)

    return check_login


class BaseHandler(webapp2.RequestHandler):
    """
    Parent RequestHandler class defines methods for user
    authentication.
    
    Derived from https://github.com/chrisgco/User-Auth-in-Google-App-Engine (GPL).
    """
    
    @webapp2.cached_property
    def auth(self):
        """Shortcut to access the auth instance as a property."""
        return auth.get_auth()

    @webapp2.cached_property
    def user_info(self):
        """Shortcut to access a subset of the user attributes that are stored
        in the session.

        The list of attributes to store in the session is specified in
          config['webapp2_extras.auth']['user_attributes'].
        :returns
          A dictionary with most user information
        """
        return self.auth.get_user_by_session()

    @webapp2.cached_property
    def user(self):
        """Shortcut to access the current logged in user.

        Unlike user_info, it fetches information from the persistence layer and
        returns an instance of the underlying model.

        :returns
          The instance of the user model associated to the logged in user.
        """
        u = self.user_info
        return self.user_model.get_by_id(u['user_id']) if u else None

    @webapp2.cached_property
    def user_model(self):
        """Returns the implementation of the user model.

        It is consistent with config['webapp2_extras.auth']['user_model'], if set.
        """    
        return self.auth.store.user_model

    @webapp2.cached_property
    def session(self):
        """Shortcut to access the current session."""
        return self.session_store.get_session(backend="datastore")

    def render_template(self, view_filename, params=None):
        if not params:
            params = {}
        
        user = self.user_info
        params['user'] = user
        path = os.path.join(os.path.dirname(__file__), 'views', view_filename)
        self.response.out.write(template.render(path, params))

    def display_message(self, message):
        """Utility function to display a template with a simple message."""
        params = {
          'message': message
        }
        self.render_template('message.html', params)

    # this is needed for webapp2 sessions to work
    def dispatch(self):
        # Get a session store for this request.
        self.session_store = sessions.get_store(request=self.request)

        try:
            # Dispatch the request.
            webapp2.RequestHandler.dispatch(self)
        finally:
            # Save all sessions.
            self.session_store.save_sessions(self.response)


class MainHandler(BaseHandler):
  """
  Displays home page or login page.
  """
  
  def get(self):
    if self.user:
      latest_films = Films.query().order(-Films.release).fetch(12)
      template_values = {
          'news':latest_films,
          'localUser': "Hi " + self.user.name
          }
      self.render_template('home.html', params=template_values)
    else:
      self.redirect(self.uri_for('login'))


class AboutHandler(BaseHandler):
  """
  About page.
  """
  
  def get(self):
    if self.user:
      template_values = {
          'localUser': "Hi " + self.user.name
          }
      self.render_template('about.html', params=template_values)
    else:
      self.redirect(self.uri_for('login'))


class ProfileHandler(BaseHandler):
  """
  User settings.
  """
  
  @user_required
  def get(self):
    template_values = {
      'user': self.user,
      'userUserName': self.user.auth_ids,
      'userFirstName': self.user.name,
      'userLastName': self.user.last_name,
      'userEmail': self.user.email_address,
      'localUser': "Hi " + self.user.name
    }
    self.render_template('profile.html', params=template_values)
  
  @user_required
  def post(self):
    p_name = self.request.get('name').strip()
    p_email = self.request.get('email').strip()
    p_password = self.request.get('password')
    
    if len(p_name) >= 2 and p_name.isalnum():
        self.user.name = p_name
        self.user.put()
    else:
        self.display_message('Invalid username')
        return
    
    if len(p_email) > 5:
        self.user.email_address = p_email
        self.user.put()
    else:
        self.display_message('Invalid email')
        return
    
    if len(p_password) > 0:
        self.display_message('Password changed')
        return
    
    self.display_message('Details updated')


class ContactHandler(BaseHandler):
  """
  Contact details of developers.
  """
  
  def get(self):
    if self.user:
      template_values = {
          'localUser': "Hi " + self.user.name
          }
      self.render_template('contact.html', params=template_values)
    else:
      self.redirect(self.uri_for('login'))



class CinemaHandler(BaseHandler):
  """
  Displays a list of cinemas.
  """
  
  def get(self):
    if self.user:
      cinemas = Cinemas.query().order(+Cinemas.name).fetch()
      
      n = 0
      while n < len(cinemas):
        cinemas[n].films = cinemas[n].get_films()
        n += 1
      
      template_values = {
          'cinema_list' : cinemas,
          'localUser': "Hi " + self.user.name
          }
      self.render_template('cinemas.html', params=template_values)
    else:
      self.redirect(self.uri_for('login'))


class MovieHandler(BaseHandler):
  """
  Displays details about a specific film.
  """
  
  def get(self, id):
    if self.user:
      movie = Films.query(Films.api_id == id).get()
      
      if movie is None:
        return webapp2.abort(404)
      
      cid = self.request.get('cinema')
      cinema = Cinemas.get_by_api_id(cid)
      cname = None
      film_times = None
      
      if cinema:
        cname = cinema.name
        film_times = Cinemas.get_film_times_cinema(cinema, movie)
      
      template_values = {
          'localUser': "Hi " + self.user.name,
          'movie':movie,
          'mt':movie.title,
          'cinema_name': cname,
          'film_times': film_times,
          }
      self.render_template('movie.html', params=template_values)
    else:
      self.redirect(self.uri_for('login'))      


class SignupHandler(BaseHandler):
  def get(self):
    self.render_template('register.html')

  def post(self):
    user_name = self.request.get('username')
    email = self.request.get('email')
    name = self.request.get('firstname')
    password = self.request.get('password')
    last_name = self.request.get('lastname')

    unique_properties = ['email_address']
    success, info = self.auth.store.user_model.create_user("auth:" + user_name,
                      email_address=email, name=name, password_raw=password,last_name=last_name)
    user_data = self.user_model.create_user(user_name,
      unique_properties,
      email_address=email, name=name, password_raw=password,
      last_name=last_name, verified=False)
    if not user_data[0]: #user_data is a tuple
      self.render_template("register.html",{"warning":"Invalid input or existing username"})
      return
    if success:
      self.auth.set_session(self.auth.store.user_to_dict(info), remember=True)
    self.redirect(self.uri_for('home'))


class ForgotPasswordHandler(BaseHandler):
  def get(self):
    self._serve_page()

  def post(self):
    username = self.request.get('username')

    user = self.user_model.get_by_auth_id(username)
    if not user:
      logging.info('Could not find any user entry for username %s', username)
      self._serve_page(not_found=True)
      return

    user_id = user.get_id()
    token = self.user_model.create_signup_token(user_id)

    verification_url = self.uri_for('verification', type='p', user_id=user_id,
      signup_token=token, _full=True)

    msg = 'Send an email to user in order to reset their password. \
          They will be able to do so by visiting <a href="{url}">{url}</a>'

    self.display_message(msg.format(url=verification_url))
  
  def _serve_page(self, not_found=False):
    username = self.request.get('username')
    params = {
      'username': username,
      'not_found': not_found
    }
    self.render_template('forgot.html', params)


class VerificationHandler(BaseHandler):
  def get(self, *args, **kwargs):
    user = None
    user_id = kwargs['user_id']
    signup_token = kwargs['signup_token']
    verification_type = kwargs['type']

    # it should be something more concise like
    # self.auth.get_user_by_token(user_id, signup_token)
    # unfortunately the auth interface does not (yet) allow to manipulate
    # signup tokens concisely
    user, ts = self.user_model.get_by_auth_token(int(user_id), signup_token,
      'signup')

    if not user:
      logging.info('Could not find any user with id "%s" signup token "%s"',
        user_id, signup_token)
      self.abort(404)
    
    # store user data in the session
    self.auth.set_session(self.auth.store.user_to_dict(user), remember=True)

    if verification_type == 'v':
      # remove signup token, we don't want users to come back with an old link
      self.user_model.delete_signup_token(user.get_id(), signup_token)

      if not user.verified:
        user.verified = True
        user.put()

      self.display_message('User email address has been verified.')
      return
    elif verification_type == 'p':
      # supply user to the page
      params = {
        'user': user,
        'token': signup_token
      }
      self.render_template('resetpassword.html', params)
    else:
      logging.info('verification type not supported')
      self.abort(404)

class SetPasswordHandler(BaseHandler):

  @user_required
  def post(self):
    password = self.request.get('password')
    old_token = self.request.get('t')

    if not password or password != self.request.get('confirm_password'):
      self.display_message('passwords do not match')
      return

    user = self.user
    user.set_password(password)
    user.put()

    # remove signup token, we don't want users to come back with an old link
    self.user_model.delete_signup_token(user.get_id(), old_token)
    
    self.display_message('Password updated')



class LoginHandler(BaseHandler):
  def get(self):
    self._serve_page()

  def post(self):
    username = self.request.get('username')
    password = self.request.get('password')
    try:
      u = self.auth.get_user_by_password(username, password, remember=True,
        save_session=True)
      self.redirect(self.uri_for('home'))
    except (InvalidAuthIdError, InvalidPasswordError) as e:
      logging.info('Login failed for user %s because of %s', username, type(e))
      self._serve_page(True)

  def _serve_page(self, failed=False):
    username = self.request.get('username')
    params = {
      'username': username,
      'failed': failed
    }
    self.render_template('login.html', params)



class LogoutHandler(BaseHandler):
  def get(self):
    self.auth.unset_session()
    self.redirect(self.uri_for('home'))



class AuthenticatedHandler(BaseHandler):
  @user_required
  def get(self):
    self.render_template('authenticated.html')


