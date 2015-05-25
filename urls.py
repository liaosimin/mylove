__author__ = 'lsm'
import handlers.home
import handlers.chatroom
import handlers.qiniu
handlers = [
    (r"/login", handlers.home.Access,{"action": "login"}, "userLogin"),
    (r"/logout", handlers.home.Access, {"action": "logout"}, "userLogout"),
    (r"/register", handlers.home.Access, {"action": "register"}, "userRegister"),
    (r"/getuniv", handlers.home.Access, {"action": "getuniv"}, "Getuniv"),

    (r"/", handlers.home.Home, {}, "Home"),
    (r"/setprofile", handlers.home.SetProfile, {}, "SetProfile"),
    (r"/profile/(\w+)", handlers.home.Profile, {}, "Profile"),

    (r"/chat", handlers.home.Chat, {}, "Chat"),
    (r"/photo", handlers.home.Photo, {}, "Photo"),
    (r"/community", handlers.home.Community, {}, "Community"),
    (r"/post", handlers.home.PostPhoto, {}, "PostPhoto"),
    (r"/wx", handlers.home.Wx, {}, "Wx"),
    (r"/qiniu", handlers.qiniu.QiniuCallback, {}, "Qiniu"),
    (r"/websocket", handlers.chatroom.Websocket, {}, "websocket")

]