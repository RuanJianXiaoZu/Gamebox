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
import wave
import numpy as np
import pyaudio
from aip import AipSpeech
import re


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

    signal1 = pyqtSignal(str, int)
    signal2 = pyqtSignal()

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
        self.signal1.emit(self.name, 0)

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
        self.record = True
        self.record_thread = Thread(target=self.record_voice)
        self.record_thread.setDaemon(True)
        self.record_thread.start()
        self.client = None

    def send_name(self):
        send_msg = {'name': self.message.text()}
        send_json = json.dumps(send_msg)
        self.client.send(send_json.encode())
        self.close()

    def get_client(self, client):
        self.client = client

    def record_voice(self):
        APP_ID = '24142986'
        API_KEY = 'lz8wrZPBovwoWXqpL2FRBtDX'
        SECRET_KEY = '34kKxkbMKB8VaqWZRQxV1y4QbPNW0xkG'

        client = AipSpeech(APP_ID, API_KEY, SECRET_KEY)


        CHUNK = 1024
        FORMAT = pyaudio.paInt16  # 16bit编码格式
        CHANNELS = 1  # 单声道
        RATE = 16000  # 16000采样频率

        while True:
            if self.record == True:
                p = pyaudio.PyAudio()
                # 创建音频流
                stream = p.open(format=FORMAT,  # 音频流wav格式
                                channels=CHANNELS,  # 单声道
                                rate=RATE,  # 采样率16000
                                input=True,
                                frames_per_buffer=CHUNK)
                print("Start Recording...")
                frames = []  # 录制的音频流
                # 录制音频数据
                while True:
                    # print("begin")
                    for i in range(0, 2):
                        data1 = stream.read(CHUNK)
                        frames.append(data1)
                    audio_data1 = np.fromstring(data1, dtype=np.short)
                    temp1 = np.max(audio_data1)
                    if temp1 > 550:
                        # print("检测到信号")
                        # print('当前阈值：', temp1)
                        less = 0
                        while True:
                            # print("recording")
                            for i in range(0, 5):
                                data2 = stream.read(CHUNK)
                                frames.append(data2)
                            audio_data2 = np.fromstring(data2, dtype=np.short)
                            temp2 = np.max(audio_data2)
                            if temp2 < 550:
                                less = less + 1
                                # print("below threshold, counting: ", less, '当前阈值：', temp2)
                                # 如果有连续15个循环的点，都不是声音信号，就认为音频结束了
                                if less == 2:
                                    break
                            else:
                                less = 0
                                # print('当前阈值：', temp2)
                        break
                    else:
                        frames = []
                # 录制完成
                stream.stop_stream()
                stream.close()
                p.terminate()
                print("Recording Done...")
                # 保存音频文件
                with wave.open("./1.wav", 'wb') as wf:
                    wf.setnchannels(CHANNELS)
                    wf.setsampwidth(p.get_sample_size(FORMAT))
                    wf.setframerate(RATE)
                    wf.writeframes(b''.join(frames))
                    wf.close()
                result = client.asr(self.get_file_content('1.wav'), 'wav', 16000, {'dev_pid': 1537,})
                if result.__contains__('result') == False:
                    continue
                elif result.__contains__('result') == True:
                    result = ''.join(result["result"])
                    print(result)
                    if result == '关闭。':
                        self.close()
                        self.record = False
                    elif result == '确认。':
                        self.send_name()
                        self.record = False
                    elif result == '我知道。' or result == '我不知道。' or result == '不知道。':
                        continue
                    elif len(result) > 0:
                        punctuation = '~`!#$%^&*()_+-=|\';":/.,?><~·！@#￥%……&*（）——+-=“：’；、。，？》《{}'
                        self.message.setText(re.sub(r"[%s]+" %punctuation, "",result))
            else:
                break

    def get_file_content(self, file_path):
        with open(file_path, 'rb') as fp:
            return fp.read()


