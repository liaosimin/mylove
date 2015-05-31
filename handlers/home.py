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
        elif self._action == "getuniv":
            self.getuniv()


    @UserBaseHandler.check_arguments("email", "password", "next?")
    def login(self):
        u = self.login_by_email_password(self.args["email"], self.args["password"])
        if not u:
            return self.send_fail(error_text="用户名或密码错误")
        self.set_current_user(u, domain=ROOT_HOST_NAME)
        # url = self.args.get("next", self.reverse_url("Home"))
        # self.redirect(url)
        return self.send_success()

    @UserBaseHandler.check_arguments("email:str", "password:str", "sex:int", "univ_id:int", "next?")
    def register(self):
        if self.args["sex"] not in [0, 1, 2]:
            return self.send_error(400)
        if not self.args["email"] or not self.args["password"]:
            return self.send_fail("邮箱或密码不能为空")
        if not self.register_with_email(self.args["email"], self.args["password"],
                                        self.args["sex"], self.args["univ_id"]):
            return self.send_fail("邮箱已经被注册")
        return self.send_success()

    @UserBaseHandler.check_arguments("univ:str")
    def getuniv(self):
        univ = self.args["univ"]
        if not univ:
            return self.send_success(data=[])
        univs = self.session.query(models.University).filter(models.University.name.like(univ+'%')).limit(10).all()
        data_list = [{'id': x.id, 'name': x.name} for x in univs]
        return self.send_success(data=data_list)



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
        page_size = 5
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
            praise_sum = self.session.query(models.UserPraisePhoto).filter_by(photo_id=photo.id).count()
            data_list.append({'id': photo.id, 'uid': photo.author.id, 'code': photo.author.code,
                              'praise_sum':praise_sum,
                              'avatar_url': photo.author.avatar_url, 'nickname': photo.author.nickname,
                              'sex': photo.author.sex, 'time': self.timedelta(photo.create_datetime),
                              'img_url': photo.img_url, 'info_label': info_label, 'intro': photo.intro})
        return self.send_success(data=data_list)

    @tornado.web.authenticated
    @UserBaseHandler.check_arguments("action:str", "id")
    def post(self):
        action = self.args['action']
        id = self.args['id']
        if action == 'praise':
            if self.session.query(models.UserPraisePhoto).filter_by(uid=self.current_user.id, photo_id=id).first():
                return self.send_fail("重复点赞")
            self.session.add(models.UserPraisePhoto(uid=self.current_user.id, photo_id=id))
            self.session.commit()
        elif action == 'love':
            self.session.add(models.UserLoveUser(uid1=self.current_user.id, uid2=id))
            self.session.commit()
        return self.send_success()


