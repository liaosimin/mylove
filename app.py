__author__ = 'lsm'
#! /usr/bin/env python3
#import gc

import dal.models as models
import tornado.web
import tornado.ioloop
from tornado.options import options, define
define("debug", default=0, help="debug mode: 1 to open, 0 to close")
define("port", default=8887, help="port, defualt: 8887")
import os

from urls import handlers

settings = {
    "static_path": os.path.join(os.path.dirname(__file__), "static"),
    "static_url_prefix": "/static/",
    "template_path": os.path.join(os.path.dirname(__file__), "templates"),
    "cookie_secret": "shabianishishabianishi",
    "xsrf_cookies": False  # todo it must be true
}

class Application(tornado.web.Application):
    def __init__(self):
        settings["debug"] = bool(options.debug)
        super().__init__(handlers, **settings)

def main():
    models.init_db_data()
    tornado.options.parse_command_line()
    application = Application()
    application.listen(options.port)
    if options.debug:
        debug_str = "in debug mode"
    else:
        debug_str = "in production mode"
    print("running mylove {0} @ {1}...".format(debug_str, options.port))
#    print("garbage collector: collected %d objecs"%gc.collect())
    tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
    main()