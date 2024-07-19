import math
import os
import pickle
import tkinter
import tkinter as tk
import random
from tkinter import messagebox, simpledialog
from tkinter import scrolledtext
# from tkinter import font
from tkinter import ttk
import threading

# 是否以测试符号的堆的开局
FLAG_TEST = 0
FLAG_DEBUG_MESSAGEBOX = False
CONST_BASE_HIT_FREQ = 0.24
CONST_BONUS_HIT_FREQ = 0.01
CONST_BONUS_FIRST_8_SPINS = [0, 0.16, 0.14, 0.12, 0.10, 0.06, 0.04, 0.03, 0.02]

CONST_TASK_TIME = 900
CONST_EMERGENCY_TASK_TIME = 600
CONST_SPIN_SPEED = 1875
CONST_BONUS_TITLE = ["Regular Bonus", "Premium Bonus", "Persistent Bonus",
                     "Persistent Bonus: Shapeshifter", "Persistent Bonus: Arms Dealer, +5 Symbols",
                     "2 Persistent Bonus",
                     "2 Persistent Bonus, +1 Extra Chance", "3 Persistent Bonus",
                     "3 Persistent Bonus: Shapeshifter, Arms Dealer, Necromancer, +2 Symbols",
                     "4 Persistent Bonus", "Premium 4 Persistent Bonus, +2 Symbols",
                     "5 Persistent Bonus",
                     "5 Persistent Bonus, +2 Symbols, +1 Extra Chance",
                     "Premium 5 Persistent Bonus, +3 Symbols, +2 Extra Chance",
                     "Premium 5 Persistent Bonus: 5x Shapeshifter, +3 Symbols, +2 Extra Chance", ]


class Profile:
    def __init__(self):
        self.Star_record = 0
        self.EXP = 0
        self.Achievements = []
        for i in range(0, 1000):
            self.Achievements.append(False)
        self.Highscore = []
        for i in range(0, 100):
            self.Highscore.append(0)

    def GetProgress(self):
        M = 1000 * 1000
        B = 1000 * M
        T = 1000 * B
        Req = [0,
               0, 1200, 4200, 14000, 45000,
               153000, 486000, 1920000, 5600000, 16800000,
               76.8 * M, 328 * M, 1.35 * B, 63 * B, 17.5 * T, 640 * T, 3200 * T]
        if self.EXP < Req[len(Req) - 2]:
            Level = 0
            while Level < len(Req) - 2:
                if self.EXP >= Req[Level + 1]:
                    Level += 1
                else:
                    break
            Percentage = 100.00 * (self.EXP - Req[Level]) / (Req[Level + 1] - Req[Level])
        else:
            CONST_EXP_FACTOR = 5
            Level = len(Req) - 2
            tempEXP = 1.0 * self.EXP
            tempEXP /= 9600000
            while tempEXP >= CONST_EXP_FACTOR:
                tempEXP /= CONST_EXP_FACTOR
                Level += 1
            Percentage = 100.00 * (tempEXP - 1.0) / CONST_EXP_FACTOR
        return [f"Level: {Level}, EXP: {self.EXP:,} ({Percentage:.2f}%)", Level, Percentage]


# 创建一个Tkinter窗口
root = tk.Tk()
# 隐藏主窗口
root.withdraw()

# 弹出输入框，提示用户输入文件名
file_path = simpledialog.askstring("Input", "Input profile name, or leave blank for default", parent=root)

# 检查文件是否存在当前目录下
if file_path == "":
    file_path = "default"

# 销毁Tkinter主窗口
root.destroy()

file_path += ".profile"
if not os.path.exists(file_path) or os.path.getsize(file_path) == 0:
    PlayerProfile = Profile()
else:

    with open(file_path, 'rb') as file:
        try:
            obj = pickle.load(file)
            # 检查对象是否与MyClass兼容
            if isinstance(obj, Profile):
                PlayerProfile = obj
            else:
                PlayerProfile = Profile()
        except Exception as e:
            print(f"Error during unpickling object (Possibly incompatible): {e}")

    # 处理用户输入


class TaskManager:
    def __init__(self):
        self.TaskList = []
        self.TaskDuration = []
        self.EmergencyTaskLeft = 0
        self.Active = False
        self.DefaultTimer = None
        self.Flag_Ongoing_Task = False

    def Reset(self):
        self.TaskList = []
        self.TaskDuration = []
        self.EmergencyTaskLeft = 0
        self.Active = False
        # 取消正在进行中的任务的
        if self.DefaultTimer is not None:
            self.DefaultTimer.cancel()
            # print("TIMER STOPPED")
        self.Flag_Ongoing_Task = False

    def isActive(self):
        return self.Active

    def TurnOn(self):

        self.Active = True
        if len(self.TaskList) > 0:
            duration = self.TaskDuration.pop(0)
            self.Wait(duration)

    def TurnOff(self):

        self.Active = False

    def Wait(self, t):

        if self.Active:
            # Timer accepts seconds, hence divide by 1000
            self.DefaultTimer = threading.Timer(t / 1000.0, self.Timer)
            self.DefaultTimer.start()

    def Timer(self):
        if not self.Active:
            return
        # print("Timer Call")
        # If there are emergency tasks left
        if self.EmergencyTaskLeft > 0:
            self.EmergencyTaskLeft -= 1

        # Execute the first task if available
        if len(self.TaskList) > 0:
            task = self.TaskList.pop(0)
            task()

            # Wait for the next task if available
            if len(self.TaskList) > 0 and len(self.TaskDuration) > 0:
                duration = self.TaskDuration.pop(0)
                self.Wait(duration)
            else:
                self.TurnOff()
        else:
            self.TurnOff()

    def AddEmergencyTask(self, Method, Duration=CONST_EMERGENCY_TASK_TIME):
        # position = self.EmergencyTaskLeft
        self.TaskList.insert(0, Method)
        self.TaskDuration.insert(0, Duration)
        self.EmergencyTaskLeft += 1

    def AddTask(self, Method, Duration=CONST_TASK_TIME):
        self.TaskList.append(Method)
        self.TaskDuration.append(Duration)


def DisplayMsg(Message):
    # 创建一个基本的tk窗口，但不显示它
    FLAG = False
    # 暂时不弹出对话框
    if FLAG:
        root = tk.Tk()
        root.withdraw()  # 隐藏主窗口

        # 显示消息框，要求用户确认
        messagebox.showinfo("EVENT", Message)

        # 销毁tk窗口
        root.destroy()


def DisplayHighscore(root, TargetProfile=PlayerProfile):
    TL = tkinter.Toplevel(root)
    TL.geometry("840x440")
    TL.resizable(False, False)

    TL.title("BIG NUMBER TRAIN.EXE - Highscore")

    label1 = tk.Label(TL, font=('Arial', 13, 'bold'),
                      text=f"Highscore\n{max(TargetProfile.Highscore):,}x\nHighest rank:\n{FormatStars(TargetProfile.Star_record)}\n",
                      anchor='w', justify='left')
    label1.place(x=20, y=10)
    # RANK
    # Mars(0)
    # Antarctica(1)
    # Africa(2)
    # China(3)
    # Asia(4)
    # Europe(5)
    # UK(6)
    # more tbd

    st1 = scrolledtext.ScrolledText(TL, font=('Arial', 11), width=500, height=260)
    st1.place(x=0, y=180)
    st1.insert(tk.END, "\n".join(CONST_BONUS_TITLE))
    st1.config(state=tk.DISABLED)

    st2 = scrolledtext.ScrolledText(TL, font=('Arial', 11), width=340, height=260)
    st2.place(x=500, y=180)
    for i in range(0, len(CONST_BONUS_TITLE)):
        if TargetProfile.Highscore[i] > 0:
            st2.insert(tk.END, f"{TargetProfile.Highscore[i]:,}x")
        else:
            st2.insert(tk.END, f"N/A")
        if i < len(CONST_BONUS_TITLE) - 1:
            st2.insert(tk.END, "\n")
    st2.config(state=tk.DISABLED)


