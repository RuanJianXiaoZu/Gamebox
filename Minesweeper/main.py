import os
import sys
import time
import random
import wave
import threading
from enum import Enum
import pygame
from pygame import event
from pygame.constants import USEREVENT
from pygame.locals import *
import numpy as np
import pyaudio
from aip import AipSpeech

BLOCK_WIDTH = 9
BLOCK_HEIGHT = 9
SIZE = 25           # 块大小
MINE_COUNT = 10     # 地雷数

# 游戏屏幕的宽
SCREEN_WIDTH = BLOCK_WIDTH * SIZE
# 游戏屏幕的高
SCREEN_HEIGHT = (BLOCK_HEIGHT + 2) * SIZE


class GameStatus(Enum):
    readied = 1,
    started = 2,
    over = 3,
    win = 4


class BlockStatus(Enum):
    normal = 1  # 未点击
    opened = 2  # 已点击
    mine = 3    # 地雷
    flag = 4    # 标记为地雷
    ask = 5     # 标记为问号
    bomb = 6    # 踩中地雷
    hint = 7    # 被双击的周围
    double = 8  # 正被鼠标左右键双击


class Mine:
    def __init__(self, x, y, value=0):
        self._x = x
        self._y = y
        self._value = 0
        self._around_mine_count = -1
        self._status = BlockStatus.normal
        self.set_value(value)

    def __repr__(self):
        return str(self._value)
        # return f'({self._x},{self._y})={self._value}, status={self.status}'

    def get_x(self):
        return self._x

    def set_x(self, x):
        self._x = x

    x = property(fget=get_x, fset=set_x)

    def get_y(self):
        return self._y

    def set_y(self, y):
        self._y = y

    y = property(fget=get_y, fset=set_y)

    def get_value(self):
        return self._value

    def set_value(self, value):
        if value:
            self._value = 1
        else:
            self._value = 0

    value = property(fget=get_value, fset=set_value, doc='0:非地雷 1:雷')

    def get_around_mine_count(self):
        return self._around_mine_count

    def set_around_mine_count(self, around_mine_count):
        self._around_mine_count = around_mine_count

    around_mine_count = property(fget=get_around_mine_count, fset=set_around_mine_count, doc='四周地雷数量')

    def get_status(self):
        return self._status

    def set_status(self, value):
        self._status = value

    status = property(fget=get_status, fset=set_status, doc='BlockStatus')


