__author__ = 'lsm'
from libs.webbase import BaseHandler
from settings import *
import dal.models as models
import tornado
import datetime, time
import json
import requests
import urllib
import qiniu

class GlobalBaseHandler(BaseHandler):
    __account_model__ = models.User
    __account_cookie_name__ = "uid"

    @property
    def session(self):
        if hasattr(self, "_session"):
            return self._session
        self._session = models.DBSession()
        return self._session

    def on_finish(self):
        # release db connection
        if hasattr(self, "_session"):
            self._session.close()

    def get_current_user(self):

        if hasattr(self, "_user"):
            return self._user

        uid = self.get_secure_cookie(self.__account_cookie_name__) or b'0'
        uid = int(uid.decode())
        if not uid:
            self._user = None
        else:
            self._user = self.__account_model__.get_by_id(self.session, uid)
            if not self._user:
                print("Suspicious Access", "may be trying to fuck you")
        return self._user

    def set_current_user(self, user, domain):
            self.set_secure_cookie(self.__account_cookie_name__, str(user.id), domain=domain)

    def clear_current_user(self):
        self.clear_cookie(self.__account_cookie_name__, domain=ROOT_HOST_NAME)

    def get_login_url(self):
        # next_url = self.request.full_url()
        # return self.reverse_url("userLogin") + "?next="+tornado.escape.url_escape(next_url)
        return self.reverse_url("userLogin")



class UserBaseHandler(GlobalBaseHandler):


    def login_by_email_password(self, email, password):
        try:
            u = self.session.query(models.User).filter_by(email=email, password=password).one()
        except:
            u = None
        return u


    def register_with_email(self, email, password, sex):
        code = int((datetime.datetime.today()-datetime.datetime(2015, 4, 25, 22, 5, 2)).total_seconds()*100)
        user = models.User(email=email,
                           password=password,
                           sex=sex,
                           code=code)

        self.session.add(user)
        self.session.commit()
        return user

    def timedelta(self, date):
        if not date:
            return "1年前"
        timedelta = datetime.datetime.now()-date
        if timedelta.days >= 365:
            return "%d年前" % (timedelta.days/365)
        elif timedelta.days >= 30:
            return "%d月前" % (timedelta.days/30)
        elif timedelta.days > 0:
            return "%d天前" % timedelta.days
        elif timedelta.seconds >= 3600:
            return "%d小时前" % (timedelta.seconds/3600)
        elif timedelta.seconds >= 60:
            return "%d分钟前" % (timedelta.seconds/60)
        else:
            return "%d秒前" % timedelta.seconds

    def send_qiniu_token(self, bucket, id):
        q = qiniu.Auth(ACCESS_KEY, SECRET_KEY)
        token = q.upload_token(bucket, expires=120,
                               policy={"callbackUrl": "http://http://mt01.monklof.com:8887/",
                                       "callbackBody": "key=$(key)&bucket=%s&id=%s" % (bucket, id),
                                       "mimeLimit": "image/*"})
        return self.send_success(token=token, key=str(time.time())+':'+str(id))



jsapi_ticket = {"jsapi_ticket": '', "create_timestamp": 0}  # 用全局变量存好，避免每次都要申请
access_token = {"access_token": '', "create_timestamp": 0}

