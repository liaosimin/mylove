__author__ = 'lsm'
import tornado.websocket
from handlers.base import GlobalBaseHandler
import json
import random

class Websocket(tornado.websocket.WebSocketHandler, GlobalBaseHandler):
    waiters = {}  # {uid:self}
    group = []  # [{uid,uid,...},{}]
    link_person = {}  # {uid:uid}
    link_group = {}  # {uid:group_index}
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
        state==0:idle, state==1:p2p, state==2:group
        msg_receive = {'type':0,'msg':'hello'}   type=0:chat, 1:change people,
        msg_send = {'type': 0, 'nickname': self.current_user.nickname, 'msg': msg_receive['msg']}
            type=0:chat, 1:keep waiting, 2:stop waiting, 3:close, 4:link, 10:error
        """
        msg_receive = json.loads(message)
        msg_send = {'type': 0, 'nickname': self.current_user.nickname, 'msg': msg_receive['msg']}
        print('info: ', msg_receive)
        if msg_receive['type'] == 0:  # chat
            if Websocket.waiters[self.current_user.id].state == 1:
                Websocket.waiters[Websocket.link_person[self.current_user.id]].write_message(json.dumps(msg_send))
                return
            elif Websocket.waiters[self.current_user.id].state == 2:
                for uid in Websocket.group[Websocket.link_group[self.current_user.id]]:
                    Websocket.waiters[uid].write_message(json.dumps(msg_send))
                return
            else:
                msg_send['type'] = 10
                msg_send['nickname'] = 'server'
                msg_send['msg'] = '请选择一个陌生人或者加入房间'

        elif msg_receive['type'] == 1:  # change people
            if self.current_user.id in Websocket.link_person.keys():  # 如果正在聊天
                id_tmp = Websocket.link_person[self.current_user.id]
                del Websocket.link_person[self.current_user.id]
                del Websocket.link_person[id_tmp]
                Websocket.waiters[self.current_user.id].state = 0
                Websocket.waiters[id_tmp].state = 0
                if self.current_user.sex == 1:
                    Websocket.waiter_male_ids.add(self.current_user.id)
                    Websocket.waiter_female_ids.add(id_tmp)
                elif self.current_user.sex == 2:
                    Websocket.waiter_female_ids.add(self.current_user.id)
                    Websocket.waiter_male_ids.add(id_tmp)
            if self.current_user.sex == 1:  # 如果空闲
                if len(Websocket.waiter_female_ids) > 0:  # 当set只有1个元素时，总会随机到同一个人
                    female_id = random.sample(Websocket.waiter_female_ids, 1)[0]  # todo 现在是随机分配，以后要加入推荐算法
                    Websocket.link_person[self.current_user.id] = female_id
                    Websocket.link_person[female_id] = self.current_user.id
                    Websocket.waiter_female_ids.remove(female_id)
                    Websocket.waiter_male_ids.remove(self.current_user.id)
                    Websocket.waiters[self.current_user.id].state = 1
                    Websocket.waiters[female_id].state = 1
                    self.send_link_msg(female_id)
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
                    self.send_link_msg(male_id)
                    msg_send['type'] = 2
                    msg_send['msg'] = "stop waiting"
                else:  # no male,so have to wait
                    msg_send['type'] = 1
                    msg_send['msg'] = "继续等待"
            else:
                pass
        print('info: id=%d ' % self.current_user.id, msg_send)
        self.write_message(json.dumps(msg_send))

    def on_close(self):
        print("WebSocket closed :",self.current_user.id)
        state = Websocket.waiters[self.current_user.id].state
        if state == 0:
            if self.current_user.sex == 1:
                Websocket.waiter_male_ids.remove(self.current_user.id)
            elif self.current_user.sex == 2:
                Websocket.waiter_female_ids.remove(self.current_user.id)
            else:
                pass
        elif state == 1:
            self.on_Pchat_close(Websocket.link_person[self.current_user.id])
        elif state == 2:  # group chat
            pass
        else:
            pass
        del Websocket.waiters[self.current_user.id]

    def on_Pchat_close(self, uid):
        del Websocket.link_person[self.current_user.id]
        del Websocket.link_person[uid]

        Websocket.waiters[self.current_user.id] = 0
        Websocket.waiters[uid].state = 0

        if Websocket.waiters[uid].current_user.sex == 1:
            Websocket.waiter_male_ids.add(uid)
        elif Websocket.waiters[uid].current_user.sex == 2:
            Websocket.waiter_female_ids.add(uid)
        else:
            pass
        self.send_close_msg(uid)

    def send_close_msg(self, uid):
        msg_send = {'type': 3, 'nickname': self.current_user.nickname, 'msg': "聊天结束"}
        Websocket.waiters[uid].write_message(json.dumps(msg_send))

    def send_link_msg(self, uid):
        msg_send = {'type': 4, 'nickname': self.current_user.nickname, 'msg': "新聊天开始"}
        Websocket.waiters[uid].write_message(json.dumps(msg_send))