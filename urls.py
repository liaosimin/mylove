__author__ = 'lsm'
handlers = [
    (r"/customer/login", handlers.customer.Access, {"action":"login"}, "customerLogin")
]