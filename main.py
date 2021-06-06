import PySimpleGUI as sg
import os
import sys
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtWebEngineWidgets import *
import wave
import numpy as np
import pyaudio
from aip import AipSpeech
import time
from threading import Thread


dirname, filename = os.path.split(os.path.abspath(__file__))
os.chdir(dirname)


class WindowClass(QMainWindow):
    signal = pyqtSignal()
    def __init__(self):

        super(WindowClass, self).__init__()
        self.setWindowTitle('Game Box')

        self.widget_all = QWidget()
        self.setCentralWidget(self.widget_all)
        self.layout_all = QVBoxLayout()
        self.widget_all.setLayout(self.layout_all)

        self.label = QLabel("Welcome! Select a game below:", self)
        self.layout_all.addWidget(self.label)

        self.button_1 = QPushButton("象棋单机游戏", self)
        self.layout_all.addWidget(self.button_1)
        self.button_1.clicked.connect(self.game_1)

        self.button_2 = QPushButton("象棋联机游戏", self)
        self.layout_all.addWidget(self.button_2)
        self.button_2.clicked.connect(self.game_2)

        self.button_3 = QPushButton("连连看", self)
        self.layout_all.addWidget(self.button_3)
        self.button_3.clicked.connect(self.game_3)

        self.button_4 = QPushButton("扫雷", self)
        self.layout_all.addWidget(self.button_4)
        self.button_4.clicked.connect(self.game_4)

        self.button_5 = QPushButton("拼图", self)
        self.layout_all.addWidget(self.button_5)
        self.button_5.clicked.connect(self.game_5)

        self.button_6 = QPushButton("推箱子", self)
        self.layout_all.addWidget(self.button_6)
        self.button_6.clicked.connect(self.game_6)

        self.button_7 = QPushButton("五子棋", self)
        self.layout_all.addWidget(self.button_7)
        self.button_7.clicked.connect(self.game_7)

        self.button_8 = QPushButton("退出", self)
        self.layout_all.addWidget(self.button_8)
        self.button_8.clicked.connect(self.game_8)

        self.resize(400, 300)
        self.signal.connect(self.game_8)
        self.record = 1
        self.record_thread = Thread(target=self.record_voice)
        self.record_thread.setDaemon(True)
        self.record_thread.start()

    def game_1(self):
        os.system('python ./ChineseChess/main.py')

    def game_2(self):
        os.system('python ./ChineseChess/client.py')

    def game_3(self):
        os.system('python ./link_game/main.py')

    def game_4(self):
        os.system('python ./Minesweeper/main.py')

    def game_5(self):
        os.system('python ./Puzzle/game.py')

    def game_6(self):
        os.system('python ./Sokoban/game.py')

    def game_7(self):
        os.system('python ./Gobang/main.py')

    def game_8(self):
        self.destroy()
        sys.exit()


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
            if self.record == 1:
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
                    if result == '退出。':
                        self.signal.emit()
                    elif result == '象棋单机游戏。':
                        os.system('python ./ChineseChess/main.py')
                    elif result == '象棋联机游戏。':
                        os.system('python ./ChineseChess/client.py')
                    elif result == '连连看。':
                        os.system('python ./link_game/main.py')
                    elif result == '扫雷。':
                        os.system('python ./Minesweeper/main.py')
                    elif result == '拼图。':
                        os.system('python ./Puzzle/game.py')
                    elif result == '推箱子。':
                        os.system('python ./Sokoban/game.py')
                    elif result == '五子棋。':
                        os.system('python ./Gobang/main.py')
                    

    def get_file_content(self, file_path):
        with open(file_path, 'rb') as fp:
            return fp.read()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = WindowClass()
    win.show()
    sys.exit(app.exec_())