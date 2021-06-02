# coding=utf-8
from pygame import font, draw, init, display, transform, image, time, mouse, event, QUIT, MOUSEBUTTONUP, quit
from pygame.constants import USEREVENT
from settings import Setting
import wave
import numpy as np
import pyaudio
from aip import AipSpeech
import json
import time as tm


class ChineseChess:

    def text_objects(self, text, font, color):
        text_surface = font.render(text, True, color)
        return text_surface, text_surface.get_rect()


    def text_display(self, window, color, text, size, coordinate, Font):  # 'freesansbold.ttf'
        large_text = font.SysFont(Font, size)
        text_surf, text_rect = self.text_objects(text, large_text, color)
        text_rect.center = coordinate
        window.blit(text_surf, text_rect)


    def blit_chess(self, team, chess, coor):
        img = Setting.img[str(team)+'_'+str(chess)]
        self.main_window.blit(img, [coor[0], coor[1], coor[2], coor[3]])
        if str(self.coors_plate[coor[2]][coor[3]])[1] == '0':
            self.coors_all[0].append(coor.copy())
        else:
            self.coors_all[1].append(coor.copy())


    def show_all_selected(self):
        coor = [0, 32]
        for row in self.coors_plate:
            coor[0] = 37
            for col in row:
                if str(col)[-1] == '1':
                    draw.circle(self.main_window, self.white, [coor[0]+30, coor[1]+30], 34,  3)
                coor[0] += 84
            coor[1] += 75


    def display_button(self, x, y, text, word_size, func):
        self.text_display(self.main_window, self.black, text, word_size, [x, y], 'simhei')


    def hui_qi(self):
        if self.hui_yi_bu and self.start:
            try:
                self.return_c_coors_plate()
                self.who_go -= 1
                self.hui_yi_bu = False
            except:
                pass


    def new_game(self, order):
        self.who_go = order
        self.start, self.load, self.over = True, False, 0
        self.coors_plate.clear()
        for i in range(0, 10):
            self.coors_plate.append(self.temp[i].copy())


    def save_game(self):
        with open('save.txt', 'w+') as save:
            for line in self.coors_plate:
                for index, coor in enumerate(line):
                    if index != 8:
                        save.writelines(str(coor)+',')
                    else:
                        save.writelines(str(coor))
                save.writelines('\n')
            save.writelines(str(self.who_go))


    def load_game(self):
        self.start, self.load, self.first_click, self.over = False, True, True, 0
        self.coors_plate.clear()
        self.c_coors_plate.clear()
        for i in range(0, 10):
            self.coors_plate.append([])
        with open('save.txt', 'r+') as save:
            for index, line in enumerate(save.readlines()):
                if index != 10:
                    for coor in line.split(','):
                        self.coors_plate[index].append(int(coor))
                else:
                    self.who_go = int(line)


    def clean_non_selected(self):
        for I, i in enumerate(self.coors_plate):
            for II, ii in enumerate(i):
                if str(ii)[-1] == '1':
                    self.coors_plate[I][II] -= 1


    def translation(self, coor):
        # window 800x800, chess 60x60, river_top 334, river_bot 394, b/w chess 84, startPt 37, 32
        x, y = coor[0], coor[1]
        coll = (x-37)//84
        if y <= 395:
            roww = (y-32)//75
        elif 395 < y < 410:
            return False
        else:
            roww = (y-32-15)//75
        return roww, coll


    def detect_legal_move(self, coor):
        chess_code = self.coors_plate[coor[1]][coor[2]]
        chess = self.coors_chess[str(chess_code)]
        self.legal_move[chess].clear()
        if chess == 'ju':
            left, right, up, down = True, False, True, False
            for horizon in range(0, 9):
                if left:
                    if self.coors_plate[coor[1]][horizon] == 0:
                        self.legal_move[chess].append([coor[1], horizon])
                    elif horizon == coor[2]:
                        left, right = False, True
                        continue
                    elif self.coors_plate[coor[1]][horizon] != 0:
                        self.legal_move[chess].clear()
                        self.legal_move[chess].append([coor[1], horizon])
                elif right:
                    if self.coors_plate[coor[1]][horizon] == 0:
                        self.legal_move[chess].append([coor[1], horizon])
                    elif self.coors_plate[coor[1]][horizon] != 0:
                        self.legal_move[chess].append([coor[1], horizon])
                        break
            self.temp = len(self.legal_move[chess])
            for vertical in range(0, 10):
                if up:
                    if self.coors_plate[vertical][coor[2]] == 0:
                        self.legal_move[chess].append([vertical, coor[2]])
                    elif vertical == coor[1]:
                        up, down = False, True
                        continue
                    elif self.coors_plate[vertical][coor[2]] != 0:
                        del self.legal_move[chess][self.temp:]
                        self.legal_move[chess].append([vertical, coor[2]])
                elif down:
                    if self.coors_plate[vertical][coor[2]] == 0:
                        self.legal_move[chess].append([vertical, coor[2]])
                    elif self.coors_plate[vertical][coor[2]] != 0:
                        self.legal_move[chess].append([vertical, coor[2]])
                        break
        elif chess == 'ma':
            for i, ma_tui in enumerate([[coor[1]-1, coor[2]], [coor[1]+1, coor[2]],
                        [coor[1], coor[2]-1], [coor[1], coor[2]+1]]):  # 四个马腿, 上下左右
                try:
                    ma_tui_s = {
                        0: [[ma_tui[0]-1, ma_tui[1]-1], [ma_tui[0]-1, ma_tui[1]+1]],  # 上马腿
                        1: [[ma_tui[0]+1, ma_tui[1]-1], [ma_tui[0]+1, ma_tui[1]+1]],  # 下马腿
                        2: [[ma_tui[0]+1, ma_tui[1]-1], [ma_tui[0]-1, ma_tui[1]-1]],  # 左马腿
                        3: [[ma_tui[0]+1, ma_tui[1]+1], [ma_tui[0]-1, ma_tui[1]+1]]   # 右马腿
                                }
                    if self.coors_plate[ma_tui[0]][ma_tui[1]] == 0:
                        for ii in ma_tui_s[i]:
                            self.legal_move[chess].append(ii)
                except:
                    pass
        elif chess == 'xiang':
            for i, xiang_tui in enumerate([[coor[1]-1, coor[2]-1], [coor[1]-1, coor[2]+1],
                                        [coor[1]+1, coor[2]-1], [coor[1]+1, coor[2]+1]]):
                try:
                    xiang_tui_s = {
                        0: [xiang_tui[0]-1, xiang_tui[1]-1],
                        1: [xiang_tui[0]-1, xiang_tui[1]+1],
                        2: [xiang_tui[0]+1, xiang_tui[1]-1],
                        3: [xiang_tui[0]+1, xiang_tui[1]+1]
                    }
                    if self.coors_plate[xiang_tui[0]][xiang_tui[1]] == 0:
                        if self.who_go % 2 == 0 and xiang_tui_s[i][0] < 5:
                            self.legal_move[chess].append(xiang_tui_s[i])
                        elif self.who_go % 2 == 1 and xiang_tui_s[i][0] > 4:
                            self.legal_move[chess].append(xiang_tui_s[i])
                except:
                    pass
        elif chess == 'shi' or chess == 'jiang' or chess == 'shuai':
            dics = {
                'shi': [[coor[1]-1, coor[2]-1], [coor[1]-1, coor[2]+1], [coor[1]+1, coor[2]+1], [coor[1]+1, coor[2]-1]],
                'jiang': [[coor[1]-1, coor[2]], [coor[1]+1, coor[2]], [coor[1], coor[2]-1], [coor[1], coor[2]+1]],
                'shuai': [[coor[1]-1, coor[2]], [coor[1]+1, coor[2]], [coor[1], coor[2]-1], [coor[1], coor[2]+1]]
            }
            if self.who_go % 2 == 1:
                for step in dics[chess]:
                    if 2 < step[1] < 6 < step[0] < 10:
                        self.legal_move[chess].append(step)
            else:
                for step in dics[chess]:
                    if -1 < step[0] < 3 and 2 < step[1] < 6:
                        self.legal_move[chess].append(step)
        elif chess == 'bing':
            if self.who_go % 2 == 0:
                if coor[1] < 5:
                    self.legal_move[chess].append([coor[1]+1, coor[2]])
                else:
                    for step in [[coor[1]+1, coor[2]], [coor[1], coor[2]-1], [coor[1], coor[2]+1]]:
                        self.legal_move[chess].append(step)
            else:
                if coor[1] > 4:
                    self.legal_move[chess].append([coor[1]-1, coor[2]])
                else:
                    for step in [[coor[1]-1, coor[2]], [coor[1], coor[2]-1], [coor[1], coor[2]+1]]:
                        self.legal_move[chess].append(step)
        elif chess == 'pao':
            all_horizon = []
            all_vertical = []
            for horizon in range(0, 9):
                all_horizon.append([self.coors_plate[coor[1]][horizon], [coor[1], horizon]])
            for vertical in range(0, 10):
                all_vertical.append([self.coors_plate[vertical][coor[2]], [vertical, coor[2]]])
            #  horizontal
            for times in range(0, 2):
                first = False
                all_horizon.reverse()
                index_h = all_horizon.index([chess_code, [coor[1], coor[2]]])
                for side in all_horizon[index_h+1:]:
                    if side[0] == 0 and not first:
                        self.legal_move[chess].append(side[1])
                    if first:
                        if side[0] != 0:
                            self.legal_move[chess].append(side[1])
                            first = False
                            break
                    elif side[0] != 0:
                        first = True
                        continue
            # vertical
            for times in range(0, 2):
                first = False
                all_vertical.reverse()
                index_v = all_vertical.index([chess_code, [coor[1], coor[2]]])
                for side in all_vertical[index_v+1:]:
                    if side[0] == 0 and not first:
                        self.legal_move[chess].append(side[1])
                    if first:
                        if side[0] != 0:
                            self.legal_move[chess].append(side[1])
                            break
                    elif side[0] != 0:
                        first = True
                        continue
        return chess


    def game_over(self):
        x = 0
        self.jiang_shuai.clear()
        for i, row in enumerate(self.coors_plate):
            for ii, col in enumerate(row):
                if col == 5000 or col == 5100 or col == 5001 or col == 5101:
                    x += 1
                    self.jiang_shuai.append([i, ii])
        try:
            if self.jiang_shuai[0][1] == self.jiang_shuai[1][1] and x == 2:
                for i in range(self.jiang_shuai[0][0]+1, abs(self.jiang_shuai[1][0] - self.jiang_shuai[0][0])+1):
                    if self.coors_plate[i][self.jiang_shuai[0][1]] != 0:
                        return x
                    elif i == self.jiang_shuai[0][0]-1 or i == self.jiang_shuai[1][0]-1:
                        x = 1
                        return x
            else:
                return x
        except:
            return 1

    def return_c_coors_plate(self):
        self.coors_plate.clear()
        for i in range(0, 10):
            self.coors_plate.append(self.c_coors_plate[i].copy())


    def update_c_coors_plate(self):
        self.c_coors_plate.clear()
        for i in range(0, 10):
            self.c_coors_plate.append(self.coors_plate[i].copy())


    def click_chess(self, side):
        if self.first_click:
            self.first_click_coor = [0, 0, 0]
            for coor in self.coors_all[side]:
                if coor[0] < self.Mouse[0] < coor[0] + 60 and coor[1] < self.Mouse[1] < coor[1] + 60:
                    self.coors_plate[coor[2]][coor[3]] += 1
                    self.first_click_coor[0], self.first_click_coor[1], self.first_click_coor[2] = \
                        self.coors_plate[coor[2]][coor[3]] - 1, coor[2], coor[3]
                    self.chess = self.detect_legal_move(self.first_click_coor)
                    self.first_click, self.start = False, True
                    if self.who_go % 2 == 1:
                        self.mouse1 = 800 - self.Mouse[0], 805 - self.Mouse[1]
                    break
        else:
            self.clean_non_selected()
            for legal in self.legal_move[self.chess]:
                second_click_coor = self.translation(self.Mouse)
                if second_click_coor[0] == legal[0] and second_click_coor[1] == legal[1]:  # x1 == x2, y1 == y2
                    self.update_c_coors_plate()
                    if self.coors_plate[second_click_coor[0]][second_click_coor[1]] == 0 or \
                            str(self.coors_plate[second_click_coor[0]][second_click_coor[1]])[1] != str(side):
                        self.coors_plate[second_click_coor[0]][second_click_coor[1]] = self.first_click_coor[0]  # 画上新的棋子
                        self.coors_plate[self.first_click_coor[1]][self.first_click_coor[2]] = 0  # 去掉旧的棋子
                        self.who_go += 1
                        self.hui_yi_bu = True
                    if self.who_go % 2 == 0:
                        self.mouse2 = 800 - self.Mouse[0], 805 - self.Mouse[1]
                        send_msg = {'type': 'sendmouse', 'name': self.name, 'mouse1': self.mouse1, 'mouse2': self.mouse2}
                        send_json = json.dumps(send_msg)
                        self.client.send(send_json.encode())  # 直接读档需要start = True让who_go进行变化
                    break
            self.first_click = True


    def voice_control(self, side):
        self.first_click_coor = [0, 0, 0]
        if side == 0:
            if self.record[1] < 10:
                self.record[1] = 10 - self.record[1]
            elif self.record[1] == 10:
                self.record[1] = 11
            elif self.record[1] == 11:
                self.record[1] = 10
            if self.record[0] == 1 or self.record[0] == 5 or self.record[0] == 6 or self.record[0] == 7:
                if self.record[2] == 1:
                    self.record[2] = 2
                elif self.record[2] == 2:
                    self.record[2] = 1
                elif self.record[2] == 3:
                    self.record[3] = 10 - self.record[3]
            elif self.record[0] == 2 or self.record[0] == 3 or self.record[0] == 4: 
                self.record[3] = 10 - self.record[3]
                if self.record[2] == 1:
                    self.record[2] = 2
                elif self.record[2] == 2:
                    self.record[2] = 1
        if self.record[1] < 10:
            for i, row in enumerate(self.coors_plate):
                if str(row[9 - self.record[1]])[0] == str(self.record[0]) and str(row[9 - self.record[1]])[1] == str(side):
                    self.coors_plate[i][9 - self.record[1]] += 1
                    self.first_click_coor[0], self.first_click_coor[1], self.first_click_coor[2] = \
                        self.coors_plate[i][9 - self.record[1]] - 1, i, 9 - self.record[1]
                    self.chess = self.detect_legal_move(self.first_click_coor)
                    self.first_click, self.start = False, True  # 直接读档需要start = True让who_go进行变化
                    break
        elif self.record[1] == 10:
            for i, row in enumerate(self.coors_plate):
                for ii, col in enumerate(row):
                    if str(col)[0] == str(self.record[0]) and str(col)[1] == str(side):
                        self.coors_plate[i][ii] += 1
                        self.first_click_coor[0], self.first_click_coor[1], self.first_click_coor[2] = \
                            self.coors_plate[i][ii] - 1, i, ii
                        self.chess = self.detect_legal_move(self.first_click_coor)
                        self.first_click, self.start = False, True  # 直接读档需要start = True让who_go进行变化
                        break
                if self.first_click == False:
                    break
        elif self.record[1] == 11:
            iii = 0
            for i, row in enumerate(self.coors_plate):
                for ii, col in enumerate(row):
                    if str(col)[0] == str(self.record[0]) and str(col)[1] == str(side):
                        self.coors_plate[i][ii] += 1
                        self.first_click_coor[0], self.first_click_coor[1], self.first_click_coor[2] = \
                            self.coors_plate[i][ii] - 1, i, ii
                        self.chess = self.detect_legal_move(self.first_click_coor)
                        self.first_click, self.start = False, True  # 直接读档需要start = True让who_go进行变化
                        iii = iii + 1
                        break
                if iii == 2:
                    break
        if self.first_click == True:
            print("语音指令错误！")
        else:
            self.clean_non_selected()
            second_click_coor = [100, 100]
            if self.record[0] == 1 or self.record[0] == 5 or self.record[0] == 6 or self.record[0] == 7:
                if self.record[2] == 1:
                    second_click_coor = [self.first_click_coor[1] - self.record[3], self.first_click_coor[2]]
                elif self.record[2] == 2:
                    second_click_coor = [self.first_click_coor[1] + self.record[3], self.first_click_coor[2]]
                elif self.record[2] == 3:
                    second_click_coor = [self.first_click_coor[1], 9 - self.record[3]]
            elif self.record[0] == 2:
                if self.record[2] == 1:
                    if abs(9 - self.record[3] - self.first_click_coor[2]) % 2 == 0:
                        second_click_coor = [self.first_click_coor[1] - 1, 9 - self.record[3]]
                    elif abs(9 - self.record[3] - self.first_click_coor[2]) % 2 == 1:
                        second_click_coor = [self.first_click_coor[1] - 2, 9 - self.record[3]]
                elif self.record[2] == 2:
                    if abs(9 - self.record[3] - self.first_click_coor[2]) % 2 == 0:
                        second_click_coor = [self.first_click_coor[1] + 1, 9 - self.record[3]]
                    elif abs(9 - self.record[3] - self.first_click_coor[2]) % 2 == 1:
                        second_click_coor = [self.first_click_coor[1] + 2, 9 - self.record[3]]
            elif self.record[0] == 3:
                if self.record[2] == 1: 
                    second_click_coor = [self.first_click_coor[1] - 2, 9 - self.record[3]]
                elif self.record[2] == 2:
                    second_click_coor = [self.first_click_coor[1] + 2, 9 - self.record[3]]
            elif self.record[0] == 4:
                if self.record[2] == 1: 
                    second_click_coor = [self.first_click_coor[1] - 1, 9 - self.record[3]]
                elif self.record[2] == 2:
                    second_click_coor = [self.first_click_coor[1] + 1, 9 - self.record[3]]
            if second_click_coor == [100, 100]:
                print("语音指令错误！")
            else:
                for legal in self.legal_move[self.chess]:
                    if second_click_coor[0] == legal[0] and second_click_coor[1] == legal[1]:  # x1 == x2, y1 == y2
                        self.update_c_coors_plate()
                        if self.coors_plate[second_click_coor[0]][second_click_coor[1]] == 0 or \
                                str(self.coors_plate[second_click_coor[0]][second_click_coor[1]])[1] != str(side):
                            self.coors_plate[second_click_coor[0]][second_click_coor[1]] = self.first_click_coor[0]  # 画上新的棋子
                            self.coors_plate[self.first_click_coor[1]][self.first_click_coor[2]] = 0  # 去掉旧的棋子
                            self.who_go += 1
                            self.hui_yi_bu = True
                            self.first_click = True
                        if self.who_go % 2 == 0:
                            send_msg = {'type': 'sendrecord', 'name': self.name, 'record': self.record}
                            send_json = json.dumps(send_msg)
                            self.client.send(send_json.encode())
                        break
                if self.first_click == False:
                    print("语音指令错误！")
                    self.first_click = True
        self.record = [0, 0, 0, 0]

    def recvrecord(self, record):
        self.record = record
        my_event = event.Event(USEREVENT + 7)
        event.post(my_event)

    def recvmouse(self, mouse1, mouse2):
        self.mouse1 = mouse1
        self.mouse2 = mouse2
        my_event = event.Event(USEREVENT + 9)
        event.post(my_event)

    def postevent(self, num):
        my_event = event.Event(USEREVENT + num)
        event.post(my_event)
    
    def quit(self):
        my_event = event.Event(USEREVENT + 8)
        event.post(my_event)

    def show(self, name, client, order):
        init()
        self.background = image.load('background.png')
        self.background = transform.scale(self.background, (1000, 800))
        self.window_width, self.window_height = 1000, 800
        self.main_window = display.set_mode((self.window_width, self.window_height))
        self.clock = time.Clock()
        self.black = (0, 0, 0)
        self.red = (255, 0, 0)
        self.gray = (100, 100, 100)
        self.white = (255, 255, 255)
        self.who_go = 0  # even means red goes first, old means black goes first
        self.first_click_coor = []
        self.start = False
        self.load = False
        self.first_click = True
        self.mouse_up = False
        self.hui_yi_bu = False
        self.temp = Setting.coors_plate
        self.coors_chess = Setting.coors_chess
        self.legal_move = Setting.legal_move
        self.coors_plate = []
        self.c_coors_plate = []
        self.jiang_shuai = []
        self.chess = 0
        self.over = 0
        self.record = [0, 0, 0, 0]
        self.mouse1 = []
        self.mouse2 = []
        self.name = name
        self.client = client
        self.order = order
        self.new_game(self.order)

        while True:
            self.main_window.blit(self.background, (0, 0))
            self.Mouse = mouse.get_pos()
            self.click = mouse.get_pressed()
            self.coors = [0, 32, 0, 0, 0]
            self.coors_all = [[], []]
            self.non_chess_coors = []

            for i, row in enumerate(self.coors_plate):
                self.coors[0] = 37
                for ii, col in enumerate(row):
                    self.coors[2], self.coors[3] = i, ii
                    # red
                    if col == 1010 or col == 1011 or col == 1020 or col == 1021:
                        self.blit_chess('red', 'ju', self.coors)
                    elif col == col == 2010 or col == 2011 or col == 2020 or col == 2021:
                        self.blit_chess('red', 'ma', self.coors)
                    elif col == 3010 or col == 3011 or col == 3020 or col == 3021:
                        self.blit_chess('red', 'xiang', self.coors)
                    elif col == col == 4010 or col == 4011 or col == 4020 or col == 4021:
                        self.blit_chess('red', 'shi', self.coors)
                    elif col == 5000 or col == 5001:
                        self.blit_chess('red', 'shuai', self.coors)
                    elif col == col == 6010 or col == 6011 or col == 6020 or col == 6021:
                        self.blit_chess('red', 'pao', self.coors)
                    elif col == 7010 or col == 7011 or col == 7020 or col == 7021 or col == 7030\
                            or col == 7031 or col == 7040 or col == 7041 or col == 7050 or col == 7051:
                        self.blit_chess('red', 'bing', self.coors)
                    # black
                    elif col == 1110 or col == 1111 or col == 1120 or col == 1121:
                        self.blit_chess('black', 'ju', self.coors)
                    elif col == 2110 or col == 2111 or col == 2120 or col == 2121:
                        self.blit_chess('black', 'ma', self.coors)
                    elif col == 3110 or col == 3111 or col == 3120 or col == 3121:
                        self.blit_chess('black', 'xiang', self.coors)
                    elif col == 4110 or col == 4111 or col == 4120 or col == 4121:
                        self.blit_chess('black', 'shi', self.coors)
                    elif col == 5100 or col == 5101:
                        self.blit_chess('black', 'jiang', self.coors)
                    elif col == 6110 or col == 6111 or col == 6120 or col == 6121:
                        self.blit_chess('black', 'pao', self.coors)
                    elif col == 7110 or col == 7111 or col == 7120 or col == 7121 or col == 7130 \
                            or col == 7131 or col == 7140 or col == 7141 or col == 7150 or col == 7151:
                        self.blit_chess('black', 'bing', self.coors)
                    else:
                        self.non_chess_coors.append(self.coors.copy())
                    self.coors[0] += 84
                self.coors[1] += 75

            self.show_all_selected()
            # 新游戏
            self.display_button(900, 90, '新游戏', 30, 'new_game')
            # 储存游戏
            self.display_button(900, 172, '存档', 30, 'save_game')
            # 加载游戏
            self.display_button(900, 633, '读档', 30, 'load_game')
            # 悔一步
            self.display_button(900, 407, '悔一步', 30, 'hui_qi')
            # 显示回合
            if self.start or self.load:
                if self.who_go % 2 == 0:
                    self.text_display(self.main_window, self.red, '对方回合', 30, [900, 717], 'simhei')
                else:
                    self.text_display(self.main_window, self.black, '您的回合', 30, [900, 717], 'simhei')
            if self.start or self.load:
                self.over = self.game_over()
                if self.over == 1:
                    self.text_display(self.main_window, self.black, '游戏结束', 100, [self.window_width // 2, self.window_height // 2], 'simhei')

            self.mouse_up = False
            for Event in event.get():
                if Event.type == QUIT:
                    if self.over == 1:
                        send_msg = {'type': 'exit', 'name': self.name}
                        send_json = json.dumps(send_msg)
                        self.client.send(send_json.encode())
                        quit()
                        break
                    else:
                        send_msg = {'type': 'quit', 'name': self.name}
                        send_json = json.dumps(send_msg)
                        self.client.send(send_json.encode())
                        quit()
                        break
                if Event.type == MOUSEBUTTONUP:
                    self.mouse_up = True
                    if 385 > self.Mouse[1] or 425 < self.Mouse[1] and self.Mouse[0] < 800:
                        if self.who_go % 2 == 1 and self.over != 1:
                            self.click_chess(1)  # eg. chess = [709, 707, 9, 8] - x, y, row, col
                if Event.type == USEREVENT + 1:
                    if self.who_go % 2 == 1 and self.over != 1:
                        self.voice_control(1)  # eg. chess = [709, 707, 9, 8] - x, y, row, col
                if Event.type == USEREVENT + 2:
                    if self.over == 1:
                        send_msg = {'type': 'exit', 'name': self.name}
                        send_json = json.dumps(send_msg)
                        self.client.send(send_json.encode())
                        quit()
                        break
                    else:
                        send_msg = {'type': 'quit', 'name': self.name}
                        send_json = json.dumps(send_msg)
                        self.client.send(send_json.encode())
                        quit()
                        break
                if Event.type == USEREVENT + 7:
                    self.voice_control(0)
                if Event.type == USEREVENT + 8:
                    quit()
                    break
                if Event.type == USEREVENT + 9:
                    self.Mouse = self.mouse1
                    self.click_chess(0)
                    self.Mouse = self.mouse2
                    self.click_chess(0)
            else:
                display.update()
                self.clock.tick()
                continue
            break