class MineBlock:
    def __init__(self):
        self._block = [[Mine(i, j) for i in range(BLOCK_WIDTH)] for j in range(BLOCK_HEIGHT)]

        # 埋雷
        for i in random.sample(range(BLOCK_WIDTH * BLOCK_HEIGHT), MINE_COUNT):
            self._block[i // BLOCK_WIDTH][i % BLOCK_WIDTH].value = 1

    def get_block(self):
        return self._block

    block = property(fget=get_block)

    def getmine(self, x, y):
        return self._block[y][x]

    def open_mine(self, x, y):
        # 踩到雷了
        if self._block[y][x].value:
            self._block[y][x].status = BlockStatus.bomb
            return False

        # 先把状态改为 opened
        self._block[y][x].status = BlockStatus.opened

        around = _get_around(x, y)

        _sum = 0
        for i, j in around:
            if self._block[j][i].value:
                _sum += 1
        self._block[y][x].around_mine_count = _sum

        # 如果周围没有雷，那么将周围8个未中未点开的递归算一遍
        # 这就能实现一点出现一大片打开的效果了
        if _sum == 0:
            for i, j in around:
                if self._block[j][i].around_mine_count == -1:
                    self.open_mine(i, j)

        return True

    def double_mouse_button_down(self, x, y):
        if self._block[y][x].around_mine_count == 0:
            return True

        self._block[y][x].status = BlockStatus.double

        around = _get_around(x, y)

        sumflag = 0     # 周围被标记的雷数量
        for i, j in _get_around(x, y):
            if self._block[j][i].status == BlockStatus.flag:
                sumflag += 1
        # 周边的雷已经全部被标记
        result = True
        if sumflag == self._block[y][x].around_mine_count:
            for i, j in around:
                if self._block[j][i].status == BlockStatus.normal:
                    if not self.open_mine(i, j):
                        result = False
        else:
            for i, j in around:
                if self._block[j][i].status == BlockStatus.normal:
                    self._block[j][i].status = BlockStatus.hint
        return result

    def double_mouse_button_up(self, x, y):
        self._block[y][x].status = BlockStatus.opened
        for i, j in _get_around(x, y):
            if self._block[j][i].status == BlockStatus.hint:
                self._block[j][i].status = BlockStatus.normal


def _get_around(x, y):
    """返回(x, y)周围的点的坐标"""
    # 这里注意，range 末尾是开区间，所以要加 1
    return [(i, j) for i in range(max(0, x - 1), min(BLOCK_WIDTH - 1, x + 1) + 1)
            for j in range(max(0, y - 1), min(BLOCK_HEIGHT - 1, y + 1) + 1) if i != x or j != y]



def print_text(screen, font, x, y, text, fcolor=(255, 255, 255)):
    imgText = font.render(text, True, fcolor)
    screen.blit(imgText, (x, y))


def ShowStartInterface(screen, width, height):
    screen.fill((255, 255, 255))
    tfont = pygame.font.Font(os.path.join(os.getcwd(), 'Minesweeper/resources/FZSTK.TTF'), width//2)
    cfont = pygame.font.Font(os.path.join(os.getcwd(), 'Minesweeper/resources/FZSTK.TTF'), width//10)
    title = tfont.render('扫雷', True, (255, 0, 0))
    content1 = cfont.render('初级(L)', True, (0, 0, 255))
    content2 = cfont.render('中级(M)', True, (0, 0, 255))
    content3 = cfont.render('高级(H)', True, (0, 0, 255))
    trect = title.get_rect()
    trect.midtop = (width/2, height/10)
    crect1 = content1.get_rect()
    crect1.midtop = (width/2, height/1.8)
    crect2 = content2.get_rect()
    crect2.midtop = (width/2, height/1.5)
    crect3 = content3.get_rect()
    crect3.midtop = (width/2, height/1.27)
    screen.blit(title, trect)
    screen.blit(content1, crect1)
    screen.blit(content2, crect2)
    screen.blit(content3, crect3)
    global BLOCK_WIDTH, BLOCK_HEIGHT, SIZE, MINE_COUNT, SCREEN_WIDTH, SCREEN_HEIGHT
    while True:
        for event in pygame.event.get():
            if (event.type == pygame.QUIT) or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE) or (event.type == USEREVENT + 2):
                isOver = True
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == ord('l'): return 2
                elif event.key == ord('m'):
                    BLOCK_WIDTH = 16
                    BLOCK_HEIGHT = 16
                    MINE_COUNT = 40     
                    SCREEN_WIDTH = BLOCK_WIDTH * SIZE
                    SCREEN_HEIGHT = (BLOCK_HEIGHT + 2) * SIZE
                    return 3
                elif event.key == ord('h'):
                    BLOCK_WIDTH = 30
                    BLOCK_HEIGHT = 16
                    MINE_COUNT = 99     
                    SCREEN_WIDTH = BLOCK_WIDTH * SIZE
                    SCREEN_HEIGHT = (BLOCK_HEIGHT + 2) * SIZE
                    return 4
            elif event.type == USEREVENT + 2: return 2
            elif event.type == USEREVENT + 3:
                BLOCK_WIDTH = 16
                BLOCK_HEIGHT = 16
                MINE_COUNT = 40     
                SCREEN_WIDTH = BLOCK_WIDTH * SIZE
                SCREEN_HEIGHT = (BLOCK_HEIGHT + 2) * SIZE
                return 3
            elif event.type == USEREVENT + 4:
                BLOCK_WIDTH = 30
                BLOCK_HEIGHT = 16
                MINE_COUNT = 99     
                SCREEN_WIDTH = BLOCK_WIDTH * SIZE
                SCREEN_HEIGHT = (BLOCK_HEIGHT + 2) * SIZE
                return 4
        pygame.display.update()


def get_file_content(file_path):
    with open(file_path, 'rb') as fp:
        return fp.read()


def record_voice():
    APP_ID = '24142986'
    API_KEY = 'lz8wrZPBovwoWXqpL2FRBtDX'
    SECRET_KEY = '34kKxkbMKB8VaqWZRQxV1y4QbPNW0xkG'

    client = AipSpeech(APP_ID, API_KEY, SECRET_KEY)

    CHUNK = 1024
    FORMAT = pyaudio.paInt16  # 16bit编码格式
    CHANNELS = 1  # 单声道
    RATE = 16000  # 16000采样频率

    while True:
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
            audio_data1 = np.frombuffer(data1, dtype=np.short)
            temp1 = np.max(audio_data1)
            if temp1 > 550:
                less = 0
                while True:
                    # print("recording")
                    for i in range(0, 5):
                        data2 = stream.read(CHUNK)
                        frames.append(data2)
                    audio_data2 = np.frombuffer(data2, dtype=np.short)
                    temp2 = np.max(audio_data2)
                    if temp2 < 550:
                        less = less + 1
                        if less == 2:
                            break
                    else:
                        less = 0
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
        
        result = ''.join(client.asr(get_file_content('1.wav'), 'wav', 16000, {
            'dev_pid': 1537,  # 默认1537（普通话 输入法模型）
        })["result"])
        print(result)

        if result == "初级。":
            my_event = event.Event(USEREVENT + 2)
            event.post(my_event)
            continue
        elif result == "中级。":
            my_event = event.Event(USEREVENT + 3)
            event.post(my_event)
            continue
        elif result == "高级。":
            my_event = event.Event(USEREVENT + 4)
            event.post(my_event)
            continue
        elif result == "结束。":
            my_event = event.Event(QUIT)
            event.post(my_event)
            break


def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption('扫雷')
    record_thread.start()
    ShowStartInterface(screen, SCREEN_WIDTH, SCREEN_HEIGHT)

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption('扫雷')
    font1 = pygame.font.Font(os.path.join(os.getcwd(), 'Minesweeper/resources/a.TTF'), SIZE * 2)  # 得分的字体
    fwidth, fheight = font1.size('999')
    red = (200, 40, 40)

    # 加载资源图片，因为资源文件大小不一，所以做了统一的缩放处理
    img0 = pygame.image.load(os.path.join(os.getcwd(), 'Minesweeper/resources/0.bmp')).convert()
    img0 = pygame.transform.smoothscale(img0, (SIZE, SIZE))
    img1 = pygame.image.load(os.path.join(os.getcwd(), 'Minesweeper/resources/1.bmp')).convert()
    img1 = pygame.transform.smoothscale(img1, (SIZE, SIZE))
    img2 = pygame.image.load(os.path.join(os.getcwd(), 'Minesweeper/resources/2.bmp')).convert()
    img2 = pygame.transform.smoothscale(img2, (SIZE, SIZE))
    img3 = pygame.image.load(os.path.join(os.getcwd(), 'Minesweeper/resources/3.bmp')).convert()
    img3 = pygame.transform.smoothscale(img3, (SIZE, SIZE))
    img4 = pygame.image.load(os.path.join(os.getcwd(), 'Minesweeper/resources/4.bmp')).convert()
    img4 = pygame.transform.smoothscale(img4, (SIZE, SIZE))
    img5 = pygame.image.load(os.path.join(os.getcwd(), 'Minesweeper/resources/5.bmp')).convert()
    img5 = pygame.transform.smoothscale(img5, (SIZE, SIZE))
    img6 = pygame.image.load(os.path.join(os.getcwd(), 'Minesweeper/resources/6.bmp')).convert()
    img6 = pygame.transform.smoothscale(img6, (SIZE, SIZE))
    img7 = pygame.image.load(os.path.join(os.getcwd(), 'Minesweeper/resources/7.bmp')).convert()
    img7 = pygame.transform.smoothscale(img7, (SIZE, SIZE))
    img8 = pygame.image.load(os.path.join(os.getcwd(), 'Minesweeper/resources/8.bmp')).convert()
    img8 = pygame.transform.smoothscale(img8, (SIZE, SIZE))
    img_blank = pygame.image.load(os.path.join(os.getcwd(), 'Minesweeper/resources/blank.bmp')).convert()
    img_blank = pygame.transform.smoothscale(img_blank, (SIZE, SIZE))
    img_flag = pygame.image.load(os.path.join(os.getcwd(), 'Minesweeper/resources/flag.bmp')).convert()
    img_flag = pygame.transform.smoothscale(img_flag, (SIZE, SIZE))
    img_ask = pygame.image.load(os.path.join(os.getcwd(), 'Minesweeper/resources/ask.bmp')).convert()
    img_ask = pygame.transform.smoothscale(img_ask, (SIZE, SIZE))
    img_mine = pygame.image.load(os.path.join(os.getcwd(), 'Minesweeper/resources/mine.bmp')).convert()
    img_mine = pygame.transform.smoothscale(img_mine, (SIZE, SIZE))
    img_blood = pygame.image.load(os.path.join(os.getcwd(), 'Minesweeper/resources/blood.bmp')).convert()
    img_blood = pygame.transform.smoothscale(img_blood, (SIZE, SIZE))
    img_error = pygame.image.load(os.path.join(os.getcwd(), 'Minesweeper/resources/error.bmp')).convert()
    img_error = pygame.transform.smoothscale(img_error, (SIZE, SIZE))
    face_size = int(SIZE * 1.25)
    img_face_fail = pygame.image.load(os.path.join(os.getcwd(), 'Minesweeper/resources/face_fail.bmp')).convert()
    img_face_fail = pygame.transform.smoothscale(img_face_fail, (face_size, face_size))
    img_face_normal = pygame.image.load(os.path.join(os.getcwd(), 'Minesweeper/resources/face_normal.bmp')).convert()
    img_face_normal = pygame.transform.smoothscale(img_face_normal, (face_size, face_size))
    img_face_success = pygame.image.load(os.path.join(os.getcwd(), 'Minesweeper/resources/face_success.bmp')).convert()
    img_face_success = pygame.transform.smoothscale(img_face_success, (face_size, face_size))
    face_pos_x = (SCREEN_WIDTH - face_size) // 2
    face_pos_y = (SIZE * 2 - face_size) // 2

    img_dict = {
        0: img0,
        1: img1,
        2: img2,
        3: img3,
        4: img4,
        5: img5,
        6: img6,
        7: img7,
        8: img8
    }

    bgcolor = (225, 225, 225)   # 背景色

    block = MineBlock()
    game_status = GameStatus.readied
    start_time = None   # 开始时间
    elapsed_time = 0    # 耗时

    while True:
        # 填充背景色
        screen.fill(bgcolor)

        for event in pygame.event.get():
            if event.type == QUIT:
                sys.exit()
            elif event.type == MOUSEBUTTONDOWN:
                mouse_x, mouse_y = event.pos
                x = mouse_x // SIZE
                y = mouse_y // SIZE - 2
                b1, b2, b3 = pygame.mouse.get_pressed()
                if game_status == GameStatus.started:
                    # 鼠标左右键同时按下，如果已经标记了所有雷，则打开周围一圈
                    # 如果还未标记完所有雷，则有一个周围一圈被同时按下的效果
                    if b1 and b3:
                        mine = block.getmine(x, y)
                        if mine.status == BlockStatus.opened:
                            if not block.double_mouse_button_down(x, y):
                                game_status = GameStatus.over
            elif event.type == MOUSEBUTTONUP:
                if y < 0:
                    if face_pos_x <= mouse_x <= face_pos_x + face_size \
                            and face_pos_y <= mouse_y <= face_pos_y + face_size:
                        game_status = GameStatus.readied
                        block = MineBlock()
                        start_time = time.time()
                        elapsed_time = 0
                        continue

                if game_status == GameStatus.readied:
                    game_status = GameStatus.started
                    start_time = time.time()
                    elapsed_time = 0

                if game_status == GameStatus.started:
                    mine = block.getmine(x, y)
                    if b1 and not b3:       # 按鼠标左键
                        if mine.status == BlockStatus.normal:
                            if not block.open_mine(x, y):
                                game_status = GameStatus.over
                    elif not b1 and b3:     # 按鼠标右键
                        if mine.status == BlockStatus.normal:
                            mine.status = BlockStatus.flag
                        elif mine.status == BlockStatus.flag:
                            mine.status = BlockStatus.ask
                        elif mine.status == BlockStatus.ask:
                            mine.status = BlockStatus.normal
                    elif b1 and b3:
                        if mine.status == BlockStatus.double:
                            block.double_mouse_button_up(x, y)

        flag_count = 0
        opened_count = 0

        for row in block.block:
            for mine in row:
                pos = (mine.x * SIZE, (mine.y + 2) * SIZE)
                if mine.status == BlockStatus.opened:
                    screen.blit(img_dict[mine.around_mine_count], pos)
                    opened_count += 1
                elif mine.status == BlockStatus.double:
                    screen.blit(img_dict[mine.around_mine_count], pos)
                elif mine.status == BlockStatus.bomb:
                    screen.blit(img_blood, pos)
                elif mine.status == BlockStatus.flag:
                    screen.blit(img_flag, pos)
                    flag_count += 1
                elif mine.status == BlockStatus.ask:
                    screen.blit(img_ask, pos)
                elif mine.status == BlockStatus.hint:
                    screen.blit(img0, pos)
                elif game_status == GameStatus.over and mine.value:
                    screen.blit(img_mine, pos)
                elif mine.value == 0 and mine.status == BlockStatus.flag:
                    screen.blit(img_error, pos)
                elif mine.status == BlockStatus.normal:
                    screen.blit(img_blank, pos)

        # 计数
        print_text(screen, font1, face_pos_x // 2 - 12, (SIZE * 2 - fheight) // 2 - 2, '%02d' % (MINE_COUNT - flag_count), red)
        if game_status == GameStatus.started:
            elapsed_time = int(time.time() - start_time)
        # 计时
        print_text(screen, font1, (SCREEN_WIDTH + face_pos_x) // 2 - 18, (SIZE * 2 - fheight) // 2 - 2, '%03d' % elapsed_time, red)

        if flag_count + opened_count == BLOCK_WIDTH * BLOCK_HEIGHT:
            game_status = GameStatus.win

        if game_status == GameStatus.over:
            screen.blit(img_face_fail, (face_pos_x, face_pos_y))
        elif game_status == GameStatus.win:
            screen.blit(img_face_success, (face_pos_x, face_pos_y))
        else:
            screen.blit(img_face_normal, (face_pos_x, face_pos_y))

        pygame.display.update()


record_thread = threading.Thread(target=record_voice)
record_thread.daemon = True
main()
