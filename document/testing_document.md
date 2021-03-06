# 测试文档
## 主界面测试方式
+ 说出游戏名称或点击相应按钮进入相应游戏
+ 说“退出”或点击退出按钮退出程序。
## 象棋联机游戏测试方式
+ 开始象棋联机游戏前需为服务器与客户端配置相应ip地址，使得服务器与客户端能够相互通信。配置完毕后开启服务器。
+ 开启客户端，说出或输入自己的ID，说确认或点击确认按钮向服务器发送自己的ID，服务器返回在线的用户列表。
+ 说出“关闭”或点击退出按钮以退出客户端。
+ 说出或点击任意在线用户的ID，若该用户为空闲状态则向该用户发送对弈邀请，若该用户为游戏状态则向该用户发送预约。
+ 若接收到其他用户发来的邀请或预约，说出“接受/拒绝”或点击接受/拒绝按钮回复该用户。
+ 若接受了其他用户的对弈邀请或其他用户接受了自己发出的对弈邀请则进入游戏界面。
+ 在游戏界面说出例如“炮二平五、兵五进一”等象棋谱法或依次点击想要移动的棋子和想要移动的位置进行行棋。
+ 在游戏界面说出“结束”以退出对局，若此时棋局未结束则会告知对手你已经逃跑。
## 象棋单机游戏测试方式
+ 说出“开始”或点击新游戏以开始新一局对局。
+ 行棋方法与联机游戏相同。
+ 说出“存档”或点击存档按钮可以保存当前盘面。
+ 说出“读档”或点击读档按钮可以将盘面恢复成读档时的情况。
+ 说出“悔棋”或点击悔一步按钮可以悔一步棋。
+ 说出“结束”可以退出游戏。
## 连连看测试方式
+ 说“新游戏”开始新游戏，自动选中中间的方块。
+ 说“向上”，“向下”，“向左”，“向右”移动选中的内容。
+ 说“确定”选中该方块，继续选择下一个方块。
+ 若想在鼠标操作后用语音继续游戏，说“语音控制”即可。
+ 说“退出”，关闭游戏。
## 拼图测试方式
+ 说“简单模式” / “中等模式” / “困难模式”，选择游戏难度。
+ 说“向上”，“向下”，“向左”，“向右”移动拼图方块。
+ 说“结束”，关闭游戏。
## 推箱子测试方式
+ 说“开始游戏”，进入第一关。
+ 说“向上”，“向下”，“向左”，“向右”移动推箱子。
+ 说“重新开始”，可重新进入本关卡。
+ 说“结束”，关闭游戏。
## 五子棋测试方式
+ 说“向上”，“向下”，“向左”，“向右”移动预选框。
+ 说“确认”，在预选框选中的位置落子。
+ 说“结束”，关闭游戏。

## 扫雷测试方式

- 说“初级” / “中级” / “高级”，或者键盘按下"l"/"m"/"h"选择游戏难度。
- 鼠标点击进行游戏和重新开始。
- 说“结束”，关闭游戏。