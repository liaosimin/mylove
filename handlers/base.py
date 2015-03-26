__author__ = 'lsm'
from libs.webbase import BaseHandler

class GlobalBaseHandler(BaseHandler):
    # @property
    # def session(self):
    #     if hasattr(self, "_session"):
    #         return self._session
    #     self._session = models.DBSession()
    #     return self._session

    def on_finish(self):
        # release db connection
        if hasattr(self, "_session"):
            self._session.close()