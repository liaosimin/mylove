__author__ = 'lsm'
import handlers.home
import handlers.chatroom
import handlers.qiniu
handlers = [
    (r"/login", handlers.home.Access,{"action": "login"}, "userLogin"),
    (r"/logout", handlers.home.Access, {"action": "logout"}, "userLogout"),
    (r"/register", handlers.home.Access, {"action": "register"}, "userRegister"),

    (r"/", handlers.home.Home, {}, "Home"),
    (r"/setprofile", handlers.home.SetProfile, {}, "SetProfile"),

    (r"/chat", handlers.home.Chat, {}, "Chat"),
    (r"/photo", handlers.home.Photo, {}, "Photo"),
    (r"/wx", handlers.home.Wx, {}, "Wx"),
    (r"/qiniu", handlers.qiniu.QiniuCallback, {}, "Qiniu"),
    (r"/websocket", handlers.chatroom.Websocket, {}, "websocket")

]