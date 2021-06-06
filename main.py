import PySimpleGUI as sg
import os
import sys
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtWebEngineWidgets import *

dirname, filename = os.path.split(os.path.abspath(__file__))
os.chdir(dirname)


class WindowClass(QMainWindow):

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

    def game_1(self):
        self.destroy()
        os.system('python ./ChineseChess/main.py')

    def game_2(self):
        self.destroy()
        os.system('python ./ChineseChess/client.py')

    def game_3(self):
        self.destroy()
        os.system('python ./link_game/main.py')

    def game_4(self):
        self.destroy()
        os.system('python ./Minesweeper/main.py')

    def game_5(self):
        self.destroy()
        os.system('python ./Puzzle/game.py')

    def game_6(self):
        self.destroy()
        os.system('python ./Sokoban/game.py')

    def game_7(self):
        self.destroy()
        os.system('python ./Gobang/main.py')

    def game_8(self):
        self.destroy()


def main():
    app = QApplication(sys.argv)
    win = WindowClass()
    win.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
