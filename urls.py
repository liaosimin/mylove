__author__ = 'lsm'
import handlers.home
handlers = [
    (r"/", handlers.home.Home, {}, "customerLogin")
]