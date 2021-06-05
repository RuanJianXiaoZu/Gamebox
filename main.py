import PySimpleGUI as sg
import os
import sys

dirname, filename = os.path.split(os.path.abspath(__file__))
os.chdir(dirname)

sg.theme('Default 1')
layout = [
    [sg.Text("Welcome! Select a game below: ")],
    [sg.Button('象棋单机游戏', enable_events=True)],
    [sg.Button('象棋联机游戏', enable_events=True)],
    [sg.Button('连连看', enable_events=True)],
    [sg.Button('扫雷', enable_events=True)],
    [sg.Button('拼图', enable_events=True)],
    [sg.Button('推箱子', enable_events=True)],
    [sg.Button('五子棋', enable_events=True)],
    [sg.Button('退出', enable_events=True)]
]
window = sg.Window('GameBox', layout, finalize=True)
window.Size = (400, 300)

while True:
    event, values = window.read()
    print(event, values)
    if event == '象棋单机游戏':
        os.system('python ./ChineseChess/main.py')
    if event == '象棋联机游戏':
        os.system('python ./ChineseChess/client.py')
    if event == '连连看':
        os.system('python ./link_game/main.py')
    if event == '扫雷':
        os.system('python ./Minesweeper/main.py')
    if event == '拼图':
        os.system('python ./Puzzle/game.py')
    if event == '推箱子':
        os.system('python ./Sokoban/game.py')
    if event == '五子棋':
        os.system('python ./Gobang/main.py')
    if event == '退出' or event == sg.WINDOW_CLOSED:
        break   

window.close()