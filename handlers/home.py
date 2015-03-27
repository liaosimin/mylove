__author__ = 'lsm'
from libs.webbase import BaseHandler

class Home(BaseHandler):
    def get(self):
        return self.render("home.html")