import tkinter as tk
from tkinter import ttk
import random

BLOCK_SIZE = 25  # ミノの縦横サイズpx
FIELD_WIDTH = 10  # フィールドの幅
FIELD_HEIGHT = 20  # フィールドの高さ

MOVE_LEFT = 0  # 左にミノを移動
MOVE_RIGHT = 1  # 右にミノを移動
MOVE_DOWN = 2  # 下にミノを移動
SPIN_LEFT = 3  # ミノを左回転
SPIN_RIGHT = 4 # ミノを右回転

class TetrisBlock():
    def __init__(self, x=0, y=0, color="gray"):
        self.x=x
        self.y=y
        self.color = color
    
    def set_cord(self, x, y):
        self.x=x
        self.y=y

    def get_cord(self):
      return int(self.x),int(self.y)
    
    def set_color(self, color):
        self.color = color
    
    def get_color(self):
        return self.color

    def get_moved_cord(self, direction, mino, count):
        mino_type = mino.mino_type
        x,y = self.get_cord()
        cx,cy = mino.center_cord[0],mino.center_cord[1]
        if direction == MOVE_LEFT:
            return x-1,y
        elif direction == MOVE_RIGHT:
            return x+1,y
        elif direction == MOVE_DOWN:
            return x,y+1
        elif direction == SPIN_LEFT or direction == SPIN_RIGHT:
            return self.get_span_cord(direction, mino, count)
        else:
            return x,y

    def get_span_cord(self, direction, mino, count):
        mino_type = mino.mino_type
        spin_amount = mino.spin_amount
        cx,cy = mino.center_cord[0],mino.center_cord[1]
        x,y = self.get_cord()
        if direction ==SPIN_LEFT:
            x,y = int(cy+cx-y),int(cy-cx+x)
        elif direction ==SPIN_RIGHT:
            x,y = int(cx-cy+y),int(cx+cy-x)
        if count == 0:
            return x, y
        elif count < 3:
            if spin_amount == 0:
                x -= 1
            elif spin_amount == 180:
                x += 1
            else:
                if direction ==SPIN_LEFT:
                    x += 1
                elif direction == SPIN_RIGHT:
                    x -= 1
            if count ==2:
                if spin_amount == 0 or spin_amount == 180:
                    y += 1
                else:
                    y -= 1
            return x,y
        else:
            if spin_amount == 0 or spin_amount == 180:
                y += 2
            else:
                y -=2
            if count ==4:
                if spin_amount == 0:
                    x -= 1
                elif spin_amount == 180:
                    x += 1
                else:
                    if direction ==SPIN_LEFT:
                        x += 1
                    elif direction == SPIN_RIGHT:
                        x -= 1
            return x,y

class TetrisCanvas(tk.Canvas):
    def __init__(self, master ,field):
        canvas_w = field.get_w() * BLOCK_SIZE
        canvas_h = field.get_h() * BLOCK_SIZE

        super().__init__(master, width=canvas_w, height=canvas_h, bg="white")

        self.grid(column=2,row=0 , rowspan=20)

        for y in range(field.get_h()):
            for x in range(field.get_w()):
                block = field.get_block(x,y)
                x1 = x*BLOCK_SIZE
                x2 = (x+1)*BLOCK_SIZE
                y1 = y*BLOCK_SIZE
                y2 = (y+1)*BLOCK_SIZE
                self.create_rectangle(x1,y1,x2,y2,outline="white",width=1,fill=block.get_color())

        self.before_field = field

    def update(self,field, mino):
        new_field = TetrisField()

        for y in range(field.get_h()): #前のフィールドの情報を取得し、新フィールドに適用
            for x in range(field.get_w()):
                block = field.get_block(x,y)
                color = block.get_color()

                new_block = new_field.get_block(x,y)
                new_block.set_color(color)

        if mino is not None: #操作中ミノの情報を取得し、新フィールドに適用
            mino_blocks = mino.get_blocks()
            for mino_block in mino_blocks:

                x,y = mino_block.get_cord()
                color = mino_block.get_color()

                new_field_block = new_field.get_block(x, y)
                new_field_block.set_color(color)

        for y in range(field.get_h()): #全フィールドと新フィールドの差分を描画しなおす
            for x in range(field.get_w()):
                new_block = new_field.get_block(x,y)
                new_color = new_block.get_color()

                before_block = self.before_field.get_block(x, y)
                before_color = before_block.get_color()
                if(new_color == before_color):
                    continue

                x1 = x * BLOCK_SIZE
                x2 = (x + 1) * BLOCK_SIZE
                y1 = y * BLOCK_SIZE
                y2 = (y + 1) * BLOCK_SIZE
                # フィールドの各位置の色で長方形描画
                self.create_rectangle(x1, y1, x2, y2,outline="white", width=1, fill=new_color)

        self.before_field = new_field

