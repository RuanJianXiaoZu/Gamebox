import socket
import json
import sys
from threading import Thread
from PyQt5 import QtGui
from PyQt5 import QtCore
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import game
import time


class Reservation(QWidget):

    def __init__(self, client):
        QWidget.__init__(self)
        self.setGeometry(600, 500, 400, 90)
        self.setWindowTitle("reservation")
        self.label = QLabel(self)
        self.label.setGeometry(30, 30, 200, 30)
        self.send_button1 = QPushButton("接受", self)
        self.send_button1.setFont(QFont("微软雅黑", 10))
        self.send_button1.setGeometry(230, 30, 70, 30)
        self.send_button1.clicked.connect(self.accept)
        self.send_button2 = QPushButton("拒绝", self)
        self.send_button2.setFont(QFont("微软雅黑", 10))
        self.send_button2.setGeometry(315, 30, 70, 30)
        self.send_button2.clicked.connect(self.refuse)
        self.client = client
        self.name = None

    def get_name(self, name):
        self.name = name
        self.label.setText('用户' + name + '向您发起预约')

    def accept(self):
        send_msg = {'type': 'success', 'name': self.name}
        send_json = json.dumps(send_msg)
        self.client.send(send_json.encode())
        self.close()

    def refuse(self):
        send_msg = {'type': 'fail', 'name': self.name}
        send_json = json.dumps(send_msg)
        self.client.send(send_json.encode())
        self.close()


class Invitation(QWidget):

    signal = pyqtSignal(str, int)

    def __init__(self, client):
        QWidget.__init__(self)
        self.setGeometry(600, 500, 400, 90)
        self.setWindowTitle("Invitation")
        self.label = QLabel(self)
        self.label.setGeometry(30, 30, 200, 30)
        self.send_button1 = QPushButton("接受", self)
        self.send_button1.setFont(QFont("微软雅黑", 10))
        self.send_button1.setGeometry(230, 30, 70, 30)
        self.send_button1.clicked.connect(self.accept)
        self.send_button2 = QPushButton("拒绝", self)
        self.send_button2.setFont(QFont("微软雅黑", 10))
        self.send_button2.setGeometry(315, 30, 70, 30)
        self.send_button2.clicked.connect(self.refuse)
        self.client = client
        self.name = None

    def get_name(self, name):
        self.name = name
        self.label.setText('用户' + name + '邀请您进行象棋对弈')

    def accept(self):
        send_msg = {'type': 'accept', 'name': self.name}
        send_json = json.dumps(send_msg)
        self.client.send(send_json.encode())
        self.signal.emit(self.name, 0)

    def refuse(self):
        send_msg = {'type': 'refuse', 'name': self.name}
        send_json = json.dumps(send_msg)
        self.client.send(send_json.encode())
        self.close()


class Getname(QWidget):

    def __init__(self):
        QWidget.__init__(self)
        self.setGeometry(600, 500, 400, 90)
        self.setWindowTitle("Get Name")
        self.message = QLineEdit(self)
        self.message.setPlaceholderText(u"输入您的id获取用户列表")
        self.message.setGeometry(30, 30, 240, 30)
        self.send_button = QPushButton("确认", self)
        self.send_button.setFont(QFont("微软雅黑", 10))
        self.send_button.setGeometry(300, 30, 70, 30)
        self.send_button.clicked.connect(self.send_name)
        self.client = None

    def send_name(self):
        send_msg = {'name': self.message.text()}
        send_json = json.dumps(send_msg)
        self.client.send(send_json.encode())
        self.close()

    def get_client(self, client):
        self.client = client


