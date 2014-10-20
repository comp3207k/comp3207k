"""
Request handlers for non-static pages go here.
"""



import webapp2

class IndexPage(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.write('Hello, World!')

application = webapp2.WSGIApplication([
    ('/', IndexPage),
], debug=True)