class NextMinoCanvas(tk.Canvas):
    def __init__(self,master,num):
        canvas_w = 5 * BLOCK_SIZE 
        canvas_h = 4 * BLOCK_SIZE

        super().__init__(master, width=canvas_w, height=canvas_h, bg="gray95")

        self.grid(column=3,row=num,sticky=tk.N)

        for y in range(4):
            for x in range(5):
                x1 = x*BLOCK_SIZE
                x2 = (x+1)*BLOCK_SIZE
                y1 = y*BLOCK_SIZE
                y2 = (y+1)*BLOCK_SIZE
                self.create_rectangle(x1,y1,x2,y2,outline="gray95",width=1,fill="gray95")

    def update(self,mino):

        mino_cords = []
        if mino is not None:
            mino_blocks = mino.get_blocks()
            for mino_block in mino_blocks:

                x,y = mino_block.get_cord()
                mino_cords.append((x-FIELD_WIDTH/2+2,y+1))
                color = mino_block.get_color()

        for y in range(4):
            for x in range(5):

                l = (x,y)
                x1 = x * BLOCK_SIZE
                x2 = (x + 1) * BLOCK_SIZE
                y1 = y * BLOCK_SIZE
                y2 = (y + 1) * BLOCK_SIZE
                # フィールドの各位置の色で長方形描画
                if l in mino_cords:
                    self.create_rectangle(x1, y1, x2, y2,outline="white", width=1, fill=color)
                else:
                    self.create_rectangle(x1, y1, x2, y2,outline="gray95", width=1, fill="gray95")

class HoldMinoCanvas(tk.Canvas):
    def __init__(self,master):
        self.holding_mino = None
        canvas_w = 5 * BLOCK_SIZE 
        canvas_h = 4 * BLOCK_SIZE
        
        super().__init__(master, width=canvas_w, height=canvas_h, bg="gray95")

        self.grid(column=1,row=0,sticky=tk.N)

        for y in range(4):
            for x in range(5):
                x1 = x*BLOCK_SIZE
                x2 = (x+1)*BLOCK_SIZE
                y1 = y*BLOCK_SIZE
                y2 = (y+1)*BLOCK_SIZE
                self.create_rectangle(x1,y1,x2,y2,outline="gray95",width=1,fill="gray95")

    def get_holding_mino(self):
        return self.holding_mino

    def update(self,mino):
        self.holding_mino = mino
        mino_cords = []
        if mino is not None:
            mino_blocks = mino.get_blocks()
            for mino_block in mino_blocks:
                color = mino_block.get_color()
            for cords in mino.cords:
                x,y = cords
                mino_cords.append((x-FIELD_WIDTH/2+2,y+1))


        for y in range(4):
            for x in range(5):

                l = (x,y)
                x1 = x * BLOCK_SIZE
                x2 = (x + 1) * BLOCK_SIZE
                y1 = y * BLOCK_SIZE
                y2 = (y + 1) * BLOCK_SIZE
                # フィールドの各位置の色で長方形描画
                if l in mino_cords:
                    self.create_rectangle(x1, y1, x2, y2,outline="white", width=1, fill=color)
                else:
                    self.create_rectangle(x1, y1, x2, y2,outline="gray95", width=1, fill="gray95")