class Round:
    def __init__(self):

        self.ExtraChance = 0
        self.HF_Bonus = False
        self.FLAG_GAME_OVER = False
        self.FLAG_DOOMSDAY = False
        # 特殊符号任务清单
        self.TaskList = TaskManager()

        # Flag1若为True, 则
        # 不输出 self.LogAndDisplayMsg(f"------ Collector Payer @ ({SourceBlock.X}, {SourceBlock.Y})'s turn! ------")
        # 等内容
        self.FLAG1 = False
        self.flag_full = False

        # self.LuckyDrawOption = IsLuckyDraw
        self.BonusType = -1

        self.PrevMultiplier = -1

        self.RoundCost = 100

        self.SpinsPlayed = 0
        # 初始化为0, 但购买奖励后则恢复为3或4
        self.SpinsLeft = 0
        self.UnlockedRows = 4
        self.ResetPlus1 = False

        self.TotalMultiplier = 0

        self.HitFreqX_Multi = 1.00
        self.HitFreqY_Multi = 1.00
        self.HitFreqZ_Multi = 1.00

        self.Blocks = []

        self.LogMessage = []

        if FLAG_TEST > 0:
            self.InitTestBlocks(FLAG_TEST)

        self.root = tk.Tk()
        self.root.geometry("1400x900")
        self.root.resizable(False, False)

        self.root.title("BIG NUMBER TRAIN.EXE")
        self.label1 = tk.Label(self.root, font=('Arial', 14, 'bold'))
        self.label1.place(x=30, y=90)
        self.label2 = tk.Label(self.root, font=('Arial', 14, 'bold'))
        self.label2.place(x=380, y=90)

        self.label3 = tk.Label(self.root, font=('Arial', 12, 'bold'), text="Feature in play\nNone")
        self.label3.place(x=265, y=800)

        self.Label4 = tk.Label(self.root, text=PlayerProfile.GetProgress()[0], font=('Arial', 12, 'bold'))
        self.Label4.place(x=30, y=40)

        # 进度条
        self.ProgressBar = ttk.Progressbar(self.root, orient="horizontal", length=400, mode="determinate")
        self.ProgressBar["maximum"] = 10000
        self.ProgressBar["value"] = int(PlayerProfile.GetProgress()[2] * 100)
        self.ProgressBar.place(x=30, y=10, width=400, height=30)

        # 需要先创建符号列表
        self.InitBlocks()

        self.Button1 = tk.Button(self.root, font=('Arial', 16, 'bold'), text="BUY\nFEATURE",
                                 command=lambda: self.PopupMenu())
        self.Button1.place(x=50, y=800, width=160, height=80)

        self.Button2 = tk.Button(self.root, font=('Arial', 16, 'bold'), text="Highscore",
                                 command=lambda root=self.root: DisplayHighscore(root))
        self.Button2.place(x=490, y=10, width=150, height=50)

        # 然后初始化
        self.UpdateUI()
        self.root.mainloop()

    def UpdateUI(self):
        # 标签1
        if self.BonusType < 0:
            self.label1.config(text=f"Click [BUY FEATURE] to begin!")
        else:
            if self.SpinsLeft > 0:
                self.label1.config(text=f"SPINS LEFT: " + "★" * self.ExtraChance + "●" * self.SpinsLeft)
            elif self.SpinsLeft <= 0 < self.ExtraChance:
                self.label1.config(text=f"SPINS LEFT: " + "★" * (self.ExtraChance - 1) + "☆" + "●" * self.SpinsLeft)
            else:
                self.label1.config(text=f"SPINS LEFT: " + "●" * self.SpinsLeft)

        # 标签2
        self.UpdateTotalMultiplier()
        if self.PrevMultiplier == -1 or self.PrevMultiplier == self.TotalMultiplier:
            self.label2.config(text="TOTAL: " + "{:,.0f}x".format(self.TotalMultiplier))
        else:
            self.label2.config(
                text="TOTAL: " + "{:,.0f}x -> {:,.0f}x".format(self.PrevMultiplier, self.TotalMultiplier))
        # 48个标签

        CONST_LABEL_WIDTH = 135
        CONST_LABEL_GAP = 2

        if not hasattr(self, "block_labels"):
            self.block_labels = []
            for j in range(8):
                for i in range(6):
                    label = tk.Label(self.root, bd=1, anchor='center', padx=5, pady=5,
                                     relief="solid", wraplength=9999)
                    label.place(x=30 + i * (CONST_LABEL_WIDTH + CONST_LABEL_GAP),
                                y=120 + j * 80, width=CONST_LABEL_WIDTH, height=78)  # 调整了块之间的间距
                    self.block_labels.append(label)

        for i in range(0, 48):
            text = ""
            label = self.block_labels[i]
            block = self.Blocks[i]
            # if block.IsNew and not block.IsUpdated and not block.IsAffected:
            # text += "(NEW!)\n"

            if block.Locked:
                label.config(bg="gray")
            elif block.IsUpdated:
                label.config(bg="#0FE864")  # GREEN
                block.IsUpdated = False
            elif block.IsAffected:
                label.config(bg="#FFF200")  # YELLOW
                block.IsAffected = False
            elif block.IsNew:
                label.config(bg='#56FFF0')  # LIGHT BLUE
            else:
                label.config(bg="white")

            if block.Type == 1:
                text += "{:,.0f}x".format(block.Value)
            elif block.Type == 2:
                # 如果雷管
                if block.Symbol == "Dynamite":
                    # print("Bomb incoming")
                    # 仅未爆炸的, 有速度值>0
                    if block.Speed > 0:
                        if not self.FLAG_GAME_OVER:
                            text += "Dynamite\n{:,.0f}x".format(block.Value)
                        else:
                            text += "Dynamite\n(Deactivated)\n{:,.0f}x".format(block.Value)
                    else:
                        text += "Dynamite\n(Exploded)\n{:,.0f}x".format(block.Value)
                        block.SetSymbol()
                else:
                    # print("DEBUG: TEXT=" + str(text))
                    # print("DEBUG: Symbol=" + str(block.Symbol))
                    text = str(text) + (block.Symbol + "\n{:,.0f}x".format(block.Value))
            elif block.Type == 3:
                if block.Symbol == "Shapeshifter" and block.Latest != "":
                    text += "**PERSISTENT**\n" + block.Latest + "\n{:,.0f}x".format(block.Value)

                else:
                    # print("DEBUG: TEXT=" + str(text))
                    # print("DEBUG: Symbol=" + str(block.Symbol))
                    text += "PERSISTENT\n" + (block.Symbol + "\n{:,.0f}x".format(block.Value))

            label.config(text=text)

            # 未激活的银框, 和金框, 用加粗表示
            if block.Symbol == "Dynamite" and self.FLAG_GAME_OVER:
                new_font = ("Microsoft YaHei UI", 9, "normal")
            elif block.Type == 3 or (block.Activated == False and block.Type == 2):
                new_font = ("Microsoft YaHei UI", 10, "bold")
            else:
                new_font = ("Microsoft YaHei UI", 9, "normal")
            label.config(font=new_font)

        # 日志文本框
        if not hasattr(self, "log_text"):
            self.log_text = scrolledtext.ScrolledText(self.root, width=54, height=40, state=tk.DISABLED)
            self.log_text.place(x=30 + 6.1 * (CONST_LABEL_WIDTH + CONST_LABEL_GAP), y=120)  # 调整了位置和大小
        else:
            self.log_text.config(state=tk.NORMAL)
            self.log_text.delete(1.0, tk.END)

        self.log_text.insert(tk.END, "\n".join(self.LogMessage))
        self.log_text.config(state=tk.DISABLED)
        self.log_text.see(tk.END)

        # self.button_spin = tk.Button(self.root, text="SPIN", width=15, height=3, command=self.Button_NextStep)
        # self.button_spin.place(x=80, y=720)

    def Button_NextStep(self):

        if self.TaskList.isActive():
            messagebox.showinfo("Cannot spin yet", "Feature symbols aren't done yet.")
            return

        if self.SpinsLeft > 0:
            self.Spin()
        else:
            messagebox.showinfo("Game Over", "Choose one of those Bonus Buy option to start a new round.")

    def PopupMenu(self):
        NewMenu = tkinter.Menu(tearoff=False)

        for i in range(0, len(CONST_BONUS_TITLE)):

            title = CONST_BONUS_TITLE[i]
            req_lv = i + 1
            flag_is_level_high_enough = (PlayerProfile.GetProgress()[1] >= req_lv)
            if flag_is_level_high_enough:

                NewMenu.add_command(label=title, command=lambda i=i, t=title: self.BONUS_BUY(i, t))
            else:

                NewMenu.add_command(label=title,
                                    command=lambda i=i, t=title: self.BONUS_BUY(i, t), state="disabled")  # 禁用的菜单项

        NewMenu.tk_popup(x=self.root.winfo_x() + 130, y=self.root.winfo_y() + 840)
        # self.Button1.place(x=50, y=800, width=160, height=80)

    def BONUS_BUY(self, BonusType, BonusTitle):

        if not self.FLAG_GAME_OVER and self.BonusType >= 0:
            UserInput = tkinter.messagebox.askyesno("Confirm",
                                                    "There's an ongoing round.\nStart a new round anyways?\n"
                                                    "You will not receive any EXP and refund.")
            if not UserInput:
                return
        if not tkinter.messagebox.askyesno("Bonus Buy", f"Buy the following feature?\n{BonusTitle}\nPrice:\nThe"
                                                        f" salesman is not here, so it's free today"):
            return
        self.ResetRound(BonusType)

    def SpinDone(self):

        for obj in self.Blocks:
            if obj.Type == 2 and obj.Symbol != "Dynamite" and not obj.Locked:
                obj.Activated = True
            obj.IsAffected = False
            obj.IsUpdated = False

        if self.ExtraChance > 0 and self.SpinsLeft == 0 and self.CountEmptySpace() > 0:
            self.UseExtraChance()
        else:
            self.LogMessage.append("======== SPIN FINISHED ========")
            self.UpdateUI()

    def ResetSymbols(self, UnlockAllRows=False):
        for i in range(0, 48):
            self.Blocks[i].SetSymbol(0)
            if (self.Blocks[i].Y <= 2 or self.Blocks[i].Y >= 7) and not UnlockAllRows:
                self.Blocks[i].Locked = True
            else:
                self.Blocks[i].Locked = False

    def do_nothing(self):
        pass

    def ResetRound(self, BonusOption=0):
        self.HF_Bonus = False

        self.FLAG_GAME_OVER = False
        self.FLAG_DOOMSDAY = False
        self.flag_full = False
        self.BonusType = BonusOption
        self.PrevMultiplier = -1
        self.ResetPlus1 = False
        self.RoundCost = GetRoundCost(self.BonusType)

        self.ResetSymbols()
        self.TaskList.Reset()

        # Premium模式: 以8行开始, 和Reset +1
        Flag_Premium = False

        # 对不同类型的奖励进行不同的初始化

        # 设置初始值
        Init_Symbol_Count = 3
        Init_Persistent_Count = 0
        Flag_Premium = False
        Predetermined_Persistent_List = []
        self.ExtraChance = 0

        # 定义不同BonusOption的配置
        bonus_configurations = {
            1: {"Init_Symbol_Count": 5, "Flag_Premium": True},
            2: {"Init_Persistent_Count": 1},
            3: {"Init_Persistent_Count": 1, "Predetermined_Persistent_List": ["Shapeshifter"]},
            4: {"Init_Symbol_Count": 8, "Init_Persistent_Count": 1, "Predetermined_Persistent_List": ["Arms Dealer"]},
            5: {"Init_Persistent_Count": 2},
            6: {"Init_Persistent_Count": 2, "ExtraChance": 1},
            7: {"Init_Persistent_Count": 3},
            8: {"Init_Symbol_Count": 5, "Init_Persistent_Count": 3,
                "Predetermined_Persistent_List": ["Shapeshifter", "Arms Dealer", "Necromancer"]},
            9: {"Init_Symbol_Count": 4, "Init_Persistent_Count": 4},
            10: {"Init_Symbol_Count": 6, "Init_Persistent_Count": 4, "Flag_Premium": True},
            11: {"Init_Symbol_Count": 5, "Init_Persistent_Count": 5},
            12: {"Init_Symbol_Count": 7, "Init_Persistent_Count": 5, "ExtraChance": 1},
            13: {"Init_Symbol_Count": 8, "Init_Persistent_Count": 5, "Flag_Premium": True, "ExtraChance": 2},
            14: {"Init_Symbol_Count": 8, "Init_Persistent_Count": 5, "Flag_Premium": True, "ExtraChance": 2,
                 "Predetermined_Persistent_List": ["Shapeshifter", "Shapeshifter", "Shapeshifter", "Shapeshifter",
                                                   "Shapeshifter"]},
        }

        # 应用配置
        config = bonus_configurations.get(BonusOption, {})
        Init_Symbol_Count = config.get("Init_Symbol_Count", Init_Symbol_Count)
        Init_Persistent_Count = config.get("Init_Persistent_Count", Init_Persistent_Count)
        Flag_Premium = config.get("Flag_Premium", Flag_Premium)
        Predetermined_Persistent_List = config.get("Predetermined_Persistent_List", Predetermined_Persistent_List)
        self.ExtraChance = config.get("ExtraChance", self.ExtraChance)

        # 决定开始的符号数量
        while Init_Symbol_Count < 12:
            RNG = random.randint(1, 4)
            if RNG != 1:
                break
            Init_Symbol_Count += 1

        SymbolType = []

        # 决定开始的符号类别(普通/金框)
        Extra_Persistent_Chance = 0.036 - 0.004 * max(5, Init_Persistent_Count)
        Extra_Persistent = 0
        for i in range(0, Init_Symbol_Count - Init_Persistent_Count):
            # print("Loop1: i=" + str(i))
            RNG = random.uniform(0, 1)
            if RNG <= Extra_Persistent_Chance:
                Extra_Persistent += 1

        Init_Persistent_Count += Extra_Persistent
        for i in range(0, Init_Symbol_Count - Init_Persistent_Count):
            # print("Loop2: i=" + str(i))
            SymbolType.append(1)
        for i in range(0, Init_Persistent_Count):
            # print("Loop2: i=" + str(i))
            SymbolType.append(3)

        # 可用的空位
        NewList = [obj for obj in self.Blocks if obj.Locked == False]
        FirstSymbol = True
        Symbol_That_Might_Cause_Problem = None
        PersistentID = 0
        # 放置每个符号
        for elem in SymbolType:
            # 普通符号
            if elem == 1:
                random.shuffle(NewList)
                InitSymbol = NewList.pop()
                InitSymbol.SetSymbol(RandomUpfrontValue(False))
            # 金框符号
            else:
                NewValue = 1
                # 若还有是预设的金框, 则优先该指定符号
                if len(Predetermined_Persistent_List) > 0:
                    NewFeatureSymbol = Predetermined_Persistent_List.pop()
                # 晋档没有预设金框符号的时候, 随机指定符号
                else:
                    NewFeatureSymbol = RandomPersistentSymbol(0, PersistentID)
                PersistentID += 1
                # Payer可能以高于1x出现
                if NewFeatureSymbol == "Payer" or NewFeatureSymbol == "Adj.Payer":
                    NewValue = RandomUpfrontValue(True)
                # 若不是第一个生成的符号, 且是Adj.Payer或Adj.Collector, 则其需要找到一个相邻于其他符号的位置
                if (NewFeatureSymbol == "Adj.Payer" or NewFeatureSymbol == "Adj.Collector") and not FirstSymbol:
                    TargetSymbolList = SearchPlaceThatCanBeAdj(self, True)
                    random.shuffle(TargetSymbolList)
                    InitSymbol = TargetSymbolList.pop()
                    InitSymbol.SetSymbol(NewValue, NewFeatureSymbol, elem, Flag_IsNew=False)
                # 其他情况可以随机选择位置
                else:
                    EmptySpace = FindSymbols(self, "Empty")
                    random.shuffle(EmptySpace)
                    InitSymbol = EmptySpace.pop()
                    InitSymbol.SetSymbol(NewValue, NewFeatureSymbol, elem, Flag_IsNew=False)
                if FirstSymbol and (NewFeatureSymbol == "Adj.Payer" or NewFeatureSymbol == "Adj.Collector"):
                    Symbol_That_Might_Cause_Problem = InitSymbol
            FirstSymbol = False

        # 检查
        # 如果都是金框, 则可能出现问题
        # 若第一个生成的是相邻收集者/支付者, 其周围可能没有任何其他符号
        if Symbol_That_Might_Cause_Problem is not None:
            Adj = FindSymbols(self, "Adjacent", False, Symbol_That_Might_Cause_Problem.X,
                              Symbol_That_Might_Cause_Problem.Y)
            if len(Adj) == 0:
                ThatSymbol = Symbol_That_Might_Cause_Problem.Symbol
                ThatValue = Symbol_That_Might_Cause_Problem.Value
                Symbol_That_Might_Cause_Problem.SetSymbol()
                TargetSymbolList = SearchPlaceThatCanBeAdj(self, True)
                random.shuffle(TargetSymbolList)
                InitSymbol = TargetSymbolList.pop()
                InitSymbol.SetSymbol(ThatValue, ThatSymbol, 3, Flag_IsNew=False)

        self.SpinsPlayed = 0
        if not Flag_Premium:
            self.ResetPlus1 = False
            self.UnlockedRows = 4
        else:
            self.ResetPlus1 = True
            self.UnlockedRows = 8
        self.HitFreqX_Multi = 1.00
        self.HitFreqY_Multi = 1.00
        self.HitFreqZ_Multi = 1.00

        self.TotalMultiplier = 0
        self.UpdateTotalMultiplier()

        for obj in self.Blocks:
            if obj.Type == 3:
                if obj.Symbol == "Collector Payer":
                    self.HitFreqX_Multi *= 0.5
                    self.HitFreqY_Multi *= 0.5
                    self.HitFreqZ_Multi *= 0.3
                elif obj.Symbol == "Sniper":
                    self.HitFreqX_Multi *= 0.6
                    self.HitFreqY_Multi *= 0.6
                    self.HitFreqZ_Multi *= 0.5
                elif obj.Symbol == "Adj.Collector" or obj.Symbol == "Adj.Payer":
                    self.HitFreqX_Multi *= 0.92
                    self.HitFreqY_Multi *= 0.96
                    self.HitFreqZ_Multi *= 0.92
                elif obj.Symbol == "Arms Dealer":
                    BONUS_HF_PERSISTENT_ARMS_DEALER = 1.172
                    self.HitFreqX_Multi *= BONUS_HF_PERSISTENT_ARMS_DEALER
                    self.HitFreqY_Multi *= BONUS_HF_PERSISTENT_ARMS_DEALER
                    self.HitFreqZ_Multi *= BONUS_HF_PERSISTENT_ARMS_DEALER
                else:
                    self.HitFreqX_Multi *= 0.7
                    self.HitFreqY_Multi *= 0.8
                    self.HitFreqZ_Multi *= 0.6

        if self.ResetPlus1:
            self.SpinsLeft = 4
        else:
            self.SpinsLeft = 3
        Flag_First = 2

        self.TaskList.AddTask(lambda: self.do_nothing(), int(CONST_TASK_TIME * 2.6))
        for obj in self.Blocks:
            if obj.Type == 3:
                self.TaskList.AddTask(lambda obj=obj: self.Activate(obj), CONST_TASK_TIME * Flag_First)
                Flag_First = 1
            if 3 <= obj.Y <= 6:
                continue
            obj.Locked = (self.UnlockedRows < 8)
        self.LogMessage = []
        self.LogMessage.append("Purchase successful! Here's your symbols.")
        if self.CountPersistent() > 0:
            self.LogMessage.append("Activating upfront persistent symbols:")
            self.LogMessage.append("When all persistents are activated, the round will start soon.")
        else:
            self.LogMessage.append("The round will start soon...")

        # self.Blocks[20].SetSymbol(1, "Supplier", 2)
        # self.Blocks[21].SetSymbol(1, "Necromancer", 3)
        # 自动开始
        self.TaskList.AddTask(lambda: self.Spin(), int(CONST_SPIN_SPEED * 2))

        self.TaskList.TurnOn()

        self.label3.configure(text="Feature in play:\n" + CONST_BONUS_TITLE[self.BonusType])

        self.UpdateUI()

    def InitBlocks(self):
        Premium_Bonus_List = []

        for j in range(1, 9):
            for i in range(1, 7):
                if 3 <= j <= 6 or self.BonusType in Premium_Bonus_List:

                    self.Blocks.append(classSymbol(i, j, False))
                else:
                    self.Blocks.append(classSymbol(i, j))
        # for i in range(0, len(self.Blocks)):
        # print(f"Block {i}, located @ {self.Blocks[i].X}, {self.Blocks[i].Y}")

    def Spin(self):

        # SPIN
        for obj in self.Blocks:
            obj.IsNew = False

        self.PrevMultiplier = self.TotalMultiplier
        Filled_Rows = self.CountRowsFilled()
        if not self.FLAG_DOOMSDAY:
            self.LogMessage = []
            self.log_text.delete("0.0", tk.END)
            self.log_text.update()

        self.SpinsPlayed += 1
        self.SpinsLeft -= 1

        self.TaskList = TaskManager()

        # print(f"DEBUG: HF Multi = {self.HitFreqX_Multi}, {self.HitFreqY_Multi}, {self.HitFreqZ_Multi}")

        NewSymbol = CONST_BASE_HIT_FREQ * self.HitFreqX_Multi + CONST_BONUS_HIT_FREQ * self.CountEmptySpace() * self.HitFreqY_Multi
        if self.SpinsPlayed <= 8:
            NewSymbol += CONST_BONUS_FIRST_8_SPINS[self.SpinsPlayed] * self.HitFreqZ_Multi

        flag_hit = False

        EmptySpace = self.CountEmptySpace()

        # 优先检查是否触发末日
        if self.UnlockedRows >= 8 and EmptySpace <= 12:
            Doomsday_chance = 100000
            if 7 <= EmptySpace <= 8:
                Doomsday_chance = 14000
            if 5 <= EmptySpace <= 6:
                Doomsday_chance = 5300
            if EmptySpace == 4:
                Doomsday_chance = 950
            if EmptySpace == 3:
                Doomsday_chance = 330
            if EmptySpace == 2:
                Doomsday_chance = 80
            if EmptySpace == 1:
                Doomsday_chance = 15
            RNG_Doomsday = random.randint(1, Doomsday_chance)
            if RNG_Doomsday == 1:
                BlockList = FindSymbols(self, "Empty")
                random.shuffle(BlockList)
                Block = BlockList.pop()
                Block.SetSymbol(666, "DOOMSDAY\nNecromancer", 2, Flag_IsNew=True)

                flag_hit = True
                self.FLAG_DOOMSDAY = True

        # 随机数
        if EmptySpace > 0:
            if not self.HF_Bonus:
                if self.SpinsLeft > 0:
                    RNG_Hit = random.uniform(0, 1)
                else:
                    RNG_Hit = random.uniform(0, 0.8)
            else:
                self.HF_Bonus = False
                RNG_Hit = random.uniform(0, 0.6)
        else:
            RNG_Hit = 9999.99

        # 获得新符号的几率
        BaseHF = CONST_BASE_HIT_FREQ * self.HitFreqX_Multi
        BonusHF = CONST_BONUS_HIT_FREQ * self.CountEmptySpace() * self.HitFreqY_Multi
        BoostHF = 0
        if self.SpinsPlayed <= 8:
            BoostHF = CONST_BONUS_FIRST_8_SPINS[self.SpinsPlayed] * self.HitFreqZ_Multi

        CONST_MIN_HF = 0.05
        if RNG_Hit <= max(BaseHF + BonusHF + BoostHF, CONST_MIN_HF):
            flag_hit = True

        factor_multiple_hit = 1.00
        while RNG_Hit <= max(BaseHF + BonusHF + BoostHF, CONST_MIN_HF) * max(factor_multiple_hit, 0.15) and \
                self.CountEmptySpace() > 0:

            factor_multiple_hit *= 0.8

            # 随机决定类别(普通/普框/金框)
            List_Types = [1, 2, 3]
            # 得到普通/普框/金框的频率(权重)
            Weight_Feature = max(14, 27 * pow(0.83, self.CountPersistent()))
            Weight_Persistent = max(1.5, 5.5 * pow(0.68, self.CountPersistent()))
            Weight_Regular = 100 - Weight_Feature - Weight_Persistent
            List_Weight = [Weight_Regular, Weight_Feature, Weight_Persistent]

            # 决定类别
            NewType = random.choices(List_Types, weights=List_Weight, k=1)[0]
            NewValue = 1
            NewFeatureSymbol = ""

            # 根据类别进行操作
            if NewType == 1:
                # 从空符号中选择一个来变成新符号
                TargetSymbolList = FindSymbols(self, "Empty")
                random.shuffle(TargetSymbolList)
                TargetSymbol = TargetSymbolList.pop()
                NewValue = RandomUpfrontValue()
                TargetSymbol.SetSymbol(NewValue, Flag_IsNew=True)
            elif NewType >= 2:
                # 随机的新的功能符号

                if NewType == 2:
                    NewFeatureSymbol = RandomFeatureSymbol("", self.UnlockedRows, self.ResetPlus1)
                elif NewType == 3:
                    NewFeatureSymbol = RandomPersistentSymbol(self.CountFeature(), self.CountPersistent())
                if NewFeatureSymbol == "Payer" or NewFeatureSymbol == "Adj.Payer":
                    NewValue = RandomUpfrontValue(True)
                if NewFeatureSymbol == "Adj.Payer" or NewFeatureSymbol == "Adj.Collector":
                    TargetSymbolList = SearchPlaceThatCanBeAdj(self, True)
                    # print("DEBUG: SearchPlaceThatCanBeAdj")
                else:
                    TargetSymbolList = FindSymbols(self, "Empty")
                    # print("DEBUG: FindSymbols(Empty)")
                random.shuffle(TargetSymbolList)
                TargetSymbol = TargetSymbolList.pop()
                if NewFeatureSymbol == "Dynamite":
                    MultiList = [2, 3, 5, 10]
                    WeightList = [76, 18, 5, 1]
                    NewValue = random.choices(MultiList, weights=WeightList, k=1)[0]
                TargetSymbol.SetSymbol(NewValue, NewFeatureSymbol, NewType, Flag_IsNew=True)

            RNG_Hit = random.uniform(0, 1)
            # 奖励HF重新计算, 因为和剩余的空间有关.
            BonusHF = CONST_BONUS_HIT_FREQ * self.CountEmptySpace() * self.HitFreqY_Multi

        # 对于部分奖励, 第一转保证一个Reset +1

        Reset = 3
        self.LogMessage.append("------ Spinning... ------")
        # 检查是否可以开新行

        if flag_hit:

            # 计算需要解锁几个新行
            Updated_Filled_Rows = self.CountRowsFilled()
            Diff = Updated_Filled_Rows - Filled_Rows
            if Diff > 0:
                for i in range(0, Diff):
                    self.UnlockRow(True)
            # 重设转数
            if self.ResetPlus1:
                Reset = 4
            self.SpinsLeft = Reset

            self.LogMessage.append("HIT\nNew symbol landed. SPINS LEFT reset to " + str(Reset) + ".")
        else:
            self.LogMessage.append(f"MISS\nNothing landed in active area. SPINS LEFT: {self.SpinsLeft}")

        if flag_hit:
            self.UpdateUI()
        elif self.CountPersistent() > 0:
            self.UpdateUI()
        else:
            for obj in self.Blocks:
                if obj.Symbol == "Dynamite":
                    self.UpdateUI()
                    break

        flag_dynamite = False
        for obj in self.Blocks:
            if obj.Type == 3:
                obj.Activated = False
            if obj.Symbol == "Shapeshifter":
                obj.Latest = ""
            if obj.Symbol == "Dynamite":
                flag_dynamite = True

        flag_action = False
        self.flag_full = False
        if self.UnlockedRows >= 8 and self.SpinsLeft <= 0 and self.CountEmptySpace() < 1 and not flag_dynamite:
            self.flag_full = True

        for obj in self.Blocks:

            if obj.Type >= 2 and not obj.Locked and not obj.Activated:
                if not flag_action:
                    flag_action = True

                    self.LogMessage.append("Activating special symbols:")

                self.TaskList.AddTask(lambda obj=obj: self.Activate(obj))

            if obj.Symbol == "DOOMSDAY\nNecromancer" and obj.IsNew and self.CountEmptySpace() == 0:
                obj.Value = 66666

            # 无论是否击中, 未激活区域都可能出现新图标, 每个空位置的几率=万分之32/8/2
            if obj.Locked and obj.IsEmpty():
                RNG_Hit = random.randint(1, 10000)
                if RNG_Hit <= 32:
                    obj.SetSymbol(RandomUpfrontValue())
                elif RNG_Hit <= 40:
                    NewValue = 1
                    NewSymbol = RandomFeatureSymbol("Locked", self.UnlockedRows, self.ResetPlus1)
                    if NewSymbol == "Payer" or NewSymbol == "Adj.Payer":
                        NewValue = RandomUpfrontValue(True)
                    obj.SetSymbol(NewValue, NewSymbol, 2)
                elif RNG_Hit <= 42:
                    NewValue = 1
                    NewSymbol = RandomPersistentSymbol(self.CountFeature(), self.CountPersistent(), "Locked")
                    if NewSymbol == "Payer" or NewSymbol == "Adj.Payer":
                        NewValue = RandomUpfrontValue(True)
                    obj.SetSymbol(NewValue, NewSymbol, 3)
        if not self.flag_full:
            if (self.SpinsLeft > 0 and self.CountEmptySpace() > 0) or self.ExtraChance > 0:
                self.TaskList.AddTask(lambda: self.SpinDone())

            elif not self.FLAG_DOOMSDAY:
                if self.ExtraChance == 0 or self.CountEmptySpace() == 0:
                    self.TaskList.AddTask(lambda: self.GameOver(), 1800)
        else:
            self.SpinsLeft = 0
            self.TaskList.AddTask(lambda: self.GameOver(), 1800)

        # 自动在1.2s后进行下一转
        if self.SpinsLeft > 0 and not self.FLAG_DOOMSDAY:
            self.TaskList.AddTask(lambda: self.Spin(), CONST_SPIN_SPEED)

        # 逐步执行
        # self.TaskList.PrintTaskList()
        self.TaskList.TurnOn()
        self.UpdateUI()

    # 使用额外机会
    # 随机放置一个普通符号
    def UseExtraChance(self):
        TargetSymbolList = FindSymbols(self, "Empty")
        random.shuffle(TargetSymbolList)
        TargetSymbol = TargetSymbolList.pop()
        TargetSymbol.SetSymbol(RandomUpfrontValue(), Flag_IsNew=True)
        self.ExtraChance -= 1
        self.SpinsLeft = 1
        self.LogMessage.append("------ EXTRA CHANCE! ------")
        self.LogMessage.append("1 Extra Chance used, to prevent a game over from happening.")
        self.LogMessage.append("A new symbol has been added, and you're given 1 more spin.")
        self.LogMessage.append("The chance of landing a symbol in the next spin is also increased.")
        self.HF_Bonus = True
        self.LogMessage.append(f"Extra Chances remaining: {self.ExtraChance}")
        self.TaskList.AddTask(lambda: self.Spin(), CONST_SPIN_SPEED * 2)
        self.LogMessage.append("======== SPIN FINISHED ========")
        self.UpdateUI()

    # 得到新图标时触发.
    # 设置开局的金框狙击手和金框收集支付者时, 将flag1设置为true

    def ReduceHitFrequency(self, flag1=False):
        if not flag1:
            self.HitFreqX_Multi *= 0.7
            self.HitFreqY_Multi *= 0.8
            self.HitFreqZ_Multi *= 0.6
        else:
            self.HitFreqX_Multi *= 0.8
            self.HitFreqY_Multi *= 0.85
            self.HitFreqZ_Multi *= 0.8

    # 激活图标
    def Activate(self, Symbol, extra_param=""):

        for obj in self.Blocks:
            obj.IsAffected = False
            obj.IsUpdated = False

        self.PrevMultiplier = self.TotalMultiplier
        Flag1 = True
        if extra_param == "advisor" and Symbol.Activated == False:
            Flag1 = False
        if Symbol.Type != 3 and Symbol.Symbol != "Dynamite":
            Symbol.Activated = True
        Symbol.IsUpdated = True
        # 使用字典映射字符串到相应的函数调用

        functions = {
            'Collector': self.DoCollector,
            'Payer': self.DoPayer,
            'Collector Payer': self.DoCollectorPayer,
            'Sniper': self.DoSniper,
            'Arms Dealer': self.DoArmsDealer,
            'Necromancer': self.DoNecromancer,
            'Unlocker': self.DoUnlocker,
            'Upgrader': self.DoUpgrader,
            'Shapeshifter': self.DoShapeshifter,
            'Reset +1': self.DoResetPlus1,
            'Dynamite': self.DoDynamite,
            'Synchronizer': self.DoSync,
            'Jobs Advisor': self.DoAdvisor,
            "DOOMSDAY\nNecromancer": self.DoDOOMSDAY,
            "Supplier": self.DoSupplier
        }

        # 获取并执行相应的函数
        func = functions.get(Symbol.Symbol)
        if FLAG_DEBUG_MESSAGEBOX:
            messagebox.showinfo("Feature Symbol", f"Activating {Symbol.Symbol} @ {self.get_coordinates(Symbol)}:")
        if func:
            func(Symbol)
        if Symbol.Symbol == "Adj.Collector":
            self.DoCollector(Symbol, True)
        if Symbol.Symbol == "Adj.Payer":
            self.DoPayer(Symbol, True)
        if not Flag1:
            Symbol.Activated = False
        self.UpdateUI()
        self.PrevMultiplier = -1

    # 计算空位数量
    def CountEmptySpace(self):

        result = 0
        for obj in self.Blocks:
            if obj.Locked == False and obj.Type == 0:
                result += 1
        return result

    def CountFeature(self):
        Count = 0
        for obj in self.Blocks:
            if obj.Locked == False and obj.Type >= 2 and obj.Symbol != "Dynamite":
                Count += 1
        return Count

    def CountRowsFilled(self):

        Count = 0
        for i in range(0, 8):
            if self.Blocks[i * 6].Locked:
                continue
            for j in range(0, 6):
                if self.Blocks[i * 6 + j].Type == 0 or self.Blocks[i * 6 + j].Value == 0:
                    break
                if j == 5:
                    Count += 1
        return Count

    def CountPersistent(self, flag_equal=False):
        Count = 0.0
        for obj in self.Blocks:
            if not obj.Locked and obj.Type == 3:
                if (obj.Symbol == "Adj.Collector" or obj.Symbol == "Adj.Payer") and not flag_equal:
                    Count += 0.5
                else:
                    Count += 1
        return Count

    # 更新总倍数
    def UpdateTotalMultiplier(self):
        self.TotalMultiplier = 0
        for obj in self.Blocks:
            if not obj.Locked and (obj.Symbol != "Dynamite" or self.FLAG_GAME_OVER):
                self.TotalMultiplier += obj.Value

    # 检查是否回合结束(无剩余旋转次数)
    def GameOver(self, Player=PlayerProfile):
        self.FLAG_GAME_OVER = True
        self.LogMessage.append("======== SPIN FINISHED ========")
        self.LogMessage.append("//////GAME OVER!//////")
        if self.flag_full:
            self.LogMessage.append("======== FULL SCREEN ACHIEVED! ========")
            self.LogMessage.append("x25 will be applied to ALL symbols! (Except DOOMSDAY Necromancer)")
            for obj in self.Blocks:
                if self.flag_full and obj.Symbol != "DOOMSDAY\nNecromancer":
                    obj.Value *= 25
                    self.UpdateTotalMultiplier()
        self.LogMessage.append("Total multiplier:\n{:,.0f}x".format(self.TotalMultiplier))
        M = 1000 * 1000
        B = 1000 * M
        T = 1000 * B
        Q1 = 1000 * T
        Q2 = 1000 * Q1
        S1 = 1000 * Q2
        S2 = 1000 * S1
        OCT = 1000 * S2
        NON = 1000 * OCT
        DEC = 1000 * NON
        uDEC = 1000 * DEC
        dDEC = 1000 * uDEC
        tDEC = 1000 * dDEC
        thresholds = [
            15, 25, 50, 100, 250,
            500, 1000, 2500, 5000, 10000,

            20000, 30000, 50000, 75000, 100000,
            150000, 200000, 300000, 500000, 1 * M,

                                            2 * M, 3 * M, 5 * M, 10 * M, 20 * M,
                                            50 * M, 100 * M, 300 * M, 1 * B, 3 * B,

                                            10 * B, 30 * B, 100 * B, 300 * B, 1 * T,
                                            3 * T, 10 * T, 30 * T, 100 * T, 300 * T,

                                            1 * Q1, 5 * Q1, 25 * Q1, 100 * Q1, 500 * Q1,
                                            2 * Q2, 10 * Q2, 50 * Q2, 200 * Q2, 1 * S1,

                                            6 * S1, 40 * S1, 250 * S1, 1.5 * S2, 10 * S2,
                                            60 * S2, 400 * S2, 2.5 * OCT, 15 * OCT, 100 * OCT,

                                            750 * OCT, 5 * NON, 35 * NON, 250 * NON, 1.8 * DEC,
                                            15 * DEC, 100 * DEC, 750 * DEC, 5 * uDEC, 40 * uDEC,

                                            42 * uDEC, 4.4 * dDEC, 46 * dDEC, 480 * dDEC, 5 * tDEC,
                                            60 * tDEC, 700 * tDEC, 8000 * tDEC, 90000 * tDEC, 1 * M * tDEC

        ]
        for i in range(0, 10):
            last = thresholds[len(thresholds) - 1]
            thresholds.append(last * 12)
        for i in range(0, 4):
            last = thresholds[len(thresholds) - 1]
            thresholds.append(last * 24)

        last = thresholds[len(thresholds) - 1]
        thresholds.append(last * 48)
        last = thresholds[len(thresholds) - 1]
        thresholds.append(last * 96)

        level = 0
        for i, threshold in enumerate(thresholds, 1):
            if self.TotalMultiplier >= threshold:
                level = i
            else:
                break
        Player.Star_record = max(Player.Star_record, level)
        self.LogMessage.append(f"Rank:\n" + FormatStars(level))

        # 增加玩家经验值等
        Player.Highscore[self.BonusType] = max(Player.Highscore[self.BonusType], self.TotalMultiplier)

        EXP_Part1 = math.log(self.TotalMultiplier, 1.65) * pow(self.TotalMultiplier, 0.45)

        if EXP_Part1 < 1:
            EXP_Part1 = 1
        if self.BonusType <= 3:
            FactorList = [4.0, 3.0, 2.2, 1.6]
            Factor = FactorList[self.BonusType]
        else:
            Factor = 1.00

        EXP_Part2 = 0
        Value_Per_Spin = 3.0
        for i in range(1, self.SpinsPlayed + 1):
            EXP_Part2 += Value_Per_Spin

            if i <= 10:
                Value_Per_Spin += max(2.4, Value_Per_Spin * 0.18)
            elif i <= 15:
                Value_Per_Spin += max(2.4, Value_Per_Spin * 0.21)
            elif i <= 20:
                Value_Per_Spin += max(2.4, Value_Per_Spin * 0.25)
            else:
                Value_Per_Spin += max(2.4, Value_Per_Spin * 0.30)
            # print(f"i={i}, ValuePerSpin={Value_Per_Spin}")
        EXP_Part2 = int(Factor * EXP_Part2)

        Player.EXP += int(EXP_Part1) + int(EXP_Part2)
        # 保存进度

        OutputString = "You get:\n"
        OutputString += f"EXP: + {int(EXP_Part1):,} from result\n"
        OutputString += f"EXP: + {int(EXP_Part2):,} from spins played ({self.SpinsPlayed})\n"
        OutputString += f"Total EXP: {int(EXP_Part1) + int(EXP_Part2):,}"

        # 添加按钮
        with open(file_path, 'wb') as f:
            pickle.dump(Player, f)

        self.Label4.configure(text=PlayerProfile.GetProgress()[0])
        self.ProgressBar['value'] = int(PlayerProfile.GetProgress()[2] * 100)
        self.LogMessage.append(OutputString)
        self.UpdateUI()

    def AddMsg_FeatureSymbolActivated(self, Symbol):

        self.LogAndDisplayMsg(f"------ {Symbol.Symbol} @ {self.get_coordinates(Symbol)}'s turn! ------")

    def get_coordinates(self, Symbol):
        # update Jul 16th 2024
        # it seems all coordinates has been messed up
        # so have to print it in format of (Y, X) so it looks correct
        # as I don't want to rewrite a lot of the code
        return f"({Symbol.Y}, {Symbol.X})"

    def DoSupplier(self, SourceBlock):
        self.AddMsg_FeatureSymbolActivated(SourceBlock)
        if self.ExtraChance < 3:
            self.LogMessage.append("You got 1 Extra Chance!")
            self.ExtraChance += 1
        else:
            self.LogMessage.append("You didn't get any Extra Chance, because you already have 3.")
        self.SpinsLeft = 3 + (self.ResetPlus1 == True)
        self.LogMessage.append(f"Spins left is also reset to {self.SpinsLeft}.")

    def DoDOOMSDAY(self, SourceBlock):
        self.FLAG_DOOMSDAY = True
        self.LogMessage.append(f"------ DOOMSDAY INCOMING! ------")

        self.TaskList.AddEmergencyTask(
            lambda: self.LogMessage.append("DOOMSDAY Necromancer will be activated after this spin."), 467)
        self.TaskList.AddTask(lambda: self.Activate_DOOMSDAY(), 40)

    def Activate_DOOMSDAY(self):
        self.SpinsLeft = 0
        self.ExtraChance = 0
        self.UpdateUI()
        self.LogMessage.append("DOOMSDAY Necromancer FEATURE ACTIVATED!")
        Feature_Symbols = FindSymbols(self, "Feature", Extra_param="DOOMSDAY")
        for obj in Feature_Symbols:
            obj.Activated = False

            self.TaskList.AddTask(lambda obj=obj: self.Activate(obj), 467)
        self.TaskList.AddTask(lambda: self.GameOver(), 1200)

    def DoDynamite(self, SourceBlock):
        Adj = FindSymbols(self, "Adjacent", False, SourceBlock.X, SourceBlock.Y)
        Adj = RemoveDynamites(Adj)
        if len(Adj) <= 0:
            SourceBlock.Value += SourceBlock.Speed
            return
        self.LogMessage.append(f"------ Dynamite @ {self.get_coordinates(SourceBlock)} Explodes! ------")
        SourceBlock.Activated = True
        Adj = FindSymbols(self, "Adjacent", False, SourceBlock.X, SourceBlock.Y)
        for obj in Adj:
            obj.Value *= SourceBlock.Value
            if obj.Symbol == "Dynamite":
                obj.Speed *= SourceBlock.Value
        SourceBlock.Speed = 0
        self.LogMessage.append(f"Everything nearby is multiplied by {SourceBlock.Value:,}")

    def DoAdvisor(self, SourceBlock):
        TargetBlocks = FindSymbols(self, "Feature", Extra_param="Jobs Advisor")
        self.AddMsg_FeatureSymbolActivated(SourceBlock)
        if len(TargetBlocks) < 1:
            self.LogMessage.append(f"{SourceBlock.Symbol} Fail to find any target.")
            return
        random.shuffle(TargetBlocks)
        Target = TargetBlocks.pop()
        Target.Symbol = FlipCollectorPayer(Target, self)

        if Target.Type == 1:
            Target.Type = 2
            Target.Activated = True
            self.LogMessage.append(f"Symbol @ {self.get_coordinates(Target)} is now a {Target.Symbol}.")
        else:
            self.LogMessage.append(f"Symbol @ {self.get_coordinates(Target)} is now a {Target.Symbol}.")
        if Target.Type == 2:
            self.LogMessage.append(f"This isn't a Persistent symbol, and it'll be activated.")
            self.TaskList.AddEmergencyTask(lambda obj=Target, extra_param="advisor": self.Activate(obj, extra_param))

    def DoSync(self, SourceBlock):
        Affected = []
        Pattern = random.randint(1, 3)

        self.AddMsg_FeatureSymbolActivated(SourceBlock)
        if Pattern == 1:
            self.LogMessage.append("Affected area: Adjacent")
            Affected = FindSymbols(self, "Adjacent", False, SourceBlock.X, SourceBlock.Y)
            Affected.append(SourceBlock)
        elif Pattern == 2:
            self.LogMessage.append("Affected area: Horizontal")
            Affected = FindSymbols(self, "Row", X=SourceBlock.X, Y=SourceBlock.Y)
        elif Pattern == 3:
            self.LogMessage.append("Affected area: Vertical")
            Affected = FindSymbols(self, "Column", X=SourceBlock.X, Y=SourceBlock.Y)

        High = SourceBlock.Value
        for obj in Affected:
            if obj.Value > High and obj.Symbol != "Dynamite":
                High = obj.Value
        self.LogMessage.append(f"Highest value in the area is {High:,}.")
        for obj in Affected:
            if obj.Symbol != "Dynamite":
                obj.Value = High
        # self.LogMessage.append(f"Collector Payer paid each of them  {SourceBlock.Value:,}.")
        self.LogMessage.append(f"Now every affected symbol's value is updated to {High:,}.")

    # 使目标符号进行收集支付者操作
    def DoCollectorPayer(self, SourceBlock):
        if not self.FLAG1:
            self.LogAndDisplayMsg(f"------ Collector Payer @ {self.get_coordinates(SourceBlock)}'s turn! ------")
        TargetCount = [3, 4, 5]
        Weight = [72, 22, 6]
        if SourceBlock.Symbol == "Collector Payer" and SourceBlock.Type == 3:
            Weight = [154, 40, 6]
        Target = random.choices(TargetCount, weights=Weight, k=1)[0]
        CollectedTotal = 0
        EligibleBlocks = FindSymbols(self, "NonEmpty", X=SourceBlock.X, Y=SourceBlock.Y)
        EligibleBlocks = RemoveDynamites(EligibleBlocks)
        if len(EligibleBlocks) < Target:
            Target = len(EligibleBlocks)
        random.shuffle(EligibleBlocks)

        str_selected = "Symbols selected: "

        for i in range(0, Target):
            CollectedTotal += EligibleBlocks[i].Value
            EligibleBlocks[i].IsAffected = True
            str_selected += f"({EligibleBlocks[i].X}, {EligibleBlocks[i].Y})"
        self.LogMessage.append(str_selected)
        SourceBlock.Value += CollectedTotal
        Value = CollectedTotal
        self.LogMessage.append(f"Collector Payer collected a total of {CollectedTotal:,} from those symbols.")
        for i in range(0, Target):
            EligibleBlocks[i].Value += SourceBlock.Value
        Value += SourceBlock.Value * Target
        self.LogMessage.append(f"Collector Payer paid each of them  {SourceBlock.Value:,}.")
        ValueString = "{:,.0f}".format(Value)
        self.LogMessage.append(f"Total profit: {ValueString}x.")

    # 使目标符号进行狙击者操作
    def DoSniper(self, SourceBlock):
        if not self.FLAG1:
            self.LogAndDisplayMsg(f"------ Sniper @ {self.get_coordinates(SourceBlock)}'s turn! ------")
        TargetCount = [3, 4, 5, 6, 7, 8]
        Weight = [160, 30, 12, 8, 4, 1]
        if SourceBlock.Type == 3:
            Weight[0] = 400
        Target = random.choices(TargetCount, weights=Weight, k=1)[0]

        EligibleBlocks = FindSymbols(self, "NonEmpty", X=SourceBlock.X, Y=SourceBlock.Y)
        Profit = 0
        for i in range(0, Target):
            random.shuffle(EligibleBlocks)
            Profit += EligibleBlocks[0].Value
            EligibleBlocks[0].IsAffected = True
            EligibleBlocks[0].Value *= 2
            self.LogMessage.append(f"The symbol @ {self.get_coordinates(EligibleBlocks[0])} is doubled:"
                                   f"{int(EligibleBlocks[0].Value / 2):,} -> {EligibleBlocks[0].Value:,}")
        self.LogMessage.append(f"Total profit: {Profit:,}x.")

    def DoCollector(self, SourceBlock, isAdj=False):
        Msg = f"Collector @ {self.get_coordinates(SourceBlock)}'s turn! ------"
        if isAdj:
            Msg = "Adj." + Msg
        Msg = "------ " + Msg

        if not self.FLAG1:
            self.LogAndDisplayMsg(Msg)
        ValueCollected = 0

        if not isAdj:
            Target = FindSymbols(self, "NonEmpty", X=SourceBlock.X, Y=SourceBlock.Y)
        else:
            Target = FindSymbols(self, "Adjacent", SearchForEmpty=False, X=SourceBlock.X, Y=SourceBlock.Y)

        for obj in Target:
            if obj.Symbol != "Dynamite":
                ValueCollected += obj.Value

        SourceBlock.Value += ValueCollected
        self.LogMessage.append("A total of {:,} collected.".format(ValueCollected))

    def DoPayer(self, SourceBlock, isAdj=False):
        Msg = f"Payer @ {self.get_coordinates(SourceBlock)}'s turn! ------"
        if isAdj:
            Msg = "Adj." + Msg
        Msg = "------ " + Msg
        if not self.FLAG1:
            self.LogAndDisplayMsg(Msg)

        BlocksAffected = 0

        if not isAdj:
            Target = FindSymbols(self, "NonEmpty", X=SourceBlock.X, Y=SourceBlock.Y)

        else:

            Target = FindSymbols(self, "Adjacent", SearchForEmpty=False, X=SourceBlock.X, Y=SourceBlock.Y)

        for obj in Target:
            if obj.Symbol != "Dynamite":
                obj.Value += SourceBlock.Value
                BlocksAffected += 1

        self.LogMessage.append(f"Paid {SourceBlock.Value:,} to {BlocksAffected:,} symbols. "
                               f"({SourceBlock.Value * BlocksAffected:,}x total)")

    def DoUnlocker(self, SourceBlock):
        if not self.FLAG1:
            Msg = f"------ Unlocker @ {self.get_coordinates(SourceBlock)}'s turn! ------"
            self.LogAndDisplayMsg(Msg)
        self.UnlockRow()

    def UnlockRow(self, Flag_NaturalUnlock=False):

        self.UnlockedRows += 1
        TargetY = [2, 7, 1, 8]
        if 5 <= self.UnlockedRows <= 8:
            for obj in self.Blocks:
                if obj.Y == TargetY[self.UnlockedRows - 5]:
                    obj.Locked = False
                    if obj.Type >= 2:
                        self.TaskList.AddEmergencyTask(lambda obj=obj: self.Activate(obj))
                        if obj.Type == 3:
                            if obj.Symbol == "Adj.Collector" or obj.Symbol == "Adj.Payer":
                                self.ReduceHitFrequency(True)
                            else:
                                self.ReduceHitFrequency()

        if Flag_NaturalUnlock:
            self.LogMessage.append("An entire row has been filled")
        self.LogMessage.append("You got a new row! If there's any new feature symbols, they'll be activated now.")

    def DoUpgrader(self, SourceBlock):

        if not self.FLAG1:
            self.LogAndDisplayMsg(f"------ Upgrader @ {self.get_coordinates(SourceBlock)}'s turn! ------")

        TargetCount = [1, 2, 3]
        Weight = [108, 16, 3]

        Target = random.choices(TargetCount, weights=Weight, k=1)[0]

        Silver_Symbols = FindSymbols(self, "Feature", Extra_param="Upgrader")
        if len(Silver_Symbols) == 0:
            self.LogMessage.append("Upgrader fail to find any target.\nNot good.")
            return
        for i in range(0, min(len(Silver_Symbols), Target)):
            self.TaskList.AddEmergencyTask(lambda: self.UpgraderSubFunction())

    def UpgraderSubFunction(self):
        Silver_Symbols = FindSymbols(self, "Feature", Extra_param="Upgrader")
        random.shuffle(Silver_Symbols)
        Selected_Symbol = Silver_Symbols.pop()
        Selected_Symbol.Type = 3
        self.LogMessage.append(f"{Selected_Symbol.Symbol} @ {self.get_coordinates(Selected_Symbol)} is now"
                               f" Persistent!")
        self.Activate(Selected_Symbol)
        self.ReduceHitFrequency()

    def DoArmsDealer(self, SourceBlock):

        if not self.FLAG1:
            self.LogAndDisplayMsg(f"------ Arms Dealer @ {self.get_coordinates(SourceBlock)}'s turn! ------")

        TargetCount = [1, 2, 3, 4]
        Weight = [30, 55, 40, 12]

        if SourceBlock.Symbol == "Arms Dealer" and SourceBlock.Type == 3:
            Target = 1
        else:
            Target = random.choices(TargetCount, weights=Weight, k=1)[0]
        Regular_Symbols = FindSymbols(self, "Regular")
        if len(Regular_Symbols) == 0:
            self.LogMessage.append("Arms dealer fail to find any target.")
            return
        # 添加紧急任务
        for i in range(0, min(Target, len(Regular_Symbols))):
            self.TaskList.AddEmergencyTask(lambda: self.ArmsDealerSubFunction())

    def ArmsDealerSubFunction(self):
        Regular_Symbols = FindSymbols(self, "Regular")
        if len(Regular_Symbols) < 1:
            return
        # 随机选择一个普通符号
        random.shuffle(Regular_Symbols)
        Selected_Symbol = Regular_Symbols.pop()
        # 其变成功能符号
        Selected_Symbol.Type = 2
        CanBeAdj = True

        # 如果没有相邻图标, 不能成为相邻收集者或相邻支付者
        if len(FindSymbols(self, "Adjacent", False, Selected_Symbol.X, Selected_Symbol.Y)) == 0:
            CanBeAdj = False

        Selected_Symbol.Symbol = RandomFeatureSymbol("Arms Dealer", self.UnlockedRows, self.ResetPlus1,
                                                     CanBeAdj=CanBeAdj)
        self.LogMessage.append(f"(Arms Dealer)Symbol @ {self.get_coordinates(Selected_Symbol)} becomes a "
                               f"{Selected_Symbol.Symbol}!")
        # 添加到加急任务
        self.Activate(Selected_Symbol)

    def DoNecromancer(self, SourceBlock):
        if not self.FLAG1:
            self.LogAndDisplayMsg(f"------ Necromancer @ {self.get_coordinates(SourceBlock)}'s turn! ------")
        TargetCount = [2, 3, 4, 5, 6, 7]
        Weight = [65, 21, 14, 8, 5, 4]

        if SourceBlock.Symbol == "Necromancer" and SourceBlock.Type == 3:
            TargetCount = [1, 2, 3, 4, 5, 6, 7]
            Weight = [355, 45, 21, 7, 4, 2, 2]

        TargetCount = random.choices(TargetCount, weights=Weight, k=1)[0]
        Feature_Symbols = FindSymbols(self, "Feature", False, SourceBlock.X, SourceBlock.Y, "Necromancer")
        if len(Feature_Symbols) == 0:
            self.LogMessage.append("Necromancer fail to find any target.")
            return
        # 添加紧急任务
        for i in range(0, TargetCount):
            self.TaskList.AddEmergencyTask(lambda X=SourceBlock: self.NecromancerSubFunction(X))

    def NecromancerSubFunction(self, SourceBlock):
        Feature_Symbols = FindSymbols(self, "Feature", False, SourceBlock.X, SourceBlock.Y, "Necromancer")
        random.shuffle(Feature_Symbols)
        Target = Feature_Symbols[0]
        self.LogMessage.append(f"(Necromancer)Activating {Target.Symbol} @ {self.get_coordinates(Target)}!")
        self.Activate(Target)

    def DoShapeshifter(self, SourceBlock):

        self.LogAndDisplayMsg(f"------ Shapeshifter @ {self.get_coordinates(SourceBlock)}'s turn! ------")

        # 定义函数和相应的字符串
        actions = [
            (self.DoCollector, "Collector"),
            (self.DoSniper, "Sniper"),
            (self.DoPayer, "Payer"),
            (self.DoCollectorPayer, "Collector Payer"),
            (self.DoUpgrader, "Upgrader"),
            (self.DoAdvisor, "Jobs Advisor"),
            (self.DoSync, "Synchronizer"),
            (self.DoSupplier, "Supplier"),

        ]
        # 定义权重
        weights = [102, 147, 63, 22, 3, 5, 15, 2]
        Adj = FindSymbols(self, "Adjacent", False, X=SourceBlock.X, Y=SourceBlock.Y)
        RemoveDynamites(Adj)
        if len(Adj) > 0:
            actions.append((lambda sb: self.DoCollector(sb, True), "Adj.Collector"))
            actions.append((lambda sb: self.DoPayer(sb, True), "Adj.Payer"))
            weights.append(65)
            weights.append(70)
        if len(FindSymbols(self, "Regular")) > 0:
            actions.append((self.DoArmsDealer, "Arms Dealer"))
            weights.append(30)
        if self.UnlockedRows < 8:
            actions.append((self.DoUnlocker, "Unlocker"))
            weights.append(15)

        # 随机选择函数
        chosen_func, action_str = random.choices(actions, weights=weights, k=1)[0]

        # 设置Action字符串
        # Msg = f"Collector @ ({SourceBlock.X}, {SourceBlock.Y})'s turn!"
        self.LogMessage.append(
            f"Shapeshifter @ {self.get_coordinates(SourceBlock)} act as a {action_str} this turn.")

        # 调用选定的函数
        self.FLAG1 = True
        SourceBlock.Latest = action_str
        chosen_func(SourceBlock)
        self.FLAG1 = False

    def DoResetPlus1(self, SourceBlock):
        if not self.FLAG1:
            self.LogAndDisplayMsg(f"------ Reset +1 @ {self.get_coordinates(SourceBlock)}'s turn! ------")

        self.ResetPlus1 = True
        self.SpinsLeft = 4
        self.LogMessage.append("Now you need 4 dead spins in a row to game over.")

    def LogAndDisplayMsg(self, Message):
        self.LogMessage.append(Message)
        DisplayMsg(Message)


