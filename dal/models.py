from sqlalchemy import create_engine, func, ForeignKey, Column
from sqlalchemy.types import String, Integer, Boolean, Float, Date, BigInteger, DateTime, Time, SMALLINT
from sqlalchemy.orm import relationship, backref
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.dialects.mysql import TINYINT

from dal.db_configs import MapBase, DBSession
from dal.dis_dict import dis_dict
import json
import time
import datetime


class User(MapBase):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, nullable=False)
    create_date = Column(DateTime, nullable=False)

    # 账户访问信息 (phone/email, password)/(wx_unionid)用来登录
    phone = Column(String(32), unique=True, default=None)
    email = Column(String(64), default=None)
    password = Column(String(128), default=None)
    wx_unionid = Column(String(64), unique=True)

    # 基本账户信息

    # 性别，男1, 女2, 其他0
    sex = Column(TINYINT, default=0)
    # 昵称
    nickname = Column(String(20))
    # 真实姓名
    realname = Column(String(10))
    # 头像url
    headimgurl = Column(String(512))
    # 生日
    birthday = Column(Date)
    # 微信数据
    wx_openid = Column(String(64))
    wx_username = Column(String(64))
    wx_country = Column(String(32))
    wx_province = Column(String(32))
    wx_city = Column(String(32))