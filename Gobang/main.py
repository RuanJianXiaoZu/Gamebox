import game
import wave
import pygame
import pyaudio
import threading
import numpy as np
from aip import AipSpeech

ROWS = 17
SIDE = 30

SCREEN_WIDTH = ROWS * SIDE
SCREEN_HEIGHT = ROWS * SIDE

EMPTY = -1
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
DIRE = [(1, 0), (0, 1), (1, 1), (1, -1)]


class Gobang(game.Game):
    def __init__(self, title, size, fps=15):
        super(Gobang, self).__init__(title, size, fps)
        self.x = 8
        self.y = 8
        self.chess = []
        self.black = True
        self.end = False
        self.board = [[EMPTY for i in range(ROWS)] for j in range(ROWS)]
        self.draw_board()
        now = BLACK if self.black else WHITE
        pygame.draw.rect(self.screen, now, (8 * SIDE, 8 * SIDE, SIDE, SIDE), 1)
        pygame.display.update()
        self.bind_click(1, self.click)

    def move(self, direction):
        if direction == 'u':
            if self.x > 0:
                self.x = self.x - 1
            else:
                return
        elif direction == 'd':
            if self.x < 16:
                self.x = self.x + 1
            else:
                return
        elif direction == 'l':
            if self.y > 0:
                self.y = self.y - 1
            else:
                return
        elif direction == 'r':
            if self.y < 16:
                self.y = self.y + 1
            else:
                return
        self.draw_all_chess()
        i, j = self.x, self.y
        now = BLACK if self.black else WHITE
        pygame.draw.rect(self.screen, now, (j * SIDE, i * SIDE, SIDE, SIDE), 1)
        pygame.display.update()

    def select(self):
        self.confirm(self.x, self.y)

    def click(self, x, y):
        if self.end:
            return
        i, j = y // SIDE, x // SIDE
        self.x = i
        self.y = j
        self.confirm(i, j)

    def confirm(self, i, j):
        if self.board[i][j] != EMPTY:
            return
        self.board[i][j] = BLACK if self.black else WHITE
        self.chess.append((self.board[i][j], i, j))
        self.draw_all_chess()
        self.black = not self.black
        self.board[i][j] = BLACK if self.black else WHITE
        pygame.draw.rect(self.screen, self.board[i][j], (j * SIDE, i * SIDE, SIDE, SIDE), 1)
        pygame.display.update()

        chess = self.check_win()
        if chess:
            self.end = True
            i, j = chess[0]
            winner = "Black"
            if self.board[i][j] == WHITE:
                winner = "White"
            pygame.display.set_caption("五子棋 ---- %s win!" % winner)
            for c in chess:
                i, j = c
                self.draw_chess((100, 255, 255), i, j)
                self.timer.tick(5)

    def check_win(self):
        for i in range(ROWS):
            for j in range(ROWS):
                win = self.check_chess(i, j)
                if win:
                    return win
        return None

    def check_chess(self, i, j):
        if self.board[i][j] == EMPTY:
            return None
        color = self.board[i][j]
        for dire in DIRE:
            x, y = i, j
            chess = []
            while self.board[x][y] == color:
                chess.append((x, y))
                x, y = x+dire[0], y+dire[1]
                if x < 0 or y < 0 or x >= ROWS or y >= ROWS:
                    break
            if len(chess) >= 5:
                return chess
        return None

    def draw_all_chess(self):
        self.draw_board()
        for c in self.chess:
            color, i, j = c
            self.draw_chess(color, i, j)
        pygame.display.update()

    def draw_chess(self, color, i, j):
        center = (j*SIDE+SIDE//2, i*SIDE+SIDE//2)
        pygame.draw.circle(self.screen, color, center, SIDE//2-2)

    def draw_board(self):
        self.screen.fill((139, 87, 66))
        for i in range(ROWS):
            start = (i*SIDE + SIDE//2, SIDE//2)
            end = (i*SIDE + SIDE//2, ROWS*SIDE - SIDE//2)
            pygame.draw.line(self.screen, 0x000000, start, end)
            start = (SIDE//2, i*SIDE + SIDE//2)
            end = (ROWS*SIDE - SIDE//2, i*SIDE + SIDE//2)
            pygame.draw.line(self.screen, 0x000000, start, end)
        center = ((ROWS//2)*SIDE+SIDE//2, (ROWS//2)*SIDE+SIDE//2)
        pygame.draw.circle(self.screen, (0, 0, 0), center, 4)
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

        result = ''.join(client.asr(get_file_content('1.wav'), 'wav', 16000, {
            'dev_pid': 1537,  # 默认1537（普通话 输入法模型），dev_pid参数见本节开头的表格
        })["result"])
        print(result)
        if result == "结束。":
            break
        elif result == "上。":
            gobang.move('u')
            continue
        elif result == "下。":
            gobang.move('d')
            continue
        elif result == "左。":
            gobang.move('l')
            continue
        elif result == "右。":
            gobang.move('r')
            continue
        elif result == "确认。":
            gobang.select()
            continue


if __name__ == '__main__':
    print('''
    Welcome to 五子棋!
    click LEFT MOUSE BUTTON to play game.
    ''')
    record_thread = threading.Thread(target=record_voice)
    record_thread.setDaemon(True)
    record_thread.start()
    gobang = Gobang("五子棋", (SCREEN_WIDTH, SCREEN_HEIGHT))
    gobang.run()
