__author__ = 'lsm'
from handlers.base import UserBaseHandler
from settings import *
import dal.models as models
import qiniu
from qiniu.services.storage.bucket import BucketManager


class QiniuCallback(UserBaseHandler):

    def post(self):
        key = self.get_argument("key")
        id = int(self.get_argument("id"))
        bucket = self.get_argument("bucket")


        if bucket == "senguoimg":
            try:
                user = self.session.query(models.User).filter_by(id=id).one()
            except:
                return self.send_error(404)
            avatar_url = user.avatar_url
            user.avatar_url = key
            if avatar_url:  # 先要把旧的的图片删除
                m = BucketManager(auth=qiniu.Auth(ACCESS_KEY, SECRET_KEY))
                m.delete(bucket=bucket, key=avatar_url)
            return self.send_success()
        return self.send_error(404)


    def check_xsrf_cookie(self):  #必须要复写tornado自带的检查_xsrf 参数，否则回调不成功
        pass
        return