class Client(QWidget):

    signal1 = pyqtSignal(str)
    signal2 = pyqtSignal(str, int)
    signal3 = pyqtSignal(list)
    signal4 = pyqtSignal()
    signal5 = pyqtSignal(int)
    signal6 = pyqtSignal(str)
    signal7 = pyqtSignal(list, list)

    def __init__(self):
        QWidget.__init__(self)
        self.users = []
        self.setGeometry(600, 300, 400, 600)
        self.setWindowTitle("Chinese Chess")
        palette = QtGui.QPalette()
        bg = QtGui.QPixmap(r"background1.jpg")
        palette.setBrush(self.backgroundRole(), QtGui.QBrush(bg))
        self.setPalette(palette)
        self.label1 = QLabel(self)
        self.label1.setGeometry(30, 5, 200, 30)
        self.label1.setText('空闲用户列表：')
        self.label1.setStyleSheet("color:gold")
        self.label2 = QLabel(self)
        self.label2.setGeometry(30, 280, 200, 30)
        self.label2.setText('游戏中用户列表：')
        self.label2.setStyleSheet("color:gold")
        self.free_userlist = QStringListModel()
        self.list1 = QListView(self)
        self.list1.setModel(self.free_userlist)
        self.list1.setGeometry(30, 35, 340, 240)
        self.gaming_userlist = QStringListModel()
        self.list2 = QListView(self)
        self.list2.setModel(self.gaming_userlist)
        self.list2.setGeometry(30, 310, 340, 240)
        self.exit_button = QPushButton("退出", self)
        self.exit_button.setFont(QFont("微软雅黑", 10))
        self.exit_button.setGeometry(300, 560, 70, 30)
        self.exit_button.clicked.connect(self.exit_program)
        self.client = socket.socket()
        self.client.connect(("127.0.0.1", 8989))
        self.list1.clicked.connect(self.choose_user)
        self.list2.clicked.connect(self.reserve_user)
        Thread(target=self.get_msg).start()
        self.signal1.connect(self.show_invitation)
        self.signal2.connect(self.startgame)
        self.signal5.connect(self.message)
        self.signal6.connect(self.show_reservation)
        self.invitation = None
        self.name = None
        self.game = None
        self.reservation = None


    def reserve_user(self, qModelIndex):
        i = 0
        for user in self.users:
            if user['status'] == '游戏中':
                if i == qModelIndex.row():
                    send_msg = {'type': 'reservation', 'name': user['name']}
                    send_json = json.dumps(send_msg)
                    self.client.send(send_json.encode())
                    break
                i = i + 1
        QMessageBox.information(self, "消息", "向用户" + user['name'] + "发起预约。")

    def message(self, type):
        if type == 1:
            QMessageBox.information(self, "消息", "您的对手已逃跑。")
        elif type ==2:
            QMessageBox.information(self, "消息", "预约成功。")
        elif type ==3:
            QMessageBox.information(self, "消息", "预约失败。")

    def startgame(self, name, side):
        if side == 0:
            self.invitation.close()
        self.name = name
        self.game = game.ChineseChess()
        self.signal3.connect(self.game.recvrecord)
        self.signal4.connect(self.game.quit)
        self.signal7.connect(self.game.recvmouse)
        self.game.show(name, self.client, side)

    def get_msg(self):
        while True:
            try:
                recv_json = self.client.recv(1024).decode()
                recv_msg = json.loads(recv_json)
                print(recv_msg)
                if recv_msg['type'] == 'userlist':
                    self.users = recv_msg['userlist']
                    free_list = []
                    gaming_list = []
                    for user in self.users:
                        if user['status'] == '空闲':
                            free_list.append(user['name'])
                        elif user['status'] == '游戏中':
                            gaming_list.append(user['name'])
                    self.free_userlist.setStringList(free_list)
                    self.gaming_userlist.setStringList(gaming_list)
                elif recv_msg['type'] == 'adduser':
                    self.users.append(recv_msg['user'])
                    free_list = []
                    gaming_list = []
                    for user in self.users:
                        if user['status'] == '空闲':
                            free_list.append(user['name'])
                        elif user['status'] == '游戏中':
                            gaming_list.append(user['name'])
                    self.free_userlist.setStringList(free_list)
                    self.gaming_userlist.setStringList(gaming_list)
                elif recv_msg['type'] == 'removeuser':
                    self.users.remove(recv_msg['user'])
                    free_list = []
                    gaming_list = []
                    for user in self.users:
                        if user['status'] == '空闲':
                            free_list.append(user['name'])
                        elif user['status'] == '游戏中':
                            gaming_list.append(user['name'])
                    self.free_userlist.setStringList(free_list)
                    self.gaming_userlist.setStringList(gaming_list)
                elif recv_msg['type'] == 'invitation':
                    self.signal1.emit(recv_msg['name'])
                elif recv_msg['type'] == 'statuschange':
                    for i, user in enumerate(self.users):
                        if user['name'] ==  recv_msg['user']['name']:
                            self.users[i] = recv_msg['user']
                            break
                    free_list = []
                    gaming_list = []
                    for user in self.users:
                        if user['status'] == '空闲':
                            free_list.append(user['name'])
                        elif user['status'] == '游戏中':
                            gaming_list.append(user['name'])
                    self.free_userlist.setStringList(free_list)
                    self.gaming_userlist.setStringList(gaming_list)
                elif recv_msg['type'] == 'accept':
                    self.name = recv_msg['name']
                    self.signal2.emit(self.name, 1)
                elif recv_msg['type'] == 'sendrecord':
                    self.signal3.emit(recv_msg['record'])
                elif recv_msg['type'] == 'sendmouse':
                    self.signal7.emit(recv_msg['mouse1'], recv_msg['mouse2'])
                elif recv_msg['type'] == 'quit':
                    self.signal4.emit()
                    self.signal5.emit(1)
                elif recv_msg['type'] == 'reservation':
                    self.signal6.emit(recv_msg['name'])
                elif recv_msg['type'] == 'success':
                    self.signal5.emit(2)
                elif recv_msg['type'] == 'fail':
                    self.signal5.emit(3)
            except:
                exit()

    def show_reservation(self, name):
        self.reservation = Reservation(self.client)
        self.reservation.get_name(name)
        self.reservation.show()
    
    def show_invitation(self, name):
        self.invitation = Invitation(self.client)
        self.invitation.signal.connect(self.startgame)
        self.invitation.get_name(name)
        self.invitation.show()

    def exit_program(self):
        send_msg = {'type': 'quit', 'name': self.name}
        send_json = json.dumps(send_msg)
        self.client.send(send_json.encode())
        time.sleep(0.5)
        send_msg = {'type': 'removeuser'}
        send_json = json.dumps(send_msg)
        self.client.send(send_json.encode())
        self.close()
        self.client.close()
        self.destroy()
        sys.exit()

    def choose_user(self, qModelIndex): 
        i = 0
        for user in self.users:
            if user['status'] == '空闲':
                if i == qModelIndex.row():
                    send_msg = {'type': 'invitation', 'name': user['name']}
                    send_json = json.dumps(send_msg)
                    self.client.send(send_json.encode())
                    break
                i = i + 1


if __name__ == '__main__':
    app = QApplication(sys.argv)
    client = Client()
    client.show()
    getname = Getname()
    getname.show()
    getname.get_client(client.client)
    sys.exit(app.exec()) 