class Community(UserBaseHandler):
    @tornado.web.authenticated
    @UserBaseHandler.check_arguments("action?:str")
    def get(self):
        if 'action' not in self.args.keys():
            return self.render("community.html")
        action = self.args["action"]
        if action == "thread":
            self.get_thread()
        elif action == "reply":
            self.get_reply()

    @UserBaseHandler.check_arguments("page:int")
    def get_thread(self):
        page = self.args["page"]
        page_size = 20
        threads = self.session.query(models.Thread).order_by(desc(models.Thread.id)).\
            offset(page*page_size).limit(page_size).all()
        data_list = []
        for thread in threads:
            university_name = ''
            grade_name = ''
            if thread.author.university:
                university_name = thread.author.university.name
            if thread.author.grade:
                grade_name = thread.author.grade_name
            ug_name = university_name+' '+grade_name
            praise_sum = self.session.query(models.UserPraiseThread).filter_by(thread_id=thread.id).count()
            reply_sum = self.session.query(models.ReplyThread).filter_by(thread_id=thread.id).count()
            data_list.append({'id': thread.id, 'uid': thread.author.id, 'code': thread.author.code,
                              'praise_sum': praise_sum, 'reply_sum': reply_sum,
                              'avatar_url': thread.author.avatar_url, 'nickname': thread.author.nickname,
                              'sex': thread.author.sex, 'time': self.timedelta(thread.create_datetime),
                              'intro': thread.intro, 'ug_name':ug_name})
        return self.send_success(data=data_list)

    @UserBaseHandler.check_arguments("thread_id:int")
    def get_reply(self):
        thread_id = self.args["thread_id"]
        replys = self.session.query(models.ReplyThread).filter_by(thread_id=thread_id).all()
        data_list = [{'author_name': x.author.nickname,
                      'reply_name': '楼主' if not x.parent_id else x.parent.author.nickname,
                      'text': x.text, 'code': x.author.code, 'id': x.id} for x in replys]
        return self.send_success(data=data_list)

    @tornado.web.authenticated
    @UserBaseHandler.check_arguments("action:str")
    def post(self):
        action = self.args["action"]
        if action == 'issue':
            self.issue_thread()
        elif action == 'praise':
            self.praise()
        elif action == "reply":
            self.reply()

        return self.send_success()

    @UserBaseHandler.check_arguments("data:str")
    def issue_thread(self):
        data = self.args["data"]
        self.session.add(models.Thread(intro=data, author_id=self.current_user.id))
        self.session.commit()

    @UserBaseHandler.check_arguments("id:int")
    def praise(self):
        id = self.args["id"]
        if self.session.query(models.UserPraiseThread).filter_by(uid=self.current_user.id, thread_id=id).first():
            return self.send_fail("重复点赞")
        self.session.add(models.UserPraiseThread(uid=self.current_user.id, thread_id=id))
        self.session.commit()

    @UserBaseHandler.check_arguments("tid:int", "rid:int", "data:str")
    def reply(self):
        thread_id = self.args["tid"]
        reply_id = self.args["rid"]
        text = self.args["data"]

        args = dict(thread_id=thread_id, author_id=self.current_user.id, text=text)
        if reply_id:
            args['parent_id'] = reply_id
        self.session.add(models.ReplyThread(**args))
        self.session.commit()



class Profile(UserBaseHandler):
    @tornado.web.authenticated
    @UserBaseHandler.check_arguments("page?:int")
    def get(self, code):
        if 'page' not in self.args.keys():
            return self.render("profile.html")
        else:
            try:
                user = self.session.query(models.User).filter_by(code=code).one()
            except:
                return self.send_error(404, "no user")

            photo_url = []
            photos = self.session.query(models.Photo).filter_by(id=user.id).all()
            for photo in photos:
                photo_url.append('http://7xitqn.com1.z0.glb.clouddn.com/'+photo.img_url)
            if not user.birthday:
                birthday = 0
            else:
                birthday = user.birthday.strftime('%Y-%m')
            following_sum = self.session.query(models.Follow).filter_by(uid1=user.id).count()
            follower_sum = self.session.query(models.Follow).filter_by(uid2=user.id).count()
            follow = self.session.query(models.Follow).filter_by(uid1=self.current_user.id, uid2=user.id).first()
            if follow:
                followed = True
            else:
                followed = False
            return self.send_success(nickname=user.nickname,
                                     sex=user.sex,
                                     avatar_url='http://7xit5j.com1.z0.glb.clouddn.com/'+user.avatar_url,
                                     photo_url=photo_url,
                                     birthday=birthday,
                                     height=user.height,
                                     weight=user.weight,
                                     intro=user.intro,
                                     univer_name=user.university.name,
                                     grade_name=user.grade_name,
                                     following_sum=following_sum,
                                     follower_sum=follower_sum,
                                     followed=followed)

    @tornado.web.authenticated
    def post(self, code):
        try:
            user = self.session.query(models.User).filter_by(code=code).one()
        except:
            return self.send_error(404, "no user")
        self.session.add(models.Follow(uid1=self.current_user.id, uid2=user.id))
        self.session.commit()
        return self.send_success()


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
