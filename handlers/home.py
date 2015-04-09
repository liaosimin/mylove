__author__ = 'lsm'
from libs.webbase import BaseHandler
from settings import *

# 登陆处理
class Access(BaseHandler):
    def initialize(self, action):
        self._action = action

    def get(self):
        next_url = self.get_argument('next', '')
        if self._action == "login":
            next_url = self.get_argument("next", "")
            return self.render("login.html",
                                 context=dict(next_url=next_url))
        elif self._action == "logout":
            self.clear_current_user()
            return self.redirect(self.reverse_url("fruitzoneHome"))
        else:
            return self.send_error(404)

    @BaseHandler.check_arguments("phone", "password", "next?")
    def post(self):
        u = models.ShopAdmin.login_by_phone_password(self.session, self.args["phone"], self.args["password"])
        if not u:
            return self.send_fail(error_text = "用户名或密码错误")
        self.set_current_user(u, domain=ROOT_HOST_NAME)
        self.redirect(self.args.get("next", self.reverse_url("fruitzoneHome")))
        return self.send_success()


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