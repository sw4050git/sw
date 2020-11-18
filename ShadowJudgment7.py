import os
import pickle
import tkinter as tk
import tkinter.filedialog
from tkinter import ttk
import win32gui
from PIL import ImageGrab
import cv2
import numpy as np

class Application(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.pack()
        self.dt = [0]*32
        self.reset = [0]*32

        self.judgeflg = False
        self.flg_cl = False
        self.flg_play = False
        self.flg_game = False
        self.flg_hide_his = True
        self.flg_hide_res = True
        self.judge_cl = [0]*8
        self.judge_play = [0]*2
        self.judge_game = [0]*2
        self.deckname = "未選択"
        self.file_name = ""

        self.images_cl = []
        self.images_cl.append(cv2.imread('images/e2.png', 1))
        self.images_cl.append(cv2.imread('images/r2.png', 1))
        self.images_cl.append(cv2.imread('images/w2.png', 1))
        self.images_cl.append(cv2.imread('images/d2.png', 1))
        self.images_cl.append(cv2.imread('images/nc2.png', 1))
        self.images_cl.append(cv2.imread('images/v2.png', 1))
        self.images_cl.append(cv2.imread('images/b2.png', 1))
        self.images_cl.append(cv2.imread('images/nm2.png', 1))

        self.images_play = []
        self.images_play.append(cv2.imread('images/first.png', 1))
        self.images_play.append(cv2.imread('images/second.png', 1))

        self.images_game = []
        self.images_game.append(cv2.imread('images/win.png', 1))
        self.images_game.append(cv2.imread('images/lose.png', 1))

        self.names_cl = []
        self.names_cl.append("エルフ　")
        self.names_cl.append("ロイヤル")
        self.names_cl.append("ウィッチ")
        self.names_cl.append("ドラゴン")
        self.names_cl.append("ネクロ　")
        self.names_cl.append("ヴァンプ")
        self.names_cl.append("ビショップ")
        self.names_cl.append("ネメシス")

        self.names_play = []
        self.names_play.append("先攻")
        self.names_play.append("後攻")

        self.names_game = []
        self.names_game.append("勝利")
        self.names_game.append("敗北")

        self.TARGET_NAME = 'Shadowverse'
        self.master.geometry("320x350")
        self.master.title("ShadowJudgment")

        self.create_widgets()
        self.hidelabel_his()
        self.hidelabel_res()
        self.setresult()

    def create_widgets(self):

        #Label
        self.label_exp = ttk.Label(self)
        self.label_exp.configure(text="""シャドバ勝敗自動判定プログラム\nバトル設定から「対戦相手のスキンをデフォルトにする」\nにチェックを入れてください""")
        self.label_exp.grid(column=0, columnspan=2, row=0, pady=5)

        self.Deckregist = ttk.LabelFrame(self, text="デッキ登録")

        self.label_regist1 = ttk.Label(self.Deckregist)
        self.label_regist1.configure(text="使用するデッキ名を入力")
        self.label_regist1.pack()

        self.name1 = tk.StringVar()
        self.entry_name1 = ttk.Entry(self.Deckregist)
        self.entry_name1.configure(textvariable=self.name1)
        self.entry_name1.pack()

        self.registbutton = ttk.Button(self.Deckregist)
        self.registbutton.configure(text="登録")
        self.registbutton.configure(command=self.regist)
        self.registbutton.pack()

        self.label_regist3 = ttk.Label(self.Deckregist, text="※すでに登録しているデッキと\n　同名のデッキを登録すると\n　戦績がリセットされます")
        self.label_regist3.pack()

        self.Deckregist.grid(column=0, row=1, rowspan=3)

        self.label_select = ttk.Label(self)
        self.label_select.configure(text="""使用するデッキを選び、\n判定開始をクリック""")
        self.label_select.grid(column=1, row=1)

        self.RadioButtons = ttk.LabelFrame(self, text="使用デッキ選択")

        self.deckselectbutton = ttk.Button(self.RadioButtons)
        self.deckselectbutton.configure(text="使用するデッキの\nデータファイルを選択")
        self.deckselectbutton.configure(command=self.deckselect)
        self.deckselectbutton.pack()

        self.decknamelabel = ttk.Label(self.RadioButtons)
        self.decknamelabel.configure(text="使用デッキ:" + self.deckname)
        self.decknamelabel.pack()

        self.RadioButtons.grid(column=1, row=2)

        self.startbutton = ttk.Button(self)
        self.startbutton.configure(text="判定開始")
        self.startbutton.configure(state="disable")
        self.startbutton.configure(command=self.judge)
        self.startbutton.grid(column=1, row=3)

        self.nowframe = ttk.LabelFrame(self, text="現在の試合")

        self.nowlabel_cl = ttk.Label(self.nowframe)
        self.nowlabel_cl.configure(text="クラス：--------")
        self.nowlabel_cl.grid(column=0, row=0)

        self.nowlabel_play = ttk.Label(self.nowframe)
        self.nowlabel_play.configure(text="　　手番：----")
        self.nowlabel_play.grid(column=1, row=0)

        self.nowlabel_game = ttk.Label(self.nowframe)
        self.nowlabel_game.configure(text="　　勝敗：----")
        self.nowlabel_game.grid(column=2, row=0)

        self.nowframe.grid(column=0, columnspan=2, row=4)

        self.hisframe = ttk.LabelFrame(self, text="直近5試合の結果(新しい順)")

        self.hidebutton_his = ttk.Button(self.hisframe, text="表示")
        self.hidebutton_his.configure(command=self.hidelabel_his)
        self.hidebutton_his.grid(column=0, row=0, sticky=tk.W)

        self.hislabel1_cl = ttk.Label(self.hisframe)
        self.hislabel1_cl.configure(text="クラス：--------")
        self.hislabel1_cl.grid(column=0, row=1)

        self.hislabel1_play = ttk.Label(self.hisframe)
        self.hislabel1_play.configure(text="　　手番：----")
        self.hislabel1_play.grid(column=1, row=1)

        self.hislabel1_game = ttk.Label(self.hisframe)
        self.hislabel1_game.configure(text="　　勝敗：----")
        self.hislabel1_game.grid(column=2, row=1)

        self.hislabel2_cl = ttk.Label(self.hisframe)
        self.hislabel2_cl.configure(text="クラス：--------")
        self.hislabel2_cl.grid(column=0, row=2)

        self.hislabel2_play = ttk.Label(self.hisframe)
        self.hislabel2_play.configure(text="　　手番：----")
        self.hislabel2_play.grid(column=1, row=2)

        self.hislabel2_game = ttk.Label(self.hisframe)
        self.hislabel2_game.configure(text="　　勝敗：----")
        self.hislabel2_game.grid(column=2, row=2)

        self.hislabel3_cl = ttk.Label(self.hisframe)
        self.hislabel3_cl.configure(text="クラス：--------")
        self.hislabel3_cl.grid(column=0, row=3)

        self.hislabel3_play = ttk.Label(self.hisframe)
        self.hislabel3_play.configure(text="　　手番：----")
        self.hislabel3_play.grid(column=1, row=3)

        self.hislabel3_game = ttk.Label(self.hisframe)
        self.hislabel3_game.configure(text="　　勝敗：----")
        self.hislabel3_game.grid(column=2, row=3)

        self.hislabel4_cl = ttk.Label(self.hisframe)
        self.hislabel4_cl.configure(text="クラス：--------")
        self.hislabel4_cl.grid(column=0, row=4)

        self.hislabel4_play = ttk.Label(self.hisframe)
        self.hislabel4_play.configure(text="　　手番：----")
        self.hislabel4_play.grid(column=1, row=4)

        self.hislabel4_game = ttk.Label(self.hisframe)
        self.hislabel4_game.configure(text="　　勝敗：----")
        self.hislabel4_game.grid(column=2, row=4)

        self.hislabel5_cl = ttk.Label(self.hisframe)
        self.hislabel5_cl.configure(text="クラス：--------")
        self.hislabel5_cl.grid(column=0, row=5)

        self.hislabel5_play = ttk.Label(self.hisframe)
        self.hislabel5_play.configure(text="　　手番：----")
        self.hislabel5_play.grid(column=1, row=5)

        self.hislabel5_game = ttk.Label(self.hisframe)
        self.hislabel5_game.configure(text="　　勝敗：----")
        self.hislabel5_game.grid(column=2, row=5)

        self.hisframe.grid(column=0, columnspan=2, row=5, sticky=tk.W+tk.E)

        self.judgeframe = ttk.LabelFrame(self, text="現在の戦績")

        self.hidebutton_res = ttk.Button(self.judgeframe, text="表示")
        self.hidebutton_res.configure(command=self.hidelabel_res)
        self.hidebutton_res.grid(column=0, row=0, sticky=tk.W)

        self.allframe = ttk.LabelFrame(self.judgeframe, text="全クラス")
        self.winrate = ttk.Label(self.allframe)
        self.winrate.pack()
        self.allframe.grid(column=0, row=1)

        self.eframe = ttk.LabelFrame(self.judgeframe, text="対エルフ")
        self.ewinrate = ttk.Label(self.eframe)
        self.ewinrate.pack()
        self.eframe.grid(column=1, row=1)

        self.rframe = ttk.LabelFrame(self.judgeframe, text="対ロイヤル")
        self.rwinrate = ttk.Label(self.rframe)
        self.rwinrate.pack()
        self.rframe.grid(column=2, row=1)

        self.wframe = ttk.LabelFrame(self.judgeframe, text="対ウィッチ")
        self.wwinrate = ttk.Label(self.wframe)
        self.wwinrate.pack()
        self.wframe.grid(column=0, row=2)

        self.dframe = ttk.LabelFrame(self.judgeframe, text="対ドラゴン")
        self.dwinrate = ttk.Label(self.dframe)
        self.dwinrate.pack()
        self.dframe.grid(column=1, row=2)

        self.ncframe = ttk.LabelFrame(self.judgeframe, text="対ネクロ")
        self.ncwinrate = ttk.Label(self.ncframe)
        self.ncwinrate.pack()
        self.ncframe.grid(column=2, row=2)

        self.vframe = ttk.LabelFrame(self.judgeframe, text="対ヴァンプ")
        self.vwinrate = ttk.Label(self.vframe)
        self.vwinrate.pack()
        self.vframe.grid(column=0, row=3)

        self.bframe = ttk.LabelFrame(self.judgeframe, text="対ビショップ")
        self.bwinrate = ttk.Label(self.bframe)
        self.bwinrate.pack()
        self.bframe.grid(column=1, row=3)

        self.nmframe = ttk.LabelFrame(self.judgeframe, text="対ネメシス")
        self.nmwinrate = ttk.Label(self.nmframe)
        self.nmwinrate.pack()
        self.nmframe.grid(column=2, row=3)

        self.judgeframe.grid(column=0, columnspan=2, row=6, sticky=tk.W+tk.E)

    def deckselect(self):
        fTyp = [("", "*")]
        iDir = "data"
        self.file_name = tk.filedialog.askopenfilename(filetypes=fTyp, initialdir=iDir)
        name = os.path.splitext(os.path.basename(self.file_name))[0]
        if len(self.file_name) == 0:
            self.deckname = '未選択'
            self.startbutton.configure(state="disable")
            self.decknamelabel.configure(text="使用デッキ:" + self.deckname)
        else:
            self.deckname = name
            a = open(self.file_name, 'rb')
            self.dt = pickle.load(a)
            self.decknamelabel.configure(text="使用デッキ:" + self.deckname)
            self.startbutton.configure(state="active")
            self.setresult()
            self.resethistry()

    def regist(self):
        self.dt = [0]*32
        try:
            with open('data/'+ self.name1.get() +'.binaryfile', 'wb') as b:
                pickle.dump(self.reset, b)
            self.name1.set("")
            self.label_regist1.configure(text="使用するデッキ名を入力")
        except OSError:
            self.label_regist1.configure(text='デッキ名に使用できない\n文字列が含まれています。\n「￥,/,:,*,?,",<>,|」は\nデッキ名に使用しないで下さい。')

    def judge(self):
        if self.judgeflg is False:
            self.judgeflg = True
            self.entry_name1.configure(state="disable")
            self.registbutton.configure(state="disable")
            self.deckselectbutton.configure(state="disable")
            self.startbutton.configure(text="判定終了")
            self.master.after(1000, self.judgestart)
        elif self.judgeflg is True:
            self.judgeflg = False
            self.entry_name1.configure(state="active")
            self.registbutton.configure(state="active")
            self.deckselectbutton.configure(state="active")
            self.startbutton.configure(text="判定開始")
            self.judgefinish()

    def judgestart(self):

        if self.judgeflg is True:
            #クラスの判定
            if self.flg_cl is False:
                self.judge_cl = [0]*8
                handle = win32gui.FindWindow(None, self.TARGET_NAME)
                rect = win32gui.GetWindowRect(handle)
                top = rect[1]+31
                bot = rect[3]-8
                lef = rect[0]+8
                rig = rect[2]-8
                im = ImageGrab.grab((lef+(rig-lef)/2, top, rig, bot-(bot-top)/2))
                window_im = np.asarray(im)
                cvcolor = cv2.cvtColor(window_im, cv2.COLOR_BGR2RGB)

                for i in range(8):
                    self.imagecheck_cl(self.images_cl[i], cvcolor, i)

                self.after(1000, self.judgestart)
                return

            #先攻後攻の判定
            if self.flg_cl is True and self.flg_play is False:
                self.judge_play = [0]*2
                handle = win32gui.FindWindow(None, self.TARGET_NAME)
                rect = win32gui.GetWindowRect(handle)
                top = rect[1]+31
                bot = rect[3]-8
                lef = rect[0]+8
                rig = rect[2]-8
                im = ImageGrab.grab((lef+(rig-lef)/2+(rig-lef)/10, top+(bot-top)/2, rig, bot))
                window_im = np.asarray(im)
                cvcolor = cv2.cvtColor(window_im, cv2.COLOR_BGR2RGB)

                for i in range(2):
                    self.imagecheck_play(self.images_play[i], cvcolor, i)

                self.after(200, self.judgestart)
                return

            #勝敗の判定
            if self.flg_cl is True and self.flg_play is True and self.flg_game is False:
                self.judge_game = [0]*2
                handle = win32gui.FindWindow(None, self.TARGET_NAME)
                rect = win32gui.GetWindowRect(handle)
                top = rect[1]+31
                bot = rect[3]-8
                lef = rect[0]+8
                rig = rect[2]-8
                im = ImageGrab.grab((lef, top+(bot-top)/3, rig, bot-(bot-top)/3))
                window_im = np.asarray(im)
                cvcolor = cv2.cvtColor(window_im, cv2.COLOR_BGR2RGB)

                for i in range(2):
                    self.imagecheck_game(self.images_game[i], cvcolor, i)

                self.after(500, self.judgestart)
                return

            if self.flg_cl is True and self.flg_play is True and self.flg_game is True:
                #戦績データの格納
                #0～3 エルフ 4～7 ロイヤル 8～11 ウィッチ 12～15 ドラゴン 16~19 ネクロ 20~23 ヴァンプ 24～27 ビショ 28～31 ネメ
                #4n 先攻勝利 4n+1 先攻敗北 4n+2 後攻勝利 4n+3 後攻敗北
                for i in range(8):
                    if int(self.judge_cl[i]) == 1:
                        if int(self.judge_play[0]) == 1:
                            if int(self.judge_game[0]) == 1:
                                num = 4*i
                                self.dt[num] += 1
                            if int(self.judge_game[1]) == 1:
                                num = (4*i)+1
                                self.dt[num] += 1
                        if int(self.judge_play[1]) == 1:
                            if int(self.judge_game[0]) == 1:
                                num = (4*i)+2
                                self.dt[num] += 1
                            if int(self.judge_game[1]) == 1:
                                num = (4*i)+3
                                self.dt[num] += 1
                self.setresult()
                self.flg_cl = False
                self.flg_play = False
                self.flg_game = False

                self.after(1000, self.judgestart)
                return
        else:
            self.flg_cl = False
            self.flg_play = False
            self.flg_game = False
            self.setresult()
            return

    def judgefinish(self):
        with open(self.file_name, 'wb') as web:
            pickle.dump(self.dt, web)

    def setresult(self):
        game_num = sum(self.dt)
        e_num = sum(self.dt[0:4])
        r_num = sum(self.dt[4:8])
        w_num = sum(self.dt[8:12])
        d_num = sum(self.dt[12:16])
        nc_num = sum(self.dt[16:20])
        v_num = sum(self.dt[20:24])
        b_num = sum(self.dt[24:28])
        nm_num = sum(self.dt[28:32])
        first_win_num = 0
        first_lose_num = 0
        second_win_num = 0
        second_lose_num = 0
        for i in range(8):
            first_win_num += self.dt[4*i]
            first_lose_num += self.dt[4*i+1]
            second_win_num += self.dt[4*i+2]
            second_lose_num += self.dt[4*i+3]
        first_num = first_win_num+first_lose_num
        second_num = second_win_num+second_lose_num
        win_num = first_win_num+second_win_num

        win_rate = self.cal_rate(win_num, game_num)
        first_win_rate = self.cal_rate(first_win_num, first_num)
        second_win_rate = self.cal_rate(second_win_num, second_num)

        e_win_rate = self.cal_rate(self.dt[0]+self.dt[2], e_num)
        e_first_win_rate = self.cal_rate(self.dt[0], sum(self.dt[0:2]))
        e_second_win_rate = self.cal_rate(self.dt[2], sum(self.dt[2:4]))

        r_win_rate = self.cal_rate(self.dt[4]+self.dt[6], r_num)
        r_first_win_rate = self.cal_rate(self.dt[4], sum(self.dt[4:6]))
        r_second_win_rate = self.cal_rate(self.dt[6], sum(self.dt[6:8]))

        w_win_rate = self.cal_rate(self.dt[8]+self.dt[10], w_num)
        w_first_win_rate = self.cal_rate(self.dt[8], sum(self.dt[8:10]))
        w_second_win_rate = self.cal_rate(self.dt[10], sum(self.dt[10:12]))

        d_win_rate = self.cal_rate(self.dt[12]+self.dt[14], d_num)
        d_first_win_rate = self.cal_rate(self.dt[12], sum(self.dt[12:14]))
        d_second_win_rate = self.cal_rate(self.dt[14], sum(self.dt[14:16]))

        nc_win_rate = self.cal_rate(self.dt[16]+self.dt[18], nc_num)
        nc_first_win_rate = self.cal_rate(self.dt[16], sum(self.dt[16:18]))
        nc_second_win_rate = self.cal_rate(self.dt[18], sum(self.dt[18:20]))

        v_win_rate = self.cal_rate(self.dt[20]+self.dt[22], v_num)
        v_first_win_rate = self.cal_rate(self.dt[20], sum(self.dt[20:22]))
        v_second_win_rate = self.cal_rate(self.dt[22], sum(self.dt[22:24]))

        b_win_rate = self.cal_rate(self.dt[24]+self.dt[26], b_num)
        b_first_win_rate = self.cal_rate(self.dt[24], sum(self.dt[24:26]))
        b_second_win_rate = self.cal_rate(self.dt[26], sum(self.dt[26:28]))

        nm_win_rate = self.cal_rate(self.dt[28]+self.dt[30], nm_num)
        nm_first_win_rate = self.cal_rate(self.dt[28], sum(self.dt[28:30]))
        nm_second_win_rate = self.cal_rate(self.dt[30], sum(self.dt[30:32]))

        self.winrate.configure(text="試合数:" + str(game_num) + "\n勝率:" + str(round(win_rate, 1)) + "%\n先攻数:" + str(first_num) + "\n後攻数:"+ str(second_num) + "\n先攻勝率" + str(round(first_win_rate, 1)) + "%\n後攻勝率:"+ str(round(second_win_rate, 1))+"%")
        self.ewinrate.configure(text="試合数:" + str(e_num) + "\n勝率:" + str(round(e_win_rate, 1)) + "%\n先攻数:" + str(sum(self.dt[0:2])) + "\n後攻数:"+ str(sum(self.dt[2:4])) + "\n先攻勝率:" + str(round(e_first_win_rate, 1)) + "%\n後攻勝率:"+ str(round(e_second_win_rate, 1))+"%")
        self.rwinrate.configure(text="試合数:" + str(r_num) + "\n勝率:" + str(round(r_win_rate, 1)) + "%\n先攻数:" + str(sum(self.dt[4:6])) + "\n後攻数:"+ str(sum(self.dt[6:8])) + "\n先攻勝率:" + str(round(r_first_win_rate, 1)) + "%\n後攻勝率:"+ str(round(r_second_win_rate, 1))+"%")
        self.wwinrate.configure(text="試合数:" + str(w_num) + "\n勝率:" + str(round(w_win_rate, 1)) + "%\n先攻数:" + str(sum(self.dt[8:10])) + "\n後攻数:"+ str(sum(self.dt[10:12])) + "\n先攻勝率:" + str(round(w_first_win_rate, 1)) + "%\n後攻勝率:"+ str(round(w_second_win_rate, 1))+"%")
        self.dwinrate.configure(text="試合数:" + str(d_num) + "\n勝率:" + str(round(d_win_rate, 1)) + "%\n先攻数:" + str(sum(self.dt[12:14])) + "\n後攻数:"+ str(sum(self.dt[14:16])) + "\n先攻勝率:" + str(round(d_first_win_rate, 1)) + "%\n後攻勝率:"+ str(round(d_second_win_rate, 1))+"%")
        self.ncwinrate.configure(text="試合数:" + str(nc_num) + "\n勝率:" + str(round(nc_win_rate, 1)) + "%\n先攻数:" + str(sum(self.dt[16:18])) + "\n後攻数:"+ str(sum(self.dt[18:20])) + "\n先攻勝率:" + str(round(nc_first_win_rate, 1)) + "%\n後攻勝率:"+ str(round(nc_second_win_rate, 1))+"%")
        self.vwinrate.configure(text="試合数:" + str(v_num) + "\n勝率:" + str(round(v_win_rate, 1)) + "%\n先攻数:" + str(sum(self.dt[20:22])) + "\n後攻数:"+ str(sum(self.dt[22:24])) + "\n先攻勝率:" + str(round(v_first_win_rate, 1)) + "%\n後攻勝率:"+ str(round(v_second_win_rate, 1))+"%")
        self.bwinrate.configure(text="試合数:" + str(b_num) + "\n勝率:" + str(round(b_win_rate, 1)) + "%\n先攻数:" + str(sum(self.dt[24:26])) + "\n後攻数:"+ str(sum(self.dt[26:28])) + "\n先攻勝率:" + str(round(b_first_win_rate, 1)) + "%\n後攻勝率:"+ str(round(b_second_win_rate, 1))+"%")
        self.nmwinrate.configure(text="試合数:" + str(nm_num) + "\n勝率:" + str(round(nm_win_rate, 1)) + "%\n先攻数:" + str(sum(self.dt[28:30])) + "\n後攻数:"+ str(sum(self.dt[30:32])) + "\n先攻勝率:" + str(round(nm_first_win_rate, 1)) + "%\n後攻勝率:"+ str(round(nm_second_win_rate, 1))+"%")

    def cal_rate(self, x, y):
        try:
            result = (float(x)/y)*100
        except ZeroDivisionError:
            result = float(0)
        return result

    def imagecheck_cl(self, image1, image2, x):

        akaze = cv2.AKAZE_create()

        kp1, des1 = akaze.detectAndCompute(image1, None)
        kp2, des2 = akaze.detectAndCompute(image2, None)

        if des2 is None:
            cv2.waitKey(1)
        elif des2.shape[0] <= 1:
            cv2.waitKey(1)
        else:
            bf = cv2.BFMatcher()
            matches = bf.knnMatch(des1, des2, k=2)
            ratio = 0.5
            good = []
            for m, n in matches:
                if m.distance < ratio * n.distance:
                    good.append([m])
            if len(good) > 20:
                self.judge_cl[x] += 1
                self.flg_cl = True
                self.sethistry()
                self.nowlabel_cl.configure(text="クラス："+str(self.names_cl[x]))

    def imagecheck_play(self, image1, image2, x):

        akaze = cv2.AKAZE_create()

        kp1, des1 = akaze.detectAndCompute(image1, None)
        kp2, des2 = akaze.detectAndCompute(image2, None)

        if des2 is None or des2.shape[1] != 61:
            cv2.waitKey(1)
        elif des2.shape[0] <= 1:
            cv2.waitKey(1)
        else:
            bf = cv2.BFMatcher()
            matches = bf.knnMatch(des1, des2, k=2)
            ratio = 0.58
            good = []
            for m, n in matches:
                if m.distance < ratio * n.distance:
                    good.append([m])
            if len(good) > 3:
                self.judge_play[x] += 1
                self.flg_play = True
                self.nowlabel_play.configure(text="　　手番："+str(self.names_play[x]))

    def imagecheck_game(self, image1, image2, x):

        akaze = cv2.AKAZE_create()

        kp1, des1 = akaze.detectAndCompute(image1, None)
        kp2, des2 = akaze.detectAndCompute(image2, None)

        if des2 is None or des2.shape[1] != 61:
            cv2.waitKey(1)
        elif des2.shape[0] <= 1:
            cv2.waitKey(1)
        else:
            bf = cv2.BFMatcher()
            matches = bf.knnMatch(des1, des2, k=2)
            ratio = 0.5
            good = []
            for m, n in matches:
                if m.distance < ratio * n.distance:
                    good.append([m])
            if len(good) > 5:
                self.judge_game[x] += 1
                self.flg_game = True
                self.nowlabel_game.configure(text="　　勝敗："+str(self.names_game[x]))

    def hidelabel_his(self):
        if self.flg_hide_his is True:
            self.hislabel1_cl.grid_remove()
            self.hislabel1_play.grid_remove()
            self.hislabel1_game.grid_remove()
            self.hislabel2_cl.grid_remove()
            self.hislabel2_play.grid_remove()
            self.hislabel2_game.grid_remove()
            self.hislabel3_cl.grid_remove()
            self.hislabel3_play.grid_remove()
            self.hislabel3_game.grid_remove()
            self.hislabel4_cl.grid_remove()
            self.hislabel4_play.grid_remove()
            self.hislabel4_game.grid_remove()
            self.hislabel5_cl.grid_remove()
            self.hislabel5_play.grid_remove()
            self.hislabel5_game.grid_remove()
            self.flg_hide_his = False
            self.hidebutton_his.configure(text="表示")
            if self.flg_hide_res is False:
                self.master.geometry("320x350")
            else:
                self.master.geometry("320x700")

        else:
            self.hislabel1_cl.grid()
            self.hislabel1_play.grid()
            self.hislabel1_game.grid()
            self.hislabel2_cl.grid()
            self.hislabel2_play.grid()
            self.hislabel2_game.grid()
            self.hislabel3_cl.grid()
            self.hislabel3_play.grid()
            self.hislabel3_game.grid()
            self.hislabel4_cl.grid()
            self.hislabel4_play.grid()
            self.hislabel4_game.grid()
            self.hislabel5_cl.grid()
            self.hislabel5_play.grid()
            self.hislabel5_game.grid()
            self.flg_hide_his = True
            self.hidebutton_his.configure(text="非表示")
            if self.flg_hide_res is False:
                self.master.geometry("320x440")
            else:
                self.master.geometry("320x780")

    def hidelabel_res(self):
        if self.flg_hide_res is True:
            self.allframe.grid_remove()
            self.eframe.grid_remove()
            self.rframe.grid_remove()
            self.wframe.grid_remove()
            self.dframe.grid_remove()
            self.ncframe.grid_remove()
            self.vframe.grid_remove()
            self.bframe.grid_remove()
            self.nmframe.grid_remove()
            self.flg_hide_res = False
            self.hidebutton_res.configure(text="表示")
            if self.flg_hide_his is False:
                self.master.geometry("320x350")
            else:
                self.master.geometry("320x440")
        else:
            self.allframe.grid()
            self.eframe.grid()
            self.rframe.grid()
            self.wframe.grid()
            self.dframe.grid()
            self.ncframe.grid()
            self.vframe.grid()
            self.bframe.grid()
            self.nmframe.grid()
            self.flg_hide_res = True
            self.hidebutton_res.configure(text="非表示")
            if self.flg_hide_his is False:
                self.master.geometry("320x690")
            else:
                self.master.geometry("320x780")

    def sethistry(self):
        self.hislabel5_cl.configure(text=self.hislabel4_cl.cget("text"))
        self.hislabel5_play.configure(text=self.hislabel4_play.cget("text"))
        self.hislabel5_game.configure(text=self.hislabel4_game.cget("text"))
        self.hislabel4_cl.configure(text=self.hislabel3_cl.cget("text"))
        self.hislabel4_play.configure(text=self.hislabel3_play.cget("text"))
        self.hislabel4_game.configure(text=self.hislabel3_game.cget("text"))
        self.hislabel3_cl.configure(text=self.hislabel2_cl.cget("text"))
        self.hislabel3_play.configure(text=self.hislabel2_play.cget("text"))
        self.hislabel3_game.configure(text=self.hislabel2_game.cget("text"))
        self.hislabel2_cl.configure(text=self.hislabel1_cl.cget("text"))
        self.hislabel2_play.configure(text=self.hislabel1_play.cget("text"))
        self.hislabel2_game.configure(text=self.hislabel1_game.cget("text"))
        self.hislabel1_cl.configure(text=self.nowlabel_cl.cget("text"))
        self.hislabel1_play.configure(text=self.nowlabel_play.cget("text"))
        self.hislabel1_game.configure(text=self.nowlabel_game.cget("text"))
        self.nowlabel_cl.configure(text="クラス：--------")
        self.nowlabel_play.configure(text="　　手番：----")
        self.nowlabel_game.configure(text="　　勝敗：----")

    def resethistry(self):
        self.hislabel5_cl.configure(text="クラス：--------")
        self.hislabel5_play.configure(text="　　手番：----")
        self.hislabel5_game.configure(text="　　勝敗：----")
        self.hislabel4_cl.configure(text="クラス：--------")
        self.hislabel4_play.configure(text="　　手番：----")
        self.hislabel4_game.configure(text="　　勝敗：----")
        self.hislabel3_cl.configure(text="クラス：--------")
        self.hislabel3_play.configure(text="　　手番：----")
        self.hislabel3_game.configure(text="　　勝敗：----")
        self.hislabel2_cl.configure(text="クラス：--------")
        self.hislabel2_play.configure(text="　　手番：----")
        self.hislabel2_game.configure(text="　　勝敗：----")
        self.hislabel1_cl.configure(text="クラス：--------")
        self.hislabel1_play.configure(text="　　手番：----")
        self.hislabel1_game.configure(text="　　勝敗：----")
        self.nowlabel_cl.configure(text="クラス：--------")
        self.nowlabel_play.configure(text="　　手番：----")
        self.nowlabel_game.configure(text="　　勝敗：----")

def main():
    root = tk.Tk()
    app = Application(master=root)
    app.mainloop()

if __name__ == "__main__":
    main()