class WxOauth2:
    __token_url = "https://api.weixin.qq.com/sns/oauth2/access_token?appid={appid}" \
                "&secret={appsecret}&code={code}&grant_type=authorization_code"
    __userinfo_url = "https://api.weixin.qq.com/sns/userinfo?access_token={access_token}&openid={openid}"
    __client_access_token_url = "https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential" \
                              "&appid={appid}&secret={appsecret}".format(appid=MP_APPID, appsecret=MP_APPSECRET)
    __jsapi_ticket_url = "https://api.weixin.qq.com/cgi-bin/ticket/getticket?access_token={access_token}&type=jsapi"
    __template_msg_url = "https://api.weixin.qq.com/cgi-bin/message/template/send?access_token={access_token}"

    @classmethod
    def get_userinfo(cls, code, mode):
        data = cls.get_access_token_openid(code, mode)
        if not data:
            return None
        access_token, openid = data
        userinfo_url = cls.__userinfo_url.format(access_token=access_token, openid=openid)
        try:
            data = json.loads(
                urllib.request.urlopen(userinfo_url).read().decode("utf-8"))
            userinfo_data = dict(
                openid=data["openid"],
                nickname=re.compile(u'[\U00010000-\U0010ffff]').sub(u'',data["nickname"]),#过滤掉Emoji，否则数据库报错
                sex=data["sex"],
                province=data["province"],
                city=data["city"],
                country=data["country"],
                headimgurl=data["headimgurl"],
                unionid=data["unionid"]
            )
            print(userinfo_data)
        except Exception as e:
            Logger.warn("Oauth2 Error", "获取用户信息失败")
            traceback.print_exc()
            return None

        return userinfo_data


    @classmethod
    def get_access_token_openid(cls, code, mode):  # access_token接口调用有次数上限，最好全局变量缓存
                                                   #这是需要用户授权才能获取的access_token
        # 需要改成异步请求
        if mode == "kf": # 从PC来的登录请求
            token_url = cls.__token_url.format(
                code=code, appid=KF_APPID, appsecret=KF_APPSECRET)
        else :
            token_url = cls.__token_url.format(
                code=code, appid=MP_APPID, appsecret=MP_APPSECRET)
        # 获取access_token
        try:
            data = json.loads(urllib.request.urlopen(token_url).read().decode("utf-8"))
            print(data)
        except Exception as e:
            Logger.warn("WxOauth2 Error", "获取access_token失败，注意是否存在攻击")
            traceback.print_exc()
            return None
        if "access_token" not in data:
            return None
        return (data["access_token"], data["openid"])

    @classmethod
    def get_jsapi_ticket(cls):
        global jsapi_ticket
        if datetime.datetime.now().timestamp() - jsapi_ticket["create_timestamp"]\
                < 7100 and jsapi_ticket["jsapi_ticket"]:  # jsapi_ticket过期时间为7200s，但为了保险起见7100s刷新一次
            return jsapi_ticket["jsapi_ticket"]
        access_token = cls.get_client_access_token()
        if not access_token:
            return None
        jsapi_ticket_url = cls.__jsapi_ticket_url.format(access_token=access_token)

        data = json.loads(urllib.request.urlopen(jsapi_ticket_url).read().decode("utf-8"))
        if data["errcode"] == 0:
            jsapi_ticket["jsapi_ticket"] = data["ticket"]
            jsapi_ticket["create_timestamp"] = datetime.datetime.now().timestamp()
            return data["ticket"]
        else:
            print("获取jsapi_ticket出错：", data)
            return None

    @classmethod
    def get_client_access_token(cls):  # 微信接口调用所需要的access_token,不需要用户授权
        global access_token
        if datetime.datetime.now().timestamp() - access_token["create_timestamp"]\
                < 7100 and access_token["access_token"]:  # jsapi_ticket过期时间为7200s，但为了保险起见7100s刷新一次
            return access_token["access_token"]

        data = json.loads(urllib.request.urlopen(cls.__client_access_token_url).read().decode("utf-8"))
        if "access_token" in data:
            access_token["access_token"] = data["access_token"]
            access_token["create_timestamp"] = datetime.datetime.now().timestamp()
            return data["access_token"]
        else:
            print("获取微信接口调用的access_token出错：", data)
            return None

    @classmethod
    def post_template_msg(cls, touser, shop_name, name, phone):
        time = datetime.datetime.now().strftime('%Y-%m-%d %R')
        postdata = {
            "touser": touser,
            "template_id": "YDIcdYNMLKk3sDw_yJgpIvmcN5qz_2Uz83N7T9i5O3s",
            "url": "http://mp.weixin.qq.com/s?__biz=MzA3Mzk3NTUyNQ==&"
                   "mid=202647288&idx=1&sn=b6b46a394ae3db5dae06746e964e011b#rd",
            "topcolor": "#FF0000",
            "data": {
                "first": {"value": "您好，您所申请的店铺“%s”已经通过审核！" % shop_name, "color": "#173177"},
                "keyword1": {"value": name, "color": "#173177"},
                "keyword2": {"value": phone, "color": "#173177"},
                "keyword3": {"value": time, "color": "#173177"},
                "remark": {"value": "务必点击详情，查看使用教程！", "color": "#FF4040"}}
        }
        access_token = cls.get_client_access_token()
        res = requests.post(cls.__template_msg_url.format(access_token=access_token), data=json.dumps(postdata))
        data = json.loads(res.content.decode("utf-8"))
        if data["errcode"] != 0:
            print("店铺审核模板消息发送失败：", data)
            return False
        return True