class classSymbol:
    def __init__(self, X, Y, Locked=True, Symbol="", Type=0):

        self.Locked = Locked
        self.Type = Type  # 0=空, 1=普通, 2=普框, 3-金框
        self.Symbol = Symbol

        self.Latest = ""

        self.Value = 0
        self.Speed = 0
        self.X = X
        self.Y = Y

        self.IsNew = False
        self.IsUpdated = 0
        self.IsAffected = 0
        self.Activated = False

    def SetSymbol(self, NewValue=0, NewSymbol="", NewType=1, Flag_IsNew=False):
        self.Value = NewValue
        self.Symbol = NewSymbol
        if NewSymbol != "":
            self.Activated = False
            if NewSymbol == "Dynamite":
                self.Speed = 1
        if NewValue > 0:
            self.Type = NewType
        else:
            self.Type = 0
        self.IsNew = Flag_IsNew
        self.Latest = ""

    def IsEmpty(self):
        if self.Type == 0 or self.Value == 0:
            return True
        return False

    def IsSamePosition(self, X2, Y2):
        if self.X == X2 and self.Y == Y2:
            return True
        return False

    def IsAdj(self):
        if self.Symbol == "Adj.Payer" or self.Symbol == "Adj.Collector":
            return True
        return False

    def GetInfo(self):
        Info = f"({self.X},{self.Y}), Symbol={self.Symbol}, Value={self.Value}"
        return Info

    def GetDebugInfo(self):
        print(f"Position: {self.X}, {self.Y}\n"
              f"Locked: {self.Locked}, Type: {self.Type}, Value: {self.Value}, Symbol:{self.Symbol}")


