#!/usr/bin/env python
import time
import wave
import numpy as np
from aip import AipSpeech
import os, random
import tkinter as tk
import tkinter.messagebox
import pyaudio
import threading
from PIL import Image, ImageTk

#from voice_control import voice

dirname=os.path.split(os.path.abspath(__file__))[0]
os.chdir(dirname)

root = tk.Tk()

class MainWindow():
	__gameTitle = "连连看游戏"
	__windowWidth = 700
	__windowHeigth = 500
	__icons = []
	__gameSize = 10 # 游戏尺寸
	__iconKind = __gameSize * __gameSize / 4 # 小图片种类数量
	__iconWidth = 40
	__iconHeight = 40
	__map = [] # 游戏地图
	__delta = 25
	__isFirst = True
	__isGameStart = False
	__formerPoint = None
	EMPTY = -1
	NONE_LINK = 0
	STRAIGHT_LINK = 1
	ONE_CORNER_LINK = 2
	TWO_CORNER_LINK = 3

	def __init__(self):
		root.title(self.__gameTitle)
		self.centerWindow(self.__windowWidth, self.__windowHeigth)
		root.minsize(460, 460)

		self.__addComponets()
		self.extractSmallIconList()



	def __addComponets(self):
		self.menubar = tk.Menu(root, bg="lightgrey", fg="black")

		self.file_menu = tk.Menu(self.menubar, tearoff=0, bg="lightgrey", fg="black")
		self.file_menu.add_command(label="新游戏", command=self.file_new, accelerator="Ctrl+N")

		self.menubar.add_cascade(label="游戏", menu=self.file_menu)
		root.configure(menu=self.menubar)

		self.canvas = tk.Canvas(root, bg = 'white', width = 450, height = 450)
		self.canvas.pack(side=tk.TOP, pady = 5)
		self.canvas.bind('<Button-1>', self.clickCanvas)
        

	def centerWindow(self, width, height):
		screenwidth = root.winfo_screenwidth()
		screenheight = root.winfo_screenheight()
		size = '%dx%d+%d+%d' % (width, height, (screenwidth - width)/2, (screenheight - height)/2)
		root.geometry(size)


	def file_new(self, event=None):
		self.iniMap()
		self.drawMap()
		self.__isGameStart = True

    
	def clickCanvas(self, event):
		if self.__isGameStart:
			point = self.getInnerPoint(Point(event.x, event.y))
			# 有效点击坐标
			if point.isUserful() :
				if self.__isFirst:
					self.drawSelectedArea(point)
					self.__isFirst= False
					self.__formerPoint = point
				else:
					if self.__formerPoint.isEqual(point):
						self.__isFirst = True
						self.canvas.delete("rectRedOne")
					else:
						linkType = self.getLinkType(self.__formerPoint, point)
						if linkType['type'] != self.NONE_LINK:
							# TODO Animation
							self.ClearLinkedBlocks(self.__formerPoint, point)
							self.canvas.delete("rectRedOne")
							self.__isFirst = True
							if self.isGameEnd():
								tk.messagebox.showinfo("You Win!", "Tip")
								self.__isGameStart = False
						else:
							self.__formerPoint = point
							self.canvas.delete("rectRedOne")
							self.drawSelectedArea(point)


	# 判断游戏是否结束
	def isGameEnd(self):
		for y in range(0, self.__gameSize):
			for x in range(0, self.__gameSize):
				if self.__map[y][x] != self.EMPTY:
					return False
		return True

							

	'''
	提取小头像数组
	'''
	def extractSmallIconList(self):
		imageSouce = Image.open('图片/NARUTO.png')
		for index in range(0, int(self.__iconKind)):
			region = imageSouce.crop((self.__iconWidth * index, 0, 
					self.__iconWidth * index + self.__iconWidth - 1, self.__iconHeight - 1))
			self.__icons.append(ImageTk.PhotoImage(region))

	'''
	初始化地图 存值为0-24
	'''
	def iniMap(self):
		self.__map = [] # 重置地图
		tmpRecords = []
		records = []
		for i in range(0, int(self.__iconKind)):
			for j in range(0, 4):
				tmpRecords.append(i)

		total = self.__gameSize * self.__gameSize
		for x in range(0, total):
			index = random.randint(0, total - x - 1)
			records.append(tmpRecords[index])
			del tmpRecords[index]

		# 一维数组转为二维，y为高维度
		for y in range(0, self.__gameSize):
			for x in range(0, self.__gameSize):
				if x == 0:
					self.__map.append([])
				self.__map[y].append(records[x + y * self.__gameSize])

	'''
	根据地图绘制图像
	'''
	def drawMap(self):
		self.canvas.delete("all")
		for y in range(0, self.__gameSize):
			for x in range(0, self.__gameSize):
				point = self.getOuterLeftTopPoint(Point(x, y))
				im = self.canvas.create_image((point.x, point.y), 
					image=self.__icons[self.__map[y][x]], anchor='nw', tags = 'im%d%d' % (x, y))

	'''
	获取内部坐标对应矩形左上角顶点坐标
	'''
	def getOuterLeftTopPoint(self, point):
		return Point(self.getX(point.x), self.getY(point.y))

	'''
	获取内部坐标对应矩形中心坐标
	'''
	def getOuterCenterPoint(self, point):
		return Point(self.getX(point.x) + int(self.__iconWidth / 2), 
				self.getY(point.y) + int(self.__iconHeight / 2))
		
	def getX(self, x):
		return x * self.__iconWidth + self.__delta

	def getY(self, y):
		return y * self.__iconHeight + self.__delta

	'''
	上下左右移动
	'''
	def right(self, point):
		if point.x==0:
			return Point(9, point.y)
		else:
			return Point(point.x+1, point.y)
	
	def left(self, point):
		if point.x==9:
			return Point(0, point.y)
		else:
			return Point(point.x-1, point.y)
	
	def up(self, point):
		if point.y==0:
			return Point(point.x, 9)
		else:
			return Point(point.x, point.y-1)
	
	def down(self, point):
		if point.y==9:
			return Point(point.x, 0)
		else:
			return Point(point.x, point.y+1)

	def voice(self):
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
			print(result)
			
			if result=="语音控制。":	
				point = Point(5, 5)
				self.drawSelectedArea(point)
				continue
			if result=="结束":
				exit(0)
			if result=="新游戏。":	
				self.file_new()
				point = Point(5, 5)
				self.drawSelectedArea(point)
				continue
			if result=="向左。":
				self.canvas.delete("rectRedOne")
				point = self.left(point)
				self.drawSelectedArea(point)
				continue
			if result=="向右。":
				self.canvas.delete("rectRedOne")
				point = self.right(point)
				self.drawSelectedArea(point)
				continue
			if result=="向上。":
				self.canvas.delete("rectRedOne")
				point = self.up(point)
				self.drawSelectedArea(point)
				continue
			if result=="向下。":
				self.canvas.delete("rectRedOne")
				point = self.down(point)
				self.drawSelectedArea(point)
				continue
			if self.__isFirst== False:
				self.drawSelectedArea(self.__formerPoint)
			if result=="确定。":
				if point.isUserful() :
					if self.__isFirst:
						self.drawSelectedArea(point)
						self.__isFirst= False
						self.__formerPoint = point
						point = Point(5, 5)
						self.drawSelectedArea(point)
					else:
						if self.__formerPoint.isEqual(point):
							self.__isFirst = True
							self.canvas.delete("rectRedOne")
							point = Point(5, 5)
							self.drawSelectedArea(point)
						else:
							linkType = self.getLinkType(self.__formerPoint, point)
							if linkType['type'] != self.NONE_LINK:
								# TODO Animation
								self.ClearLinkedBlocks(self.__formerPoint, point)
								self.canvas.delete("rectRedOne")
								self.__isFirst = True
								if self.isGameEnd():
									tk.messagebox.showinfo("You Win!", "Tip")
									self.__isGameStart = False
								point = Point(5, 5)
								self.drawSelectedArea(point)	
							else:
								self.__formerPoint = point
								self.canvas.delete("rectRedOne")
								self.drawSelectedArea(point)
								point = Point(5, 5)
								self.drawSelectedArea(point)	
				continue
	'''
	获取内部坐标
	'''
	def getInnerPoint(self, point):
		x = -1
		y = -1

		for i in range(0, self.__gameSize):
			x1 = self.getX(i)
			x2 = self.getX(i + 1)
			if point.x >= x1 and point.x < x2:
				x = i

		for j in range(0, self.__gameSize):
			j1 = self.getY(j)
			j2 = self.getY(j + 1)
			if point.y >= j1 and point.y < j2:
				y = j

		return Point(x, y)

	'''
	选择的区域变红，point为内部坐标
	'''
	def drawSelectedArea(self, point):
		pointLT = self.getOuterLeftTopPoint(point)
		pointRB = self.getOuterLeftTopPoint(Point(point.x + 1, point.y + 1))
		self.canvas.create_rectangle(pointLT.x, pointLT.y, 
				pointRB.x - 1, pointRB.y - 1, outline = 'red', tags = "rectRedOne")


	'''
	消除连通的两个块
	'''
	def ClearLinkedBlocks(self, p1, p2):
		self.__map[p1.y][p1.x] = self.EMPTY
		self.__map[p2.y][p2.x] = self.EMPTY
		self.canvas.delete('im%d%d' % (p1.x, p1.y))
		self.canvas.delete('im%d%d' % (p2.x, p2.y))

	'''
	地图上该点是否为空
	'''
	def isEmptyInMap(self, point):
		if self.__map[point.y][point.x] == self.EMPTY:
			return True
		else:
			return False

	'''
	获取两个点连通类型
	'''
	def getLinkType(self, p1, p2):
		# 首先判断两个方块中图片是否相同
		if self.__map[p1.y][p1.x] != self.__map[p2.y][p2.x]:
			return { 'type': self.NONE_LINK }

		if self.isStraightLink(p1, p2):
			return {
				'type': self.STRAIGHT_LINK
			}
		res = self.isOneCornerLink(p1, p2)
		if res:
			return {
				'type': self.ONE_CORNER_LINK,
				'p1': res
			}
		res = self.isTwoCornerLink(p1, p2)
		if res:
			return {
				'type': self.TWO_CORNER_LINK,
				'p1': res['p1'],
				'p2': res['p2']
			}
		return {
			'type': self.NONE_LINK
		}


	'''
	直连
	'''
	def isStraightLink(self, p1, p2):
		start = -1
		end = -1
		# 水平
		if p1.y == p2.y:
			# 大小判断
			if p2.x < p1.x:
				start = p2.x
				end = p1.x
			else:
				start = p1.x
				end = p2.x
			for x in range(start + 1, end):
				if self.__map[p1.y][x] != self.EMPTY:
					return False
			return True
		elif p1.x == p2.x:
			if p1.y > p2.y:
				start = p2.y
				end = p1.y
			else:
				start = p1.y
				end = p2.y
			for y in range(start + 1, end):
				if self.__map[y][p1.x] != self.EMPTY:
					return False
			return True
		return False

	def isOneCornerLink(self, p1, p2):
		pointCorner = Point(p1.x, p2.y)
		if self.isStraightLink(p1, pointCorner) and self.isStraightLink(pointCorner, p2) and self.isEmptyInMap(pointCorner):
			return pointCorner

		pointCorner = Point(p2.x, p1.y)
		if self.isStraightLink(p1, pointCorner) and self.isStraightLink(pointCorner, p2) and self.isEmptyInMap(pointCorner):
			return pointCorner

	def isTwoCornerLink(self, p1, p2):
		for y in range(-1, self.__gameSize + 1):
			pointCorner1 = Point(p1.x, y)
			pointCorner2 = Point(p2.x, y)
			if y == p1.y or y == p2.y:
				continue
			if y == -1 or y == self.__gameSize:
				if self.isStraightLink(p1, pointCorner1) and self.isStraightLink(pointCorner2, p2):
					return {'p1': pointCorner1, 'p2': pointCorner2}
			else:
				if self.isStraightLink(p1, pointCorner1) and self.isStraightLink(pointCorner1, pointCorner2) and self.isStraightLink(pointCorner2, p2) and self.isEmptyInMap(pointCorner1) and self.isEmptyInMap(pointCorner2):
					return {'p1': pointCorner1, 'p2': pointCorner2}

		# 横向判断
		for x in range(-1, self.__gameSize + 1):
			pointCorner1 = Point(x, p1.y)
			pointCorner2 = Point(x, p2.y)
			if x == p1.x or x == p2.x:
				continue
			if x == -1 or x == self.__gameSize:
				if self.isStraightLink(p1, pointCorner1) and self.isStraightLink(pointCorner2, p2):
					return {'p1': pointCorner1, 'p2': pointCorner2}
			else:
				if self.isStraightLink(p1, pointCorner1) and self.isStraightLink(pointCorner1, pointCorner2) and self.isStraightLink(pointCorner2, p2) and self.isEmptyInMap(pointCorner1) and self.isEmptyInMap(pointCorner2):
					return {'p1': pointCorner1, 'p2': pointCorner2}


class Point():
	def __init__(self, x, y):
		self.x = x
		self.y = y

	def isUserful(self):
		if self.x >= 0 and self.y >= 0:
			return True
		else:
			return False
					
	'''
	判断两个点是否相同
	'''
	def isEqual(self, point):
		if self.x == point.x and self.y == point.y:
			return True
		else:
			return False

	'''
	克隆一份对象
	'''
	def clone(self):
		return Point(self.x, self.y)


	'''
	改为另一个对象
	'''
	def changeTo(self, point):
		self.x = point.x
		self.y = point.y



m = MainWindow()
record_thread =threading.Thread(target=MainWindow.voice, args=[m, ])
record_thread.daemon = True
record_thread.start()
root.mainloop()

