import PySimpleGUI as sg
import os
import sys

dirname, filename = os.path.split(os.path.abspath(__file__))
os.chdir(dirname)

sg.theme('Default 1')
layout = [
    [sg.Text("Welcome! Select a game below: ")],
    [sg.Button('ChineseChess', enable_events=True)],
    [sg.Button('link game', enable_events=True)],
    [sg.Button('Minesweeper', enable_events=True)],
    [sg.Button('Puzzle', enable_events=True)],
    [sg.Button('Sokoban', enable_events=True)],
    [sg.Button('Gobang', enable_events=True)],
    [sg.Button('Exit', enable_events=True)]
]
window = sg.Window('GameBox', layout, finalize=True)
window.Size = (400, 300)

while True:
    event, values = window.read()
    print(event, values)
    if event == 'ChineseChess':
        os.system('python ./ChineseChess/game.py')
    if event == 'link game':
        os.system('python ./link_game/main.py')
    if event == 'Minesweeper':
        os.system('python ./Minesweeper/main.py')
    if event == 'Puzzle':
        os.system('python ./Puzzle/game.py')
    if event == 'Sokoban':
        os.system('python ./Sokoban/game.py')
    if event == 'Gobang':
        os.system('python ./Gobang/main.py')
    if event == 'Exit' or event == sg.WINDOW_CLOSED:
        break   

window.close()