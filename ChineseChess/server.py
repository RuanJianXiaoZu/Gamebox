import socket
from threading import Thread
import json


class Server:

    def __init__(self):
        self.server = socket.socket()
        self.server.bind(("192.168.43.197", 8989))
        self.server.listen(10)
        self.client_dicts = []
        self.user_dicts = []
        self.get_conn()

    def get_conn(self):
        while True:
            client, address = self.server.accept()
            Thread(target=self.get_msg, args=(client, address)).start()

    def get_msg(self, client, address):
        recv_json = client.recv(1024).decode()
        recv_msg = json.loads(recv_json)
        user_dict = {'address': address, 'name': recv_msg['name'], 'status': '空闲'}
        client_dict = {'client': client, 'address': address, 'name': recv_msg['name']}
        send_msg = {'type': 'userlist', 'userlist': self.user_dicts}
        send_json = json.dumps(send_msg)
        client.send(send_json.encode())
        self.client_dicts.append(client_dict)
        self.user_dicts.append(user_dict)
        send_msg = {'type': 'adduser', 'user': user_dict}
        send_json = json.dumps(send_msg)
        for d in self.client_dicts:
            if d == client_dict:
                continue
            d['client'].send(send_json.encode())
        while True:
            try:
                recv_json = client.recv(1024).decode()
            except Exception as e:
                self.close_client(client_dict, user_dict)
                break
            
            recv_msg = json.loads(recv_json)
            if recv_msg['type'] == 'removeuser':
                self.close_client(client_dict, user_dict)
                break
            elif recv_msg['type'] == 'invitation':
                for d in self.client_dicts:
                    if d['name'] == recv_msg['name']:
                        send_msg = {'type': 'invitation', 'name': user_dict['name']}
                        send_json = json.dumps(send_msg)
                        d['client'].send(send_json.encode())
                        break
            elif recv_msg['type'] == 'accept':
                send_json1 = None
                send_json2 = None
                send_msg = {'type': 'accept', 'name': user_dict['name']}
                send_json = json.dumps(send_msg)
                for i, u in enumerate(self.user_dicts):
                    if u['name'] == recv_msg['name']:
                        self.user_dicts[i]['status'] = '游戏中'
                        send_msg = {'type': 'statuschange', 'user': self.user_dicts[i]}
                        send_json1 = json.dumps(send_msg)
                    if u['name'] == user_dict['name']:
                        self.user_dicts[i]['status'] = '游戏中'
                        send_msg = {'type': 'statuschange', 'user': self.user_dicts[i]}
                        send_json2 = json.dumps(send_msg)
                for d in self.client_dicts:
                    if d['name'] == recv_msg['name']:
                        d['client'].send(send_json.encode())
                        d['client'].send(send_json2.encode())
                        continue
                    if d == client_dict:
                        d['client'].send(send_json1.encode())
                        continue
                    d['client'].send(send_json1.encode())
                    d['client'].send(send_json2.encode())
            elif recv_msg['type'] == 'refuse':
                for d in self.client_dicts:
                    if d['name'] == recv_msg['name']:
                        d['client'].send(recv_json.encode())
                        break
            elif recv_msg['type'] == 'sendrecord':
                for d in self.client_dicts:
                    if d['name'] == recv_msg['name']:
                        d['client'].send(recv_json.encode())
                        break
            elif recv_msg['type'] == 'sendmouse':
                for d in self.client_dicts:
                    if d['name'] == recv_msg['name']:
                        d['client'].send(recv_json.encode())
                        break
            elif recv_msg['type'] == 'quit':
                if user_dict['status'] == '空闲':
                    continue
                send_json1 = None
                send_json2 = None
                send_msg = {'type': 'quit', 'name': user_dict['name']}
                send_json = json.dumps(send_msg)
                for i, u in enumerate(self.user_dicts):
                    if u['name'] == recv_msg['name']:
                        self.user_dicts[i]['status'] = '空闲'
                        send_msg = {'type': 'statuschange', 'user': self.user_dicts[i]}
                        send_json1 = json.dumps(send_msg)
                    if u['name'] == user_dict['name']:
                        self.user_dicts[i]['status'] = '空闲'
                        send_msg = {'type': 'statuschange', 'user': self.user_dicts[i]}
                        send_json2 = json.dumps(send_msg)
                for d in self.client_dicts:
                    if d['name'] == recv_msg['name']:
                        d['client'].send(send_json.encode())
                        d['client'].send(send_json2.encode())
                        continue
                    if d == client_dict:
                        d['client'].send(send_json1.encode())
                        continue
                    d['client'].send(send_json1.encode())
                    d['client'].send(send_json2.encode())
            elif recv_msg['type'] == 'reservation':
                for d in self.client_dicts:
                    if d['name'] == recv_msg['name']:
                        send_msg = {'type': 'reservation', 'name': user_dict['name']}
                        send_json = json.dumps(send_msg)
                        d['client'].send(send_json.encode())
                        break
            elif recv_msg['type'] == 'success':
                for d in self.client_dicts:
                    if d['name'] == recv_msg['name']:
                        d['client'].send(recv_json.encode())
                        break
            elif recv_msg['type'] == 'fail':
                for d in self.client_dicts:
                    if d['name'] == recv_msg['name']:
                        d['client'].send(recv_json.encode())
                        break

    def close_client(self, client_dict, user_dict):
        self.client_dicts.remove(client_dict)
        self.user_dicts.remove(user_dict)
        client_dict['client'].close()
        send_msg = {'type': 'removeuser', 'user': user_dict}
        send_json = json.dumps(send_msg)
        for d in self.client_dicts:
            d['client'].send(send_json.encode())


if __name__ == '__main__':
    Server()