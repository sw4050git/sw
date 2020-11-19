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
    #初期化処理
    def __init__(self, master):
        super().__init__(master)
        self.pack()
        #戦績データ格納用リスト
        self.dt = [0]*32
        #戦績データリセット用リスト
        self.reset = [0]*32

        #フラグ
        self.flg_judge = False #判定中か否か
        self.flg_cl = False #クラスの判定が終了したか否か
        self.flg_play = False #手番の判定が終了したか否か
        self.flg_game = False #勝敗の判定が終了したか否か
        self.flg_hide_his = True #過去5戦の結果が非表示か否か
        self.flg_hide_res = True #戦績が非表示か否か

        #判定中における、判定結果の一時保存用リスト
        self.judge_cl = [0]*8
        self.judge_play = [0]*2
        self.judge_game = [0]*2

        #選択中のデッキ名表示用テキスト
        self.deckname = "未選択"
        #デッキ登録、選択の際のファイルネーム格納用
        self.file_name = ""

        #クラス判定用の画像の読み込み
        self.images_cl = []
        self.images_cl.append(cv2.imread('images/e2.png', 1))
        self.images_cl.append(cv2.imread('images/r2.png', 1))
        self.images_cl.append(cv2.imread('images/w2.png', 1))
        self.images_cl.append(cv2.imread('images/d2.png', 1))
        self.images_cl.append(cv2.imread('images/nc2.png', 1))
        self.images_cl.append(cv2.imread('images/v2.png', 1))
        self.images_cl.append(cv2.imread('images/b2.png', 1))
        self.images_cl.append(cv2.imread('images/nm2.png', 1))

        #手番判定用の画像の読み込み
        self.images_play = []
        self.images_play.append(cv2.imread('images/first.png', 1))
        self.images_play.append(cv2.imread('images/second.png', 1))

        #勝敗判定用の画像の読み込み
        self.images_game = []
        self.images_game.append(cv2.imread('images/win.png', 1))
        self.images_game.append(cv2.imread('images/lose.png', 1))

        #クラス名表示用テキストの読み込み
        self.names_cl = []
        self.names_cl.append("全クラス")
        self.names_cl.append("エルフ　")
        self.names_cl.append("ロイヤル")
        self.names_cl.append("ウィッチ")
        self.names_cl.append("ドラゴン")
        self.names_cl.append("ネクロ　")
        self.names_cl.append("ヴァンプ")
        self.names_cl.append("ビショップ")
        self.names_cl.append("ネメシス")

        #手番表示用テキストの読み込み
        self.names_play = []
        self.names_play.append("先攻")
        self.names_play.append("後攻")

        #勝敗表示用テキストの読み込み
        self.names_game = []
        self.names_game.append("勝利")
        self.names_game.append("敗北")

        #シャドウバースのウィンドウをキャプチャのターゲットに設定
        self.TARGET_NAME = 'Shadowverse'

        #GUIの初期サイズの設定
        self.master.geometry("320x350")
        #GUIのタイトル
        self.master.title("ShadowJudgment")

        #GUIの作成および戦績の初期化。戦績、過去5戦結果は非表示の状態でスタート。
        self.create_widgets()
        self.hidelabel_his()
        self.hidelabel_res()
        self.setresult()

    #GUI全体の作成処理
    def create_widgets(self):

        #説明部分
        self.label_exp = ttk.Label(self)
        self.label_exp.configure(text="シャドバ勝敗自動判定プログラム\nバトル設定から「対戦相手のスキンをデフォルトにする」\nにチェックを入れてください")
        self.label_exp.grid(column=0, columnspan=2, row=0, pady=5)

        #デッキ登録部分
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

        #使用デッキ選択部分
        self.label_select = ttk.Label(self)
        self.label_select.configure(text="""使用するデッキを選び、\n判定開始をクリック""")
        self.label_select.grid(column=1, row=1)
        self.deckselectframe = ttk.LabelFrame(self, text="使用デッキ選択")
        self.deckselectbutton = ttk.Button(self.deckselectframe)
        self.deckselectbutton.configure(text="使用するデッキの\nデータファイルを選択")
        self.deckselectbutton.configure(command=self.deckselect)
        self.deckselectbutton.pack()
        self.decknamelabel = ttk.Label(self.deckselectframe)
        self.decknamelabel.configure(text="使用デッキ:" + self.deckname)
        self.decknamelabel.pack()
        self.deckselectframe.grid(column=1, row=2)

        #判定開始、終了部分
        self.startbutton = ttk.Button(self)
        self.startbutton.configure(text="判定開始")
        self.startbutton.configure(state="disable")
        self.startbutton.configure(command=self.judge)
        self.startbutton.grid(column=1, row=3)

        #現在の試合相手の表示
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

        #直近5試合の結果の表示
        self.hisframe = ttk.LabelFrame(self, text="直近5試合の結果(新しい順)")
        self.hidebutton_his = ttk.Button(self.hisframe, text="表示")
        self.hidebutton_his.configure(command=self.hidelabel_his)
        self.hidebutton_his.grid(column=0, row=0, sticky=tk.W)
        self.hislabels_cl = []
        self.hislabels_play = []
        self.hislabels_game = []
        for i in range(5):
            self.hislabels_cl.append(ttk.Label(self.hisframe))
            self.hislabels_play.append(ttk.Label(self.hisframe))
            self.hislabels_game.append(ttk.Label(self.hisframe))
            self.hislabels_cl[i].configure(text="クラス：--------")
            self.hislabels_play[i].configure(text="　　手番：----")
            self.hislabels_game[i].configure(text="　　勝敗：----")
            self.hislabels_cl[i].grid(column=0, row=i+1)
            self.hislabels_play[i].grid(column=1, row=i+1)
            self.hislabels_game[i].grid(column=2, row=i+1)
        self.hisframe.grid(column=0, columnspan=2, row=5, sticky=tk.W+tk.E)

        #戦績の表示
        self.judgeframe = ttk.LabelFrame(self, text="現在の戦績")
        self.hidebutton_res = ttk.Button(self.judgeframe, text="表示")
        self.hidebutton_res.configure(command=self.hidelabel_res)
        self.hidebutton_res.grid(column=0, row=0, sticky=tk.W)
        self.frames = []
        self.winrates = []
        for i in range(9):
            c = i%3
            if i < 3:
                j = 1
            elif i < 6:
                j = 2
            else:
                j = 3
            self.frames.append(ttk.LabelFrame(self.judgeframe, text="対"+self.names_cl[i]))
            self.winrates.append(ttk.Label(self.frames[i]))
            self.winrates[i].pack()
            self.frames[i].grid(column=c, row=j)
        self.judgeframe.grid(column=0, columnspan=2, row=6, sticky=tk.W+tk.E)

    #使用デッキ選択処理
    def deckselect(self):
        fTyp = [("", "*")]
        iDir = "data"
        self.file_name = tk.filedialog.askopenfilename(filetypes=fTyp, initialdir=iDir) #使用デッキのデータファイル選択
        name = os.path.splitext(os.path.basename(self.file_name))[0] #使用データファイルから、デッキ名部分のみ抽出
        if len(self.file_name) == 0: #データファイルが選択されなければ
            self.deckname = '未選択'
            self.startbutton.configure(state="disable")
            self.decknamelabel.configure(text="使用デッキ:" + self.deckname)
        else: #正常に選択されたら
            self.deckname = name
            data = open(self.file_name, 'rb') #データファイルから過去の戦績の読み出し
            self.dt = pickle.load(data)
            self.decknamelabel.configure(text="使用デッキ:" + self.deckname)
            self.startbutton.configure(state="active") #判定開始ボタンを押下可能に
            self.setresult() #戦績のセット
            self.resethistry() #過去5戦の結果のリセット

    #デッキ登録処理
    def regist(self):
        self.dt = [0]*32
        try:
            with open('data/'+ self.name1.get() +'.binaryfile', 'wb') as b: #入力されたデッキ名のデータファイルを作成
                pickle.dump(self.reset, b) #データを初期化
            self.name1.set("") #デッキ登録欄の初期化
            self.label_regist1.configure(text="使用するデッキ名を入力")
        except OSError: #ファイル名に使用できない文字列が含まれていた場合のエラー処理
            self.label_regist1.configure(text='デッキ名に使用できない\n文字列が含まれています。\n「￥,/,:,*,?,",<>,|」は\nデッキ名に使用しないで下さい。')

    #判定開始,終了ボタンを押した時の処理
    def judge(self):
        if self.flg_judge is False: #ボタン押下時、判定中じゃなければ
            self.flg_judge = True #判定状態に遷移
            self.entry_name1.configure(state="disable") #デッキ登録、デッキ選択を一時的に不可に
            self.registbutton.configure(state="disable")
            self.deckselectbutton.configure(state="disable")
            self.startbutton.configure(text="判定終了") #判定開始ボタンを判定終了ボタンに変更
            self.master.after(1000, self.judgestart) #判定を開始
        elif self.flg_judge is True: #ボタン押下時、判定中なら
            self.flg_judge = False #非判定状態に遷移
            self.entry_name1.configure(state="active") #デッキ登録、デッキ選択を再度可能に
            self.registbutton.configure(state="active")
            self.deckselectbutton.configure(state="active")
            self.startbutton.configure(text="判定開始") #判定終了ボタンを判定開始ボタンに変更
            self.judgefinish() #判定の終了

    #判定全体の処理
    def judgestart(self):
        #判定中なら
        if self.flg_judge is True:
            #画面キャプチャ
            handle = win32gui.FindWindow(None, self.TARGET_NAME)
            rect = win32gui.GetWindowRect(handle)
            top = rect[1]+31 #キャプチャの上限位置
            bot = rect[3]-8 #下限
            lef = rect[0]+8 #左限
            rig = rect[2]-8 #右限

            #クラスの判定
            if self.flg_cl is False:
                self.judge_cl = [0]*8
                im = ImageGrab.grab((lef+(rig-lef)/2, top, rig, bot-(bot-top)/2)) #クラス判定に必要な部分のみをキャプチャ
                window_im = np.asarray(im)
                cvcolor = cv2.cvtColor(window_im, cv2.COLOR_BGR2RGB)

                #1クラス毎に判定
                for i in range(8):
                    self.imagecheck_cl(self.images_cl[i], cvcolor, i)

                self.after(1000, self.judgestart)
                return

            #先攻後攻の判定
            elif self.flg_play is False:
                self.judge_play = [0]*2
                im = ImageGrab.grab((lef+(rig-lef)/2+(rig-lef)/10, top+(bot-top)/2, rig, bot)) #手番判定に必要な部分のみをキャプチャ
                window_im = np.asarray(im)
                cvcolor = cv2.cvtColor(window_im, cv2.COLOR_BGR2RGB)

                #手番を判定
                for i in range(2):
                    self.imagecheck_play(self.images_play[i], cvcolor, i)

                self.after(200, self.judgestart)
                return

            #勝敗の判定
            elif self.flg_game is False:
                self.judge_game = [0]*2
                im = ImageGrab.grab((lef, top+(bot-top)/3, rig, bot-(bot-top)/3)) #勝敗判定に必要な部分のみをキャプチャ
                window_im = np.asarray(im)
                cvcolor = cv2.cvtColor(window_im, cv2.COLOR_BGR2RGB)

                #勝敗を判定
                for i in range(2):
                    self.imagecheck_game(self.images_game[i], cvcolor, i)

                self.after(500, self.judgestart)
                return

            #全ての判定終了時に以下を実行
            else:
                #戦績データをself.dtに格納
                #以下self.dtのインデックス番号の意味
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
                self.setresult() #戦績を更新
                self.flg_cl = False #全てのフラグをリセット
                self.flg_play = False
                self.flg_game = False
                self.after(1000, self.judgestart)
                return

        #判定中じゃ無ければ
        else:
            self.flg_cl = False
            self.flg_play = False
            self.flg_game = False
            self.setresult()
            return

    #判定終了処理
    def judgefinish(self):
        #戦績データの保存
        with open(self.file_name, 'wb') as web:
            pickle.dump(self.dt, web)

    #戦績を戦績欄に表示する処理
    def setresult(self):

        #以下self.dt内の数値をもとに、戦績のカウント
        #以下self.dtのインデックス番号の意味
        #0～3 エルフ 4～7 ロイヤル 8～11 ウィッチ 12～15 ドラゴン 16~19 ネクロ 20~23 ヴァンプ 24～27 ビショ 28～31 ネメ
        #4n 先攻勝利 4n+1 先攻敗北 4n+2 後攻勝利 4n+3 後攻敗北

        #先攻勝利数、敗北数、後攻勝利数、敗北数のカウント
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

        #各クラスとの対面数のカウント、勝率、先攻勝率、後攻勝率の計算
        cl_nums = []
        cl_first_nums = []
        cl_second_nums = []
        win_rates = []
        first_win_rates = []
        second_win_rates = []
        cl_nums.append(sum(self.dt))
        cl_first_nums.append(first_win_num+first_lose_num)
        cl_second_nums.append(second_win_num+second_lose_num)
        win_rates.append(self.cal_rate(win_num, cl_nums[0]))
        first_win_rates.append(self.cal_rate(first_win_num, first_num))
        second_win_rates.append(self.cal_rate(second_win_num, second_num))
        for i in range(8):
            j = i*4
            cl_nums.append(sum(self.dt[j:j+4]))
            cl_first_nums.append(sum(self.dt[j:j+2]))
            cl_second_nums.append(sum(self.dt[j+2:j+4]))
            win_rates.append(self.cal_rate(self.dt[j]+self.dt[j+2], cl_nums[i+1]))
            first_win_rates.append(self.cal_rate(self.dt[j], sum(self.dt[j:j+2])))
            second_win_rates.append(self.cal_rate(self.dt[j+2], sum(self.dt[j+2:j+4])))

        #以上でカウントした情報を戦績表示欄に戦績をセット
        for i in range(9):
            self.winrates[i].configure(text="試合数:" + str(cl_nums[i]) + "\n勝率:" + str(round(win_rates[i], 1)) + "%\n先攻数:" + str(cl_first_nums[i]) + "\n後攻数:" + str(cl_second_nums[i]) + "\n先攻勝率:" + str(round(first_win_rates[i], 1)) + "%\n後攻勝率:" + str(round(second_win_rates[i], 1)) + "%")

    #勝率の計算処理
    def cal_rate(self, x, y):
        try:
            result = (float(x)/y)*100
        except ZeroDivisionError:
            result = float(0)
        return result

    #対面のクラスを判定する処理
    def imagecheck_cl(self, image1, image2, x):

        akaze = cv2.AKAZE_create()

        kp1, des1 = akaze.detectAndCompute(image1, None)
        kp2, des2 = akaze.detectAndCompute(image2, None)

        if des2 is None: #画像から特徴点が検出されない等のエラー処理
            return
        elif des2.shape[0] <= 1: #同上
            return
        else: #以下、特徴点マッチング
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
                self.nowlabel_cl.configure(text="クラス："+str(self.names_cl[x+1]))

    #手番を判定する処理
    def imagecheck_play(self, image1, image2, x):

        akaze = cv2.AKAZE_create()

        kp1, des1 = akaze.detectAndCompute(image1, None)
        kp2, des2 = akaze.detectAndCompute(image2, None)

        if des2 is None or des2.shape[1] != 61:
            return
        elif des2.shape[0] <= 1:
            return
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

    #勝敗を判定する処理
    def imagecheck_game(self, image1, image2, x):

        akaze = cv2.AKAZE_create()

        kp1, des1 = akaze.detectAndCompute(image1, None)
        kp2, des2 = akaze.detectAndCompute(image2, None)

        if des2 is None or des2.shape[1] != 61:
            return
        elif des2.shape[0] <= 1:
            return
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

    #過去5戦の結果表示欄の表示、非表示を行う処理
    def hidelabel_his(self):
        if self.flg_hide_his is True:
            for i in range(5):
                self.hislabels_cl[i].grid_remove()
                self.hislabels_play[i].grid_remove()
                self.hislabels_game[i].grid_remove()
            self.flg_hide_his = False
            self.hidebutton_his.configure(text="表示")
            if self.flg_hide_res is False:
                self.master.geometry("320x350")
            else:
                self.master.geometry("320x700")

        else:
            for i in range(5):
                self.hislabels_cl[i].grid()
                self.hislabels_play[i].grid()
                self.hislabels_game[i].grid()
            self.flg_hide_his = True
            self.hidebutton_his.configure(text="非表示")
            if self.flg_hide_res is False:
                self.master.geometry("320x440")
            else:
                self.master.geometry("320x780")

    #戦績表示欄の表示、非表示を行う処理
    def hidelabel_res(self):
        if self.flg_hide_res is True:
            for i in range(9):
                self.frames[i].grid_remove()
            self.flg_hide_res = False
            self.hidebutton_res.configure(text="表示")
            if self.flg_hide_his is False:
                self.master.geometry("320x350")
            else:
                self.master.geometry("320x440")
        else:
            for i in range(9):
                self.frames[i].grid()
            self.flg_hide_res = True
            self.hidebutton_res.configure(text="非表示")
            if self.flg_hide_his is False:
                self.master.geometry("320x690")
            else:
                self.master.geometry("320x780")

    #過去5戦の結果を表示させる処理
    def sethistry(self):
        for i in range(4):
            self.hislabels_cl[4-i].configure(text=self.hislabels_cl[4-i-1].cget("text"))
            self.hislabels_play[4-i].configure(text=self.hislabels_play[4-i-1].cget("text"))
            self.hislabels_game[4-i].configure(text=self.hislabels_game[4-i-1].cget("text"))
        self.hislabels_cl[0].configure(text=self.nowlabel_cl.cget("text"))
        self.hislabels_play[0].configure(text=self.nowlabel_play.cget("text"))
        self.hislabels_game[0].configure(text=self.nowlabel_game.cget("text"))
        self.nowlabel_cl.configure(text="クラス：--------")
        self.nowlabel_play.configure(text="　　手番：----")
        self.nowlabel_game.configure(text="　　勝敗：----")

    #過去5戦の結果表示をリセットする処理
    def resethistry(self):
        for i in range(5):
            self.hislabels_cl[i].configure(text="クラス：--------")
            self.hislabels_play[i].configure(text="　　手番：----")
            self.hislabels_game[i].configure(text="　　勝敗：----")
        self.nowlabel_cl.configure(text="クラス：--------")
        self.nowlabel_play.configure(text="　　手番：----")
        self.nowlabel_game.configure(text="　　勝敗：----")

def main():
    root = tk.Tk()
    app = Application(master=root)
    app.mainloop()

if __name__ == "__main__":
    main()