class TetrisField():
    def __init__(self):
        self.w = FIELD_WIDTH
        self.h = FIELD_HEIGHT

        self.blocks = []
        for y in range(self.h):
            for x in range(self.w):
                self.blocks.append(TetrisBlock(x,y,"gray"))

    def get_w(self):
        return self.w

    def get_h(self):
        return self.h

    def get_blocks(self):
        return self.blocks

    def get_block(self,x,y):
        return self.blocks[y*self.w + x]

    def judge_game_over(self, mino):
        no_empty_cord = set(block.get_cord() for block in self.get_blocks() 
                                            if block.get_color() != "gray")

        mino_cord = set(block.get_cord() for block in mino.get_blocks())

        collision_set = no_empty_cord & mino_cord

        if len(collision_set) == 0:
            ret = False
        else:
            ret = True

        return ret

    def judge_can_move(self, mino, direction , count):
        no_empty_cord = set(block.get_cord() for block in self.get_blocks() 
                                            if block.get_color() != "gray")

        moved_mino_cords = []
        for block in mino.get_blocks():
            moved_mino_cords.append(block.get_moved_cord(direction, mino, count))

        moved_mino_cords_set = set(moved_mino_cords)

        for x,y in moved_mino_cords:
            if x < 0 or x >= self.w or y < 0 or y >= self.h :
                if count > 4:
                    return None
                return self.judge_can_move(mino, direction, count+1)

        collision_set = no_empty_cord & moved_mino_cords_set

        if len(collision_set) == 0:
            ret = moved_mino_cords
        else:
            if (direction == SPIN_LEFT or direction == SPIN_RIGHT) and (count <= 4):
                ret = self.judge_can_move(mino, direction, count+1)
            else:
                ret = None

        return ret

    def fix_mino(self,mino):
        for block in mino.get_blocks():
            x, y = block.get_cord()
            color = block.get_color()

            field_block = self.get_block(x,y)
            field_block.set_color(color)

    def delete_line(self):
        for y in range(self.h):
            for x in range(self.w):
                block = self.get_block(x, y)
                if(block.get_color() == "gray"):
                    break
            else:
                for down_y in range(y, 0, -1):
                    for x in range(self.w):
                        src_block = self.get_block(x, down_y-1)
                        dst_block = self.get_block(x, down_y)
                        dst_block.set_color(src_block.get_color())

                for x in range(self.w):
                    block = self.get_block(x, 0)
                    block.set_color("gray")

