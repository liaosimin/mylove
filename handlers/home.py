__author__ = 'lsm'
import tornado.web
from handlers.base import UserBaseHandler, WxOauth2
from settings import *
import dal.models as models
import datetime, time
from sqlalchemy import desc
import hashlib
import random
import urllib
from qiniu import put_data
import qiniu
from qiniu.utils import urlsafe_base64_decode

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

        if action == "edit_avatar":
            return self.send_qiniu_token(BUCKET_AVATAR, self.current_user.id)
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


class PostPhoto(UserBaseHandler):
    @tornado.web.authenticated
    def get(self):
        return self.render("post_photo.html")

    @tornado.web.authenticated
    @UserBaseHandler.check_arguments("intro:str", "data")
    def post(self):
        intro = self.args["intro"]
        data = self.args["data"].split(',')

        q = qiniu.Auth(ACCESS_KEY, SECRET_KEY)
        token = q.upload_token(BUCKET_PHOTO)
        key = str(time.time())+':'+str(self.current_user.id)
        ret, info = put_data(token, key, urlsafe_base64_decode(data[1]), mime_type=data[0][5:-7], check_crc=True)
        if info.status_code == 200:
            self.session.add(models.Photo(img_url=key, intro=intro, author_id=self.current_user.id))
            self.session.commit()
            return self.send_success()
        return self.send_error()



class Chat(UserBaseHandler):
    #@tornado.web.authenticated
    def get(self):
        return self.render("chatroom.html")


class Photo(UserBaseHandler):

    @tornado.web.authenticated
    @UserBaseHandler.check_arguments("page?:int")
    def get(self):
        if 'page' not in self.args.keys():
            return self.render("photo.html")
        page = self.args["page"]
        page_size = 10
        photos = self.session.query(models.Photo).order_by(desc(models.Photo.id)).\
            offset(page*page_size).limit(page_size).all()
        data_list = []
        for photo in photos:
            info_label = []
            if photo.author.birthday:
                info_label.append(photo.author.birthday.strftime('%Y-%m'))
            if photo.author.height:
                info_label.append(str(photo.author.height)+'cm')
            if photo.author.weight:
                info_label.append(str(photo.author.weight)+'kg')
            if photo.author.university:
                info_label.append(photo.author.university.name)
            if photo.author.grade:
                info_label.append(photo.author.grade_name)
            data_list.append({'avatar_url': photo.author.avatar_url, 'nickname': photo.author.nickname,
                              'sex': photo.author.sex, 'time': self.timedelta(photo.create_datetime),
                              'img_url': photo.img_url, 'info_label': info_label, 'intro': photo.intro})
        return self.send_success(data=data_list)

class Wx(UserBaseHandler):
    @tornado.web.authenticated
    def get(self):
        jsapi_ticket = WxOauth2.get_jsapi_ticket()
        noncestr = ''.join(random.sample('zyxwvutsrqponmlkjihgfedcba0123456789', 10))
        timestamp = int(time.time())
        url = 'http://mt01.monklof.com/setprofile'
        sign_str = 'jsapi_ticket=%s&noncestr=%s&timestamp=%d&url=%s' % (jsapi_ticket, noncestr, timestamp, url)
        signature = hashlib.sha1(sign_str.encode('utf-8')).hexdigest()
        print(jsapi_ticket, noncestr, timestamp, url, sign_str, signature)
        return self.send_success(timestamp=timestamp, noncestr=noncestr, signature=signature)

    @tornado.web.authenticated
    @UserBaseHandler.check_arguments("serverid:str")
    def post(self):
        serverid = self.args["serverid"]
        url = 'http://file.api.weixin.qq.com/cgi-bin/media/get?access_token=%s&media_id=%s' %\
              (WxOauth2.get_client_access_token(), serverid)
        photo = urllib.request.urlopen(url).read()
        print(url, photo)