def RandomFeatureSymbol(Source="", UnlockedRows=4, HaveResetPlus1=False, CanBeAdj=True):
    Symbols = ["Collector", "Payer", "Sniper", "Collector Payer", "Upgrader", "Synchronizer", "Jobs Advisor",
               "Supplier"]
    # NUMBERS
    Weights = [140, 140, 125, 16, 2, 9, 24, 20]
    if CanBeAdj and Source != "Locked":
        Symbols.append("Adj.Collector")
        Weights.append(110)
        Symbols.append("Adj.Payer")
        Weights.append(120)

    if Source == "Arms Dealer":
        Weights[0] = 49
        Weights[3] = 33
        Weights[7] = 5
    if Source != "Arms Dealer":
        Symbols.append("Arms Dealer")
        Weights.append(50)
    if Source != "Arms Dealer" and Source != "Necromancer":
        Symbols.append("Necromancer")
        Weights.append(6)
    if UnlockedRows < 8 and Source != "Locked":
        Symbols.append("Unlocker")
        WeightList = [110, 90, 60, 45]
        Weights.append(WeightList[UnlockedRows - 4])
    if not HaveResetPlus1 and Source != "Arms Dealer" and Source != "Necromancer":
        Symbols.append("Reset +1")
        Weights.append(8)

    return random.choices(Symbols, weights=Weights, k=1)[0]


