import os
import sys
import cfg
import random
import pygame
from pygame import event
from pygame.constants import USEREVENT
import threading
import wave
import numpy as np
import pyaudio
from aip import AipSpeech


'''判断游戏是否结束'''
def isGameOver(board, size):
    assert isinstance(size, int)
    num_cells = size * size
    for i in range(num_cells-1):
        if board[i] != i: return False
    return True


'''将空白Cell左边的Cell右移到空白Cell位置'''
def moveR(board, blank_cell_idx, num_cols):
    if blank_cell_idx % num_cols == 0: return blank_cell_idx
    board[blank_cell_idx-1], board[blank_cell_idx] = board[blank_cell_idx], board[blank_cell_idx-1]
    return blank_cell_idx - 1


'''将空白Cell右边的Cell左移到空白Cell位置'''
def moveL(board, blank_cell_idx, num_cols):
    if (blank_cell_idx+1) % num_cols == 0: return blank_cell_idx
    board[blank_cell_idx+1], board[blank_cell_idx] = board[blank_cell_idx], board[blank_cell_idx+1]
    return blank_cell_idx + 1


'''将空白Cell上边的Cell下移到空白Cell位置'''
def moveD(board, blank_cell_idx, num_cols):
    if blank_cell_idx < num_cols: return blank_cell_idx
    board[blank_cell_idx-num_cols], board[blank_cell_idx] = board[blank_cell_idx], board[blank_cell_idx-num_cols]
    return blank_cell_idx - num_cols


'''将空白Cell下边的Cell上移到空白Cell位置'''
def moveU(board, blank_cell_idx, num_rows, num_cols):
    if blank_cell_idx >= (num_rows-1) * num_cols: return blank_cell_idx
    board[blank_cell_idx+num_cols], board[blank_cell_idx] = board[blank_cell_idx], board[blank_cell_idx+num_cols]
    return blank_cell_idx + num_cols


'''获得打乱的拼图'''
def CreateBoard(num_rows, num_cols, num_cells):
    board = []
    for i in range(num_cells): board.append(i)
    # 去掉右下角那块
    blank_cell_idx = num_cells - 1
    board[blank_cell_idx] = -1
    for i in range(cfg.NUMRANDOM):
        # 0: left, 1: right, 2: up, 3: down
        direction = random.randint(0, 3)
        if direction == 0: blank_cell_idx = moveL(board, blank_cell_idx, num_cols)
        elif direction == 1: blank_cell_idx = moveR(board, blank_cell_idx, num_cols)
        elif direction == 2: blank_cell_idx = moveU(board, blank_cell_idx, num_rows, num_cols)
        elif direction == 3: blank_cell_idx = moveD(board, blank_cell_idx, num_cols)
    return board, blank_cell_idx


'''随机选取一张图片'''
def GetImagePath(rootdir):
    imagenames = os.listdir(rootdir)
    assert len(imagenames) > 0
    return os.path.join(rootdir, random.choice(imagenames))


