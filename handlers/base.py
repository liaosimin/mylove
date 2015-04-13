__author__ = 'lsm'
from libs.webbase import BaseHandler
from settings import *
import dal.models as models
import tornado

class GlobalBaseHandler(BaseHandler):
    __account_model__ = models.User
    __account_cookie_name__ = "uid"

    @property
    def session(self):
        if hasattr(self, "_session"):
            return self._session
        self._session = models.DBSession()
        return self._session

    def on_finish(self):
        # release db connection
        if hasattr(self, "_session"):
            self._session.close()

    def get_current_user(self):

        if hasattr(self, "_user"):
            return self._user

        uid = self.get_secure_cookie(self.__account_cookie_name__) or b'0'
        uid = int(uid.decode())
        if not uid:
            self._user = None
        else:
            self._user = self.__account_model__.get_by_id(self.session, uid)
            if not self._user:
                Logger.warn("Suspicious Access", "may be trying to fuck you")
        return self._user

    def set_current_user(self, user, domain):
            self.set_secure_cookie(self.__account_cookie_name__, str(user.id), domain=domain)

    def clear_current_user(self):
        self.clear_cookie(self.__account_cookie_name__, domain=ROOT_HOST_NAME)

    def get_login_url(self):
        next_url = self.request.full_url()
        return self.reverse_url("userLogin") + "?next="+tornado.escape.url_escape(next_url)



class UserBaseHandler(GlobalBaseHandler):


    def login_by_email_password(self, email, password):
        try:
            u = self.session.query(models.User).filter_by(email=email, password=password).one()
        except:
            u = None
        return u


    def register_with_email(self, email, password, sex):
        user = models.User(email=email,
                           password=password,
                           sex=sex)

        self.session.add(user)
        self.session.commit()
        return user