def RandomPersistentSymbol(ExistingFeature=0, ExistingPersistent=0.0, flag=""):
    # 定义函数和相应的字符串
    Symbol = ["Payer", "Collector", "Sniper", "Shapeshifter",
              "Collector Payer", "Jobs Advisor"]
    if flag != "Locked":
        Symbol.append("Adj.Payer")
        Symbol.append("Adj.Collector")
    # 定义权重
    if ExistingPersistent < 0.01:
        weights = [490, 310, 140, 40, 95, 16]
        if flag != "Locked":
            weights.append(400)
            weights.append(430)
        if ExistingFeature > 0:
            Symbol.append("Necromancer")
            weights.append(20)
    else:
        weights = [130, 110, 245, 120, 57, 14]
        if flag != "Locked":
            weights.append(150)
            weights.append(140)
        if ExistingFeature > 0:
            Symbol.append("Necromancer")
            weights.append(15)
    # 随机选择
    return random.choices(Symbol, weights=weights, k=1)[0]


CONST_UPGRADER_SYMBOLS = ["Collector", "Payer", "Adj.Collector", "Adj.Payer", "Sniper", "Collector Payer",
                          "Arms Dealer", "Necromancer", "Jobs Advisor"]
# CONST_ArmsDealer_SYMBOLS = ["Collector", "Payer", "Adj.Collector", "Adj.Payer", "Sniper", "Collector Payer", "Unlocker",
#                            "Upgrader", "Jobs Advisor", "Supplier"]
CONST_NECROMANCER_SYMBOLS = ["Collector", "Payer", "Adj.Collector", "Adj.Payer", "Sniper", "Collector Payer",
                             "Unlocker",
                             "Upgrader", "Arms Dealer", "Jobs Advisor", "Supplier"]