'''显示游戏结束界面'''
def ShowEndInterface(screen, width, height):
    screen.fill(cfg.BACKGROUNDCOLOR)
    font = pygame.font.Font(cfg.FONTPATH, width//15)
    title = font.render('恭喜! 你成功完成了拼图!', True, (233, 150, 122))
    rect = title.get_rect()
    rect.midtop = (width/2, height/2.5)
    screen.blit(title, rect)
    pygame.display.update()
    while True:
        for event in pygame.event.get():
            if (event.type == pygame.QUIT) or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                pygame.quit()
                sys.exit()
        pygame.display.update()


'''显示游戏开始界面'''
def ShowStartInterface(screen, width, height):
    screen.fill(cfg.BACKGROUNDCOLOR)
    tfont = pygame.font.Font(cfg.FONTPATH, width//4)
    cfont = pygame.font.Font(cfg.FONTPATH, width//20)
    title = tfont.render('拼图游戏', True, cfg.RED)
    content1 = cfont.render('简单模式(L) 3x3', True, cfg.BLUE)
    content2 = cfont.render('中等模式(M) 4x4', True, cfg.BLUE)
    content3 = cfont.render('困难模式(H) 5x5', True, cfg.BLUE)
    trect = title.get_rect()
    trect.midtop = (width/2, height/10)
    crect1 = content1.get_rect()
    crect1.midtop = (width/2, height/2.2)
    crect2 = content2.get_rect()
    crect2.midtop = (width/2, height/1.8)
    crect3 = content3.get_rect()
    crect3.midtop = (width/2, height/1.5)
    screen.blit(title, trect)
    screen.blit(content1, crect1)
    screen.blit(content2, crect2)
    screen.blit(content3, crect3)
    while True:
        for event in pygame.event.get():
            if (event.type == pygame.QUIT) or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE) or (event.type == USEREVENT + 2):
                isOver = True
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == ord('l'): return 3
                elif event.key == ord('m'): return 4
                elif event.key == ord('h'): return 5
            elif event.type == USEREVENT + 2: return 3
            elif event.type == USEREVENT + 3: return 4
            elif event.type == USEREVENT + 4: return 5
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

        if result == "结束。":
            my_event = event.Event(USEREVENT + 2)
            event.post(my_event)
            break
        elif result == "简单模式。":
            my_event = event.Event(USEREVENT + 3)
            event.post(my_event)
            continue
        elif result == "中等模式。":
            my_event = event.Event(USEREVENT + 4)
            event.post(my_event)
            continue
        elif result == "困难模式。":
            my_event = event.Event(USEREVENT + 5)
            event.post(my_event)
            continue
        elif result == "向左。":
            my_event = event.Event(USEREVENT + 6)
            event.post(my_event)
            continue
        elif result == "向右。":
            my_event = event.Event(USEREVENT + 7)
            event.post(my_event)
            continue
        elif result == "向上。":
            my_event = event.Event(USEREVENT + 8)
            event.post(my_event)
            continue
        elif result == "向下。":
            my_event = event.Event(USEREVENT + 9)
            event.post(my_event)
            continue


'''主函数'''
def main():
    # 初始化
    pygame.init()
    clock = pygame.time.Clock()
    # 加载图片
    game_img_used = pygame.image.load(GetImagePath(cfg.PICTURE_ROOT_DIR))
    game_img_used = pygame.transform.scale(game_img_used, cfg.SCREENSIZE)
    game_img_used_rect = game_img_used.get_rect()
    # 设置窗口
    screen = pygame.display.set_mode(cfg.SCREENSIZE)
    pygame.display.set_caption('拼图游戏')
    # 游戏开始界面
    record_thread.start()
    size = ShowStartInterface(screen, game_img_used_rect.width, game_img_used_rect.height)
    assert isinstance(size, int)
    num_rows, num_cols = size, size
    num_cells = size * size
    # 计算Cell大小
    cell_width = game_img_used_rect.width // num_cols
    cell_height = game_img_used_rect.height // num_rows
    # 避免初始化为原图
    while True:
        game_board, blank_cell_idx = CreateBoard(num_rows, num_cols, num_cells)
        if not isGameOver(game_board, size):
            break
    # 游戏主循环
    is_running = True
    while is_running:
        # --事件捕获
        for event in pygame.event.get():
            # ----退出游戏
            if (event.type == pygame.QUIT) or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE) or (event.type == USEREVENT + 2):
                isOver = True
                pygame.quit()
                sys.exit()
            # ----键盘操作
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT or event.key == ord('a'):
                    blank_cell_idx = moveL(game_board, blank_cell_idx, num_cols)
                elif event.key == pygame.K_RIGHT or event.key == ord('d'):
                    blank_cell_idx = moveR(game_board, blank_cell_idx, num_cols)
                elif event.key == pygame.K_UP or event.key == ord('w'):
                    blank_cell_idx = moveU(game_board, blank_cell_idx, num_rows, num_cols)
                elif event.key == pygame.K_DOWN or event.key == ord('s'):
                    blank_cell_idx = moveD(game_board, blank_cell_idx, num_cols)
            # ----鼠标操作
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                x, y = pygame.mouse.get_pos()
                x_pos = x // cell_width
                y_pos = y // cell_height
                idx = x_pos + y_pos * num_cols
                if idx == blank_cell_idx-1:
                    blank_cell_idx = moveR(game_board, blank_cell_idx, num_cols)
                elif idx == blank_cell_idx+1:
                    blank_cell_idx = moveL(game_board, blank_cell_idx, num_cols)
                elif idx == blank_cell_idx+num_cols:
                    blank_cell_idx = moveU(game_board, blank_cell_idx, num_rows, num_cols)
                elif idx == blank_cell_idx-num_cols:
                    blank_cell_idx = moveD(game_board, blank_cell_idx, num_cols)
            # ----语音操作
            elif event.type == USEREVENT + 6:
                blank_cell_idx = moveL(game_board, blank_cell_idx, num_cols)
            elif event.type == USEREVENT + 7:
                blank_cell_idx = moveR(game_board, blank_cell_idx, num_cols)
            elif event.type == USEREVENT + 8:
                blank_cell_idx = moveU(game_board, blank_cell_idx, num_rows, num_cols)
            elif event.type == USEREVENT + 9:
                blank_cell_idx = moveD(game_board, blank_cell_idx, num_cols)

        # --判断游戏是否结束
        if isGameOver(game_board, size):
            game_board[blank_cell_idx] = num_cells - 1
            is_running = False
        # --更新屏幕
        screen.fill(cfg.BACKGROUNDCOLOR)
        for i in range(num_cells):
            if game_board[i] == -1:
                continue
            x_pos = i // num_cols
            y_pos = i % num_cols
            rect = pygame.Rect(y_pos*cell_width, x_pos*cell_height, cell_width, cell_height)
            img_area = pygame.Rect((game_board[i]%num_cols)*cell_width, (game_board[i]//num_cols)*cell_height, cell_width, cell_height)
            screen.blit(game_img_used, rect, img_area)
        for i in range(num_cols+1):
            pygame.draw.line(screen, cfg.BLACK, (i*cell_width, 0), (i*cell_width, game_img_used_rect.height))
        for i in range(num_rows+1):
            pygame.draw.line(screen, cfg.BLACK, (0, i*cell_height), (game_img_used_rect.width, i*cell_height))
        pygame.display.update()
        clock.tick(cfg.FPS)
    # 游戏结束界面
    ShowEndInterface(screen, game_img_used_rect.width, game_img_used_rect.height)


record_thread = threading.Thread(target=record_voice)
record_thread.daemon = True
main()