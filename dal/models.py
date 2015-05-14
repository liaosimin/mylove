from sqlalchemy import create_engine, func, ForeignKey, Column
from sqlalchemy.types import String, Integer, Boolean, Float, Date, BigInteger, DateTime, Time, SMALLINT
from sqlalchemy.orm import relationship, backref
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.dialects.mysql import TINYINT

from dal.db_configs import MapBase, DBSession
import json
import time
import datetime


class _CommonApi:

    @classmethod
    def get_by_id(cls, session, id):
        s = session
        try:
            u = s.query(cls).filter_by(id=id).one()
        except:
            u = None
        return u


class User(MapBase, _CommonApi):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, nullable=False)
    create_datetime = Column(DateTime, default=func.now())
    code = Column(Integer, unique=True, nullable=False)

    # 账户访问信息 (phone/email, password)/(wx_unionid)用来登录
    phone = Column(String(32), unique=True, default=None)
    email = Column(String(64), unique=True, default=None)
    password = Column(String(128), default=None)
    wx_unionid = Column(String(64), unique=True)

    # 基本账户信息
    avatar_url = Column(String(512))  # 头像url
    nickname = Column(String(20))  # 昵称
    realname = Column(String(10))  # 真实姓名
    sex = Column(TINYINT, default=2)  # 性别，男1, 女2, 其他0
    birthday = Column(Date)  # 生日
    height = Column(SMALLINT)
    weight = Column(SMALLINT)

    intro = Column(String(512))

    university_id = Column(Integer, ForeignKey('university.id'))
    grade = Column(SMALLINT)  # 年级,11：大一,12：大二,13：大三,14：大四,21:研一,22:研二,23:研三,30:研三以上
    # 微信数据
    wx_openid = Column(String(64))
    wx_username = Column(String(64))
    wx_country = Column(String(32))
    wx_province = Column(String(32))
    wx_city = Column(String(32))

    university = relationship("University", uselist=False)

    @property
    def sex_name(self):
        if self.sex == 1:
            return '男'
        elif self.sex == 2:
            return '女'
        else:
            return None

    @property
    def grade_name(self):
        if self.grade == 11:
            return '大一'
        elif self.grade == 12:
            return '大二'
        elif self.grade == 13:
            return '大三'
        elif self.grade == 14:
            return '大四'
        elif self.grade == 21:
            return '研一'
        elif self.grade == 22:
            return '研二'
        elif self.grade == 23:
            return '研三'
        elif self.grade == 30:
            return '研三以上'
        else:
            return None


class Province(MapBase):
    __tablename__ = "_province"

    code = Column(Integer, primary_key=True, nullable=False)
    name = Column(String(10))


class City(MapBase):
    __tablename__ = "_city"

    code = Column(Integer, primary_key=True, nullable=False)
    name = Column(String(20))


class University(MapBase):
    __tablename__ = "university"

    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    name = Column(String(50))
    city_code = Column(Integer,  ForeignKey(City.code))

class Photo(MapBase):
    __tablename__ = "photo"

    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    img_url = Column(String(512))
    intro = Column(String(128))
    create_datetime = Column(DateTime, default=func.now())
    author_id = Column(Integer, ForeignKey(User.id), nullable=False)

    author = relationship("User", uselist=False)

def init_db_data():
    MapBase.metadata.create_all()

    s = DBSession()
    if s.query(Province).count() == 0:
        from utils.dis_dict import dis_dict
        for (prov_code, prov) in dis_dict.items():
            s.add(Province(code=prov_code, name=prov["name"]))
            if 'city' in prov.keys():
                for (city_code, city) in prov["city"].items():
                    s.add(City(code=city_code, name=city["name"]))

            else:
                s.add(City(code=prov_code, name=prov["name"]))
        s.commit()

    if s.query(University).count() == 0:
        from utils.university import universities
        for university in universities:
            cities = s.query(City).filter_by(name=university[1]).all()
            if len(cities) == 1:
                s.add(University(name=university[0], city_code=cities[0].code))
            elif not cities:
                print("not found:", university)
            else:  # to many
                print("city duplicate", university)
        s.commit()

    print("init db success")
    return True