CONST_DOOMSDAY_SYMBOLS = ["Collector", "Payer", "Adj.Collector", "Adj.Payer", "Collector Payer",
                          "Sniper", "Arms Dealer", "Shapeshifter", "Dynamite", "Synchronizer",
                          "Jobs Advisor"]


def FlipCollectorPayer(SourceSymbol, Round):
    SourceSymbol.IsAffected = True
    if SourceSymbol.Symbol == "Collector":
        return "Payer"
    if SourceSymbol.Symbol == "Payer":
        return "Collector"
    if SourceSymbol.Symbol == "Adj.Collector":
        return "Adj.Payer"
    if SourceSymbol.Symbol == "Adj.Payer":
        return "Adj.Collector"
    # 若还在继续, 则是随机的选择了一个普通符号
    if len(FindSymbols(Round, "Adjacent", False, SourceSymbol.X, SourceSymbol.Y)) > 0:
        Weight = [20, 20, 30, 30]
        NewSymbol = ["Adj.Collector", "Adj.Payer", "Collector", "Payer"]
    else:
        Weight = [50, 50]
        NewSymbol = ["Collector", "Payer"]
    return random.choices(NewSymbol, weights=Weight, k=1)[0]


def FindSymbols(BonusRound, Requirement, SearchForEmpty=False, X=-1, Y=-1, Extra_param=""):
    # EligibleBlocks = FindBlocks(self, "NonEmpty", SourceBlock.X, SourceBlock.Y)

    Eligible_Blocks = []
    if Requirement == "Row":
        for obj in BonusRound.Blocks:
            if obj.Y == Y:
                Eligible_Blocks.append(obj)
    if Requirement == "Column":
        for obj in BonusRound.Blocks:
            if obj.Locked == False and obj.X == X:
                Eligible_Blocks.append(obj)
    if Requirement == "Empty":  # 空的
        for obj in BonusRound.Blocks:
            if obj.Type == 0 and obj.Locked == False and not obj.IsSamePosition(X, Y):
                Eligible_Blocks.append(obj)
    if Requirement == "NonEmpty":  # 空的
        for obj in BonusRound.Blocks:
            if obj.Type != 0 and obj.Locked == False and not obj.IsSamePosition(X, Y):
                Eligible_Blocks.append(obj)

    if Requirement == "Regular":
        for obj in BonusRound.Blocks:
            if obj.Type == 1 and obj.Locked == False and not obj.IsSamePosition(X, Y):
                Eligible_Blocks.append(obj)
    if Requirement == "Feature":
        # 就业顾问
        if Extra_param == "Jobs Advisor":
            for obj in BonusRound.Blocks:
                if not obj.Locked and obj.Symbol in ["Collector", "Payer", "Adj.Collector", "Adj.Payer"] and \
                        ((obj.Type == 3) or (obj.Type == 2)) and (obj.Activated or obj.Type == 3) \
                        and not obj.IsSamePosition(X, Y):
                    Eligible_Blocks.append(obj)
            if len(Eligible_Blocks) == 0:
                for obj in BonusRound.Blocks:
                    if obj.Type != 0 and obj.Locked == False and not obj.IsSamePosition(X, Y):
                        Eligible_Blocks.append(obj)

        if Extra_param == "Upgrader":
            for obj in BonusRound.Blocks:
                if obj.Type == 2 and obj.Locked == False and obj.Symbol in CONST_UPGRADER_SYMBOLS \
                        and not obj.IsSamePosition(X, Y):
                    Eligible_Blocks.append(obj)
        if Extra_param == "Necromancer":

            for obj in BonusRound.Blocks:

                if obj.Type == 2 and obj.Locked == False and obj.Symbol in CONST_NECROMANCER_SYMBOLS \
                        and not obj.IsSamePosition(X, Y) and obj.Activated \
                        and not (BonusRound.UnlockedRows >= 8 and obj.Symbol == "Unlocker"):
                    Eligible_Blocks.append(obj)
        if Extra_param == "DOOMSDAY":
            for obj in BonusRound.Blocks:

                if obj.Type >= 2 and obj.Locked == False and obj.Symbol in CONST_DOOMSDAY_SYMBOLS:
                    Eligible_Blocks.append(obj)

    # Target = FindBlocks(self, "Adjacent", SearchForEmpty=False, X=SourceBlock.X, Y=SourceBlock.Y)
    if Requirement == "Adjacent":  # 周围的
        for obj in BonusRound.Blocks:
            if abs(obj.X - X) <= 1 and abs(obj.Y - Y) <= 1 and \
                    obj.Locked == False and not obj.IsSamePosition(X, Y) and obj.Type >= 0:
                if obj.IsEmpty() == SearchForEmpty:
                    Eligible_Blocks.append(obj)

    return Eligible_Blocks


