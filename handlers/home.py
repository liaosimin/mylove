__author__ = 'lsm'
import tornado.web
from handlers.base import UserBaseHandler
from settings import *
import dal.models as models
import datetime


# 登陆处理
class Access(UserBaseHandler):

    def initialize(self, action):
        self._action = action

    def get(self):
        if self._action == "login":
            next_url = self.get_argument("next", "")
            return self.render("login.html", context=dict(next_url=next_url))
        elif self._action == "logout":
            self.clear_current_user()
            return self.redirect(self.reverse_url("userLogin"))
        elif self._action == "register":
            return self.render("register.html")
        else:
            return self.send_error(404)

    def post(self):
        if self._action == "login":
            self.login()
        elif self._action == "register":
            self.register()

    @UserBaseHandler.check_arguments("email", "password", "next?")
    def login(self):
        u = self.login_by_email_password(self.args["email"], self.args["password"])
        if not u:
            return self.send_fail(error_text="用户名或密码错误")
        self.set_current_user(u, domain=ROOT_HOST_NAME)
        # url = self.args.get("next", self.reverse_url("Home"))
        # self.redirect(url)
        return self.send_success()

    @UserBaseHandler.check_arguments("email:str", "password:str", "sex:int", "next?")
    def register(self):
        if self.args["sex"] not in [0, 1, 2]:
            return self.send_error(400)
        if not self.register_with_email(self.args["email"], self.args["password"], self.args["sex"]):
            return self.send_fail("邮箱已经被注册")
        return self.send_success()


class Home(UserBaseHandler):
    @tornado.web.authenticated
    def get(self):
        return self.render("home.html")

class SetProfile(UserBaseHandler):
    @tornado.web.authenticated
    def get(self):
        test = "test"
        return self.render("set-profile.html", test=test)

    @tornado.web.authenticated
    @UserBaseHandler.check_arguments("action:str", "data")
    def post(self):
        action = self.args["action"]
        data = self.args["data"]

        if action == "edit_realname":
            self.session.query(models.User).filter_by(id=self.current_user.id).update({models.User.realname: data})
        elif action == "edit_wx_username":
            self.session.query(models.User).filter_by(id=self.current_user.id).update({models.User.wx_username: data})
        elif action == "edit_birthday":
            data = eval(data)
            date = datetime.date(int(data["year"]), int(data["month"]), 1)
            self.session.query(models.User).filter_by(id=self.current_user.id).update({models.User.birthday: date})
        elif action == "edit_height":
            self.session.query(models.User).filter_by(id=self.current_user.id).update({models.User.height: data})
        elif action == "edit_weight":
            self.session.query(models.User).filter_by(id=self.current_user.id).update({models.User.weight: data})
        elif action == "edit_intro":
            self.session.query(models.User).filter_by(id=self.current_user.id).update({models.User.intro: data})
        else:
            return self.send_fail("you are wrong")
        self.session.commit()
        return self.send_success()

class Chat(UserBaseHandler):
    #@tornado.web.authenticated
    def get(self):
        return self.render("chatroom.html")