class Client(QWidget):

    signal1 = pyqtSignal(str)
    signal2 = pyqtSignal(str, int)
    signal3 = pyqtSignal(list)
    signal4 = pyqtSignal()
    signal5 = pyqtSignal(int, str)
    signal6 = pyqtSignal(str)
    signal7 = pyqtSignal(list, list)
    signal8 = pyqtSignal()
    signal9 = pyqtSignal()

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
        self.invitation = Invitation(self.client)
        self.invitation.signal1.connect(self.startgame)
        self.invitation.signal2.connect(self.changerecord)
        self.name = None
        self.reservation = Reservation(self.client)
        self.signal8.connect(self.reservation.accept)
        self.signal9.connect(self.reservation.refuse)
        self.game = game.ChineseChess()
        self.signal3.connect(self.game.recvrecord)
        self.signal4.connect(self.game.quit)
        self.signal7.connect(self.game.recvmouse)
        self.record = 0
        self.record_thread = Thread(target=self.record_voice)
        self.record_thread.setDaemon(True)
        self.record_thread.start()

    def record_voice(self):
        APP_ID = '24142986'
        API_KEY = 'lz8wrZPBovwoWXqpL2FRBtDX'
        SECRET_KEY = '34kKxkbMKB8VaqWZRQxV1y4QbPNW0xkG'

        client = AipSpeech(APP_ID, API_KEY, SECRET_KEY)


        CHUNK = 1024
        FORMAT = pyaudio.paInt16  # 16bit编码格式
        CHANNELS = 1  # 单声道
        RATE = 16000  # 16000采样频率

        while True:
            if self.record == 0:
                time.sleep(0.5)
            elif self.record == 5:
                break
            elif self.record == 1 or self.record == 2 or self.record == 3:
                p = pyaudio.PyAudio()
                # 创建音频流
                stream = p.open(format=FORMAT,  # 音频流wav格式
                                channels=CHANNELS,  # 单声道
                                rate=RATE,  # 采样率16000
                                input=True,
                                frames_per_buffer=CHUNK)
                print("Start Recording...")
                frames = []  # 录制的音频流
                # 录制音频数据
                while True:
                    # print("begin")
                    for i in range(0, 2):
                        data1 = stream.read(CHUNK)
                        frames.append(data1)
                    audio_data1 = np.fromstring(data1, dtype=np.short)
                    temp1 = np.max(audio_data1)
                    if temp1 > 550:
                        # print("检测到信号")
                        # print('当前阈值：', temp1)
                        less = 0
                        while True:
                            # print("recording")
                            for i in range(0, 5):
                                data2 = stream.read(CHUNK)
                                frames.append(data2)
                            audio_data2 = np.fromstring(data2, dtype=np.short)
                            temp2 = np.max(audio_data2)
                            if temp2 < 550:
                                less = less + 1
                                # print("below threshold, counting: ", less, '当前阈值：', temp2)
                                # 如果有连续15个循环的点，都不是声音信号，就认为音频结束了
                                if less == 2:
                                    break
                            else:
                                less = 0
                                # print('当前阈值：', temp2)
                        break
                    else:
                        frames = []
                # 录制完成
                stream.stop_stream()
                stream.close()
                p.terminate()
                print("Recording Done...")
                # 保存音频文件
                with wave.open("./1.wav", 'wb') as wf:
                    wf.setnchannels(CHANNELS)
                    wf.setsampwidth(p.get_sample_size(FORMAT))
                    wf.setframerate(RATE)
                    wf.writeframes(b''.join(frames))
                    wf.close()
                result = client.asr(self.get_file_content('1.wav'), 'wav', 16000, {'dev_pid': 1537,})
                if result.__contains__('result') == False:
                    continue
                elif result.__contains__('result') == True:
                    result = ''.join(result["result"])
                    print(result)
                    if result == '关闭。':
                        self.exit_program()
                    elif result == '我知道。' or result == '我不知道。' or result == '不知道。':
                        continue
                    elif self.record == 1 and len(result) > 0:
                        punctuation = '~`!#$%^&*()_+-=|\';":/.,?><~·！@#￥%……&*（）——+-=“：’；、。，？》《{}'
                        for user in self.users:
                            if user['name'] == re.sub(r"[%s]+" %punctuation, "",result):
                                if user['status'] == '空闲':
                                    send_msg = {'type': 'invitation', 'name': user['name']}
                                    send_json = json.dumps(send_msg)
                                    self.client.send(send_json.encode())
                                    self.signal5.emit(5, user['name'])
                                    break
                                elif user['status'] == '游戏中':
                                    send_msg = {'type': 'reservation', 'name': user['name']}
                                    send_json = json.dumps(send_msg)
                                    self.client.send(send_json.encode())
                                    self.signal5.emit(6, user['name'])
                                    break
                    elif self.record == 2 and len(result) > 0:
                        if result == '接受。':
                            self.invitation.accept()
                        elif result == '拒绝。':
                            self.invitation.refuse()
                    elif self.record == 3 and len(result) > 0:
                        if result == "结束。":
                            self.game.postevent(2)
                            self.record = 1
                        elif result == '接受。':
                            self.signal8.emit()
                        elif result == '拒绝。':
                            self.signal9.emit()
                        elif self.game.who_go % 2 == 1 and len(result) > 4:
                            if result[0] == "车":
                                self.game.record[0] = 1
                            elif result[0] == "马":
                                self.game.record[0] = 2
                            elif result[0] == "象" or result[0] == "相":
                                self.game.record[0] = 3
                            elif result[0] == "士" or result[0] == "仕":
                                self.game.record[0] = 4
                            elif result[0] == "帅" or result[0] == "将":
                                self.game.record[0] = 5
                            elif result[0] == "炮":
                                self.game.record[0] = 6
                            elif result[0] == "兵" or result[0] == "卒":
                                self.game.record[0] = 7
                            elif result[0] == "前":
                                self.game.record[1] = 10
                            elif result[0] == "后":
                                self.game.record[1] = 11
                            if result[1] == "一":
                                self.game.record[1] = 1
                            elif result[1] == "二":
                                self.game.record[1] = 2
                            elif result[1] == "三":
                                self.game.record[1] = 3
                            elif result[1] == "四":
                                self.game.record[1] = 4
                            elif result[1] == "五":
                                self.game.record[1] = 5
                            elif result[1] == "六":
                                self.game.record[1] = 6
                            elif result[1] == "七":
                                self.game.record[1] = 7
                            elif result[1] == "八":
                                self.game.record[1] = 8
                            elif result[1] == "九":
                                self.game.record[1] = 9
                            elif result[1] == "车":
                                self.game.record[0] = 1
                            elif result[1] == "马":
                                self.game.record[0] = 2
                            elif result[1] == "象" or result[1] == "相":
                                self.game.record[0] = 3
                            elif result[1] == "士" or result[1] == "仕":
                                self.game.record[0] = 4
                            elif result[1] == "炮":
                                self.game.record[0] = 6
                            elif result[1] == "兵" or result[1] == "卒":
                                self.game.record[0] = 7
                            if result[2] == "进":
                                self.game.record[2] = 1
                            elif result[2] == "退":
                                self.game.record[2] = 2
                            elif result[2] == "平":
                                self.game.record[2] = 3
                            if result[3] == "一":
                                self.game.record[3] = 1
                            elif result[3] == "二":
                                self.game.record[3] = 2
                            elif result[3] == "三":
                                self.game.record[3] = 3
                            elif result[3] == "四":
                                self.game.record[3] = 4
                            elif result[3] == "五":
                                self.game.record[3] = 5
                            elif result[3] == "六":
                                self.game.record[3] = 6
                            elif result[3] == "七":
                                self.game.record[3] = 7
                            elif result[3] == "八":
                                self.game.record[3] = 8
                            elif result[3] == "九":
                                self.game.record[3] = 9
                            if self.game.record[0] == 0 or self.game.record[1] == 0 or self.game.record[2] == 0 or self.game.record[3] == 0:
                                self.game.record = [0, 0, 0, 0]
                                print("语音指令错误！")
                            else:
                                self.game.postevent(1)

    def get_file_content(self, file_path):
        with open(file_path, 'rb') as fp:
            return fp.read()

    def reserve_user(self, qModelIndex):
        i = 0
        for user in self.users:
            if user['status'] == '游戏中':
                if i == qModelIndex.row():
                    send_msg = {'type': 'reservation', 'name': user['name']}
                    send_json = json.dumps(send_msg)
                    self.client.send(send_json.encode())
                    self.signal5.emit(6, user['name'])
                    break
                i = i + 1

    def message(self, type, name):
        infoBox = QMessageBox()
        infoBox.setIcon(QMessageBox.Information)
        if type == 1:
            infoBox.setText("您的对手已逃跑，对弈结束。")
        elif type == 2:
            infoBox.setText("预约成功。")
        elif type == 3:
            infoBox.setText("预约失败。")
        elif type == 4:
            infoBox.setText("对方拒绝了您的邀请")
        elif type == 5:
            infoBox.setText("向用户" + name + "发起对弈邀请。")
        elif type == 6:
            infoBox.setText("向用户" + name + "发起预约。")
        infoBox.setWindowTitle("Information")
        infoBox.setStandardButtons(QMessageBox.Ok)
        infoBox.button(QMessageBox.Ok).animateClick(1500)
        infoBox.exec_()

    def startgame(self, name, side):
        if side == 0:
            self.invitation.close()
        self.record = 3
        self.name = name
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
                    self.record = 1
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
                    self.record = 2
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
                    self.record = 3
                    self.signal2.emit(self.name, 1)
                elif recv_msg['type'] == 'refuse':
                    self.signal5.emit(4, '')
                elif recv_msg['type'] == 'sendrecord':
                    self.signal3.emit(recv_msg['record'])
                elif recv_msg['type'] == 'sendmouse':
                    self.signal7.emit(recv_msg['mouse1'], recv_msg['mouse2'])
                elif recv_msg['type'] == 'quit':
                    self.signal4.emit()
                    self.signal5.emit(1, '')
                    self.record = 1
                elif recv_msg['type'] == 'reservation':
                    self.signal6.emit(recv_msg['name'])
                elif recv_msg['type'] == 'success':
                    self.signal5.emit(2, '')
                elif recv_msg['type'] == 'fail':
                    self.signal5.emit(3, '')
                elif recv_msg['type'] == 'changerecordstatus':
                    self.record = 1
            except:
                exit()

    def show_reservation(self, name):
        self.reservation.get_name(name)
        self.reservation.show()
    
    def show_invitation(self, name):
        self.invitation.get_name(name)
        self.invitation.show()

    def changerecord(self):
        self.record = 1

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
                    self.signal5.emit(5, user['name'])
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