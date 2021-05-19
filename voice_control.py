import time
import wave
import numpy as np
import pyaudio
from aip import AipSpeech

APP_ID = '24142986'
API_KEY = 'lz8wrZPBovwoWXqpL2FRBtDX'
SECRET_KEY = '34kKxkbMKB8VaqWZRQxV1y4QbPNW0xkG'

client = AipSpeech(APP_ID, API_KEY, SECRET_KEY)


CHUNK = 1024
FORMAT = pyaudio.paInt16  # 16bit编码格式
CHANNELS = 1  # 单声道
RATE = 16000  # 16000采样频率

def get_file_content(file_path):
    with open(file_path, 'rb') as fp:
        return fp.read()

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
            # print("检测到信号")
            # print('当前阈值：', temp1)
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

    if result == "你好。":
        print("你也好")
    elif result == "结束。":
        break
    else:
        print(result)