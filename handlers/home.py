__author__ = 'lsm'
from libs.webbase import BaseHandler

class Home(BaseHandler):
    def get(self):
        return self.render("home.html")

class SetProfile(BaseHandler):
    def get(self):
        test = "test"
        return self.render("set-profile.html", test=test)

    @BaseHandler.check_arguments("nickname")
    def post(self):
        print(self.args["nickname"])
        return self.send_success()