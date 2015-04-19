__author__ = 'lsm'
import tornado.websocket
from handlers.base import GlobalBaseHandler
import json
import random

class Websocket(tornado.websocket.WebSocketHandler, GlobalBaseHandler):
    waiters = {}  # {uid:self}
    group = []
    link_person = {}  # {uid:uid}
    link_group = {}  # {}
    waiter_male_ids = set()
    waiter_female_ids = set()

    def open(self):
        Websocket.waiters[self.current_user.id] = self
        self.state = 0
        if self.current_user.sex == 1:  # male
            Websocket.waiter_male_ids.add(self.current_user.id)
        else:  # female or other
            Websocket.waiter_female_ids.add(self.current_user.id)
        print("WebSocket opened:"+str(self.current_user.id))

    def on_message(self, message):
        """
        msg_receive = {'type':0,'msg':'hello'}   type=0:chat, 1:change people,
        msg_send = {'type': 0, 'nickname': self.current_user.nickname, 'msg': msg_receive['msg']}
            type=0:chat,1:keep waiting,2:stop waiting
        """
        msg_receive = json.loads(message)
        msg_send = {'type': 0, 'nickname': self.current_user.nickname, 'msg': msg_receive['msg']}
        if msg_receive['type'] == 0:
            if Websocket.waiters[self.current_user.id].state == 1:
                Websocket.waiters[Websocket.link_person[self.current_user.id]].write_message(json.dumps(msg_send))
                return
            elif Websocket.waiters[self.current_user.id].state == 2:
                for uid in Websocket.group[Websocket.link_group[self.current_user.id]]:
                    Websocket.waiters[uid].write_message(json.dumps(msg_send))
                return
            else:
                msg_send['type'] = 1
                msg_send['msg'] = '请选择一个陌生人或者加入房间'

        elif msg_receive['type'] == 1:  # change people
            if self.current_user.id in Websocket.link_person.keys():
                id_tmp = Websocket.link_person[self.current_user.id]
                del Websocket.link_person[self.current_user.id]
                del Websocket.link_person[id_tmp]
                Websocket.waiters[self.current_user.id].state = 0
                Websocket.waiters[id_tmp].state = 0
                if self.current_user.sex == 1:
                    Websocket.waiter_male_ids.add(self.current_user.id)
                elif self.current_user.sex == 2:
                    Websocket.waiter_female_ids.add(self.current_user.id)
            if self.current_user.sex == 1:
                if len(Websocket.waiter_female_ids) > 0:  # 当set只有1个元素时，总会随机到同一个人
                    female_id = random.sample(Websocket.waiter_female_ids, 1)[0]  # todo 现在是随机分配，以后要加入推荐算法
                    Websocket.link_person[self.current_user.id] = female_id
                    Websocket.link_person[female_id] = self.current_user.id
                    Websocket.waiter_female_ids.remove(female_id)
                    Websocket.waiter_male_ids.remove(self.current_user.id)
                    Websocket.waiters[self.current_user.id].state = 1
                    Websocket.waiters[female_id].state = 1
                    msg_send['type'] = 2
                    msg_send['msg'] = "stop waiting"
                else:  # no female,so have to wait
                    msg_send['type'] = 1
                    msg_send['msg'] = "继续等待"
            elif self.current_user.sex == 2:
                if len(Websocket.waiter_male_ids) > 0:
                    male_id = random.sample(Websocket.waiter_male_ids, 1)[0]  # todo 现在是随机分配，以后要加入推荐算法
                    Websocket.link_person[self.current_user.id] = male_id
                    Websocket.link_person[male_id] = self.current_user.id
                    Websocket.waiter_male_ids.remove(male_id)
                    Websocket.waiter_female_ids.remove(self.current_user.id)
                    Websocket.waiters[self.current_user.id].state = 1
                    Websocket.waiters[male_id].state = 1
                    msg_send['type'] = 2
                    msg_send['msg'] = "stop waiting"
                else:  # no male,so have to wait
                    msg_send['type'] = 1
                    msg_send['msg'] = "继续等待"
            else:
                pass
        self.write_message(json.dumps(msg_send))





    def on_close(self):
        print("WebSocket closed")