__author__ = 'lsm'
import handlers.home
handlers = [
    (r"/", handlers.home.Home, {}, "Home"),
    (r"/setprofile", handlers.home.SetProfile, {}, "SetProfile")
]