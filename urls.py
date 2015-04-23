__author__ = 'lsm'
import handlers.home
import handlers.chatroom
handlers = [
    (r"/login", handlers.home.Access,{"action": "login"}, "userLogin"),
    (r"/logout", handlers.home.Access, {"action": "logout"}, "userLogout"),
    (r"/register", handlers.home.Access, {"action": "register"}, "userRegister"),

    (r"/", handlers.home.Home, {}, "Home"),
    (r"/setprofile", handlers.home.SetProfile, {}, "SetProfile"),

    (r"/chat", handlers.home.Chat, {}, "Chat"),
    (r"/websocket", handlers.chatroom.Websocket, {}, "websocket")

]