def RandomUpfrontValue(isPayer=False):
    NewValueIndex = 0
    Predefined_Values = [1, 2, 3, 4, 5,
                         6, 7, 8, 9, 10,
                         15, 20, 25, 30, 50,
                         100, 150, 200, 300, 500,
                         1000, 2000, 3000, 5000, 10000]
    Success_Rate = [80, 80, 80, 80, 80,
                    60, 60, 60, 60, 60,
                    50, 50, 50, 50, 50,
                    40, 40, 40, 40, 40,
                    25, 20, 15, 10]
    if isPayer:
        Success_Rate = [65, 65, 65, 65, 65,
                        55, 55, 55, 55, 55,
                        40, 40, 40, 40, 40,
                        30, 30, 30, 30, 30,
                        20, 15, 10, 5]
    while NewValueIndex < len(Predefined_Values) - 1:
        RNG = random.randint(1, 100)
        if RNG < Success_Rate[NewValueIndex]:
            NewValueIndex += 1
        else:
            break
    return Predefined_Values[NewValueIndex]


# 寻找可以是
def SearchPlaceThatCanBeAdj(Round, Requirement_Empty=True):
    Place = []
    for obj in Round.Blocks:
        if obj.Locked or obj.IsEmpty() != Requirement_Empty:
            continue
        Adj = FindSymbols(Round, "Adjacent", False, X=obj.X, Y=obj.Y)
        RemoveDynamites(Adj)
        if len(Adj) > 0:
            Place.append(obj)

    return Place


def RemoveDynamites(Symbols):
    NewList = [obj for obj in Symbols if obj.Symbol != "Dynamite"]
    return NewList


def GetRoundCost(BonusOption):
    return 0 * BonusOption


def FormatStars(stars):
    formatted_stars = ""
    flag = False
    while stars >= 10:
        stars -= 10
        formatted_stars += "★★★★★"
        if stars > 0:
            flag = not flag
            if flag:
                formatted_stars += " "
            else:
                formatted_stars += "\n"
    while stars >= 2:
        stars -= 2
        formatted_stars += "★"
    if stars == 1:
        formatted_stars += "☆"
    return formatted_stars


ThisRound = Round()