class TetrisMino():
    def __init__(self, mino_type):
        self.blocks = []
        self.center_cord = []
        self.cords = []
        self.mino_type = mino_type
        self.spin_amount = 0

        if mino_type == 1:
            color = "cyan"
            self.center_cord = [FIELD_WIDTH / 2+0.5,0.5]
            self.cords = [
                [FIELD_WIDTH / 2-1,0],
                [FIELD_WIDTH / 2, 0],
                [FIELD_WIDTH / 2+1, 0],
                [FIELD_WIDTH / 2+2, 0],
            ]

        elif mino_type == 2:
            color = "yellow"
            self.center_cord = [FIELD_WIDTH / 2-0.5,0.5]
            self.cords = [
                [FIELD_WIDTH / 2,0],
                [FIELD_WIDTH / 2, 1],
                [FIELD_WIDTH / 2-1, 0],
                [FIELD_WIDTH / 2-1, 1],
            ]

        elif mino_type == 3:
            color = "orange"
            self.center_cord = [FIELD_WIDTH / 2,1]
            self.cords = [
                [FIELD_WIDTH / 2-1,1],
                [FIELD_WIDTH / 2, 1],
                [FIELD_WIDTH / 2+1, 1],
                [FIELD_WIDTH / 2+1, 0],
            ]

        elif mino_type == 4:
            color = "blue"
            self.center_cord = [FIELD_WIDTH / 2,1]
            self.cords = [
                [FIELD_WIDTH / 2-1,1],
                [FIELD_WIDTH / 2, 1],
                [FIELD_WIDTH / 2+1, 1],
                [FIELD_WIDTH / 2-1, 0],
            ]
        
        elif mino_type == 5:
            color = "green"
            self.center_cord = [FIELD_WIDTH / 2,1]
            self.cords = [
                [FIELD_WIDTH / 2, 0],
                [FIELD_WIDTH / 2, 1],
                [FIELD_WIDTH / 2+1, 0],
                [FIELD_WIDTH / 2-1, 1],
            ]
        
        elif mino_type == 6:
            color = "red"
            self.center_cord = [FIELD_WIDTH / 2,1]
            self.cords = [
                [FIELD_WIDTH / 2, 0],
                [FIELD_WIDTH / 2, 1],
                [FIELD_WIDTH / 2+1, 1],
                [FIELD_WIDTH / 2-1, 0],
            ]

        elif mino_type == 7:
            color = "magenta"
            self.center_cord = [FIELD_WIDTH / 2,1]
            self.cords = [
                [FIELD_WIDTH / 2, 0],
                [FIELD_WIDTH / 2, 1],
                [FIELD_WIDTH / 2+1, 1],
                [FIELD_WIDTH / 2-1, 1],
            ]

        for cord in self.cords:
            self.blocks.append(TetrisBlock(cord[0],cord[1],color))

    def get_blocks(self):
        return self.blocks

    def get_mino_type(self):
        return self.mino_type
    
    def change_spin_amount(self, direction):
        if direction == SPIN_LEFT:
            if self.spin_amount < 360:
                self.spin_amount += 90
            else:
                self.spin_amount = 0
        elif direction == SPIN_RIGHT:
            if self.spin_amount <=0:
                self.spin_amount = 270
            else:
                self.spin_amount -= 90

    def move(self, direction, moved_cords):
        self.change_spin_amount(direction)
        for block in self.blocks:
            x,y = moved_cords.pop(0)
            block.set_cord(x,y)
        self.update_center_cord()

    def update_center_cord(self):
        if self.mino_type == 1:
            tx,ty = 0,0
            for block in self.blocks:
                x,y = block.get_cord()
                tx += x
                ty += y
            if self.spin_amount == 0:
                self.center_cord = tx/4,ty/4+0.5
            elif self.spin_amount == 90:
                self.center_cord = tx/4-0.5,ty/4
            elif self.spin_amount == 180:
                self.center_cord = tx/4,ty/4-0.5
            else:
                self.center_cord = tx/4+0.5,ty/4
        elif self.mino_type == 2:
            tx,ty = 0,0
            for block in self.blocks:
                x,y = block.get_cord()
                tx += x
                ty += y
            self.center_cord = tx/4,ty/4
        else:
            self.center_cord = self.blocks[1].get_cord()

class TetrisGame():
    
    def __init__(self,master):
        self.field = TetrisField()
        self.mino_container = []
        self.second_mino_container = []
        self.mino = None
        self.next_mino = None
        self.next_next_mino = None
        self.able_hold = True
        self.canvas = TetrisCanvas(master, self.field)
        self.next_mino_canvas = NextMinoCanvas(master,0)
        self.next_next_mino_canvas = NextMinoCanvas(master,1)
        self.hold_mino_canvas = HoldMinoCanvas(master)
        self.canvas.update(self.field, self.mino)
        self.create_mino_container()

    def start(self, func):
        self.end_func = func
        self.field = TetrisField()
        self.new_mino()

    def new_mino(self):
        if len(self.mino_container) == 0:
            self.create_mino_container()
        self.mino = TetrisMino(self.mino_container.pop(0))
        self.set_next_mino()
        if self.field.judge_game_over(self.mino):
            self.end_func()
            print("GAMEOVER")
        self.canvas.update(self.field, self.mino)
        self.next_mino_canvas.update(self.next_mino)
        self.next_next_mino_canvas.update(self.next_next_mino)

    def hold_mino(self):
        if self.able_hold is True:
            self.able_hold = False
            if self.hold_mino_canvas.get_holding_mino() is None:
                self.hold_mino_canvas.update(self.mino)
                self.new_mino()
            else:
                new_mino = self.hold_mino_canvas.get_holding_mino()
                self.hold_mino_canvas.update(self.mino)
                self.mino = TetrisMino(new_mino.mino_type)
                self.canvas.update(self.field, self.mino)

    def set_next_mino(self):
        if len(self.mino_container) == 0:
            self.next_mino = TetrisMino(self.second_mino_container[0])
            self.next_next_mino = TetrisMino(self.second_mino_container[1])
        elif len(self.mino_container) == 1:
            self.next_mino = TetrisMino(self.mino_container[0])
            self.next_next_mino = TetrisMino(self.second_mino_container[0])
        else:
            self.next_mino = TetrisMino(self.mino_container[0])
            self.next_next_mino = TetrisMino(self.mino_container[1])

    def move_block(self, direction):
        moved_cords = self.field.judge_can_move(self.mino, direction, 0)
        if moved_cords is not None:
            self.mino.move(direction, moved_cords)
            self.canvas.update(self.field, self.mino)
        else:
            if direction == MOVE_DOWN:
                self.field.fix_mino(self.mino)
                self.field.delete_line()
                self.able_hold = True
                self.new_mino()
                return False
        return True

    def create_mino_container(self):
        container = [1,2,3,4,5,6,7]
        if len(self.second_mino_container) == 0:
            self.second_mino_container = random.sample(container,7)
        self.mino_container = self.second_mino_container
        self.second_mino_container = random.sample(container,7)

class EventHandller():
    def __init__(self, master, game):
        self.master = master
        self.game = game
        self.timer = None

        button = tk.Button(master, text= 'START',command=self.start_event)
        button.pack()
    
    def start_event(self):
        self.game.start(self.end_event)
        self.running = True

        self.timer_start()

        self.master.bind("<KeyPress-a>", self.left_key_event)
        self.master.bind("<KeyPress-d>", self.right_key_event)
        self.master.bind("<KeyPress-s>", self.down_key_event)
        self.master.bind("<KeyPress-f>", self.leftspin_key_event)
        self.master.bind("<KeyPress-r>", self.rightspin_key_event)
        self.master.bind("<KeyPress-e>", self.hold_key_event)
        self.master.bind("<KeyPress-w>", self.harddrop_key_event)

    def end_event(self):
        self.running = False

        self.timer_end()

        self.master.unbind("<KeyPress-a>")
        self.master.unbind("<KeyPress-d>")
        self.master.unbind("<KeyPress-s>")
        self.master.unbind("<KeyPress-f>")
        self.master.unbind("<KeyPress-r>")
        self.master.unbind("<KeyPress-e>")

    def timer_end(self):

        if self.timer is not None:
            self.master.after_cancel(self.timer)
            self.timer = None

    def timer_start(self):

        if self.timer is not None:
            self.master.after_cancel(self.timer)

        if self.running:
            self.timer = self.master.after(1000, self.timer_event)

    def left_key_event(self, event):
        self.game.move_block(MOVE_LEFT)

    def right_key_event(self, event):
        self.game.move_block(MOVE_RIGHT)

    def down_key_event(self, event):
        self.game.move_block(MOVE_DOWN)
        self.timer_start()

    def harddrop_key_event(self, event):
        a = True
        while a is True:
            a = self.game.move_block(MOVE_DOWN)
        self.timer_start()

    def leftspin_key_event(self, event):
        self.game.move_block(SPIN_LEFT)

    def rightspin_key_event(self, event):
        self.game.move_block(SPIN_RIGHT)

    def hold_key_event(self, event):
        self.game.hold_mino()
    
    def timer_event(self):
        self.down_key_event(None)

class Application(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.master.geometry("600x600")
        self.master.title("テトリス")
        game = TetrisGame(self)
        EventHandller(self.master, game)
        self.pack()

def main():
    root = tk.Tk()
    app = Application(master=root)
    app.mainloop()

if __name__ == "__main__":
    main()
