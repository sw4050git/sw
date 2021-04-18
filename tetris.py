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

    def get_moved_cord(self, direction, center_cord):
        x,y = self.get_cord()
        cx,cy = center_cord[0],center_cord[1]
        if direction == MOVE_LEFT:
            return x-1,y
        elif direction == MOVE_RIGHT:
            return x+1,y
        elif direction == MOVE_DOWN:
            return x,y+1
        elif direction == SPIN_LEFT:
            return int(cy+cx-y),int(cy-cx+x)
        elif direction == SPIN_RIGHT:
            return int(cx-cy+y),int(cx+cy-x)
        else:
            return x,y

class TetrisCanvas(tk.Canvas):
    def __init__(self, master ,field):
        canvas_w = field.get_w() * BLOCK_SIZE
        canvas_h = field.get_h() * BLOCK_SIZE

        super().__init__(master, width=canvas_w, height=canvas_h, bg="white")

        self.pack()

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
        for y in range(field.get_h()):
            for x in range(field.get_w()):
                block = field.get_block(x,y)
                color = block.get_color()

                new_block = new_field.get_block(x,y)
                new_block.set_color(color)

        if mino is not None:
            mino_blocks = mino.get_blocks()
            for mino_block in mino_blocks:

                x,y = mino_block.get_cord()
                color = mino_block.get_color()

                new_field_block = new_field.get_block(x, y)
                new_field_block.set_color(color)

        for y in range(field.get_h()):
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

    def judge_can_move(self, mino, direction):
        no_empty_cord = set(block.get_cord() for block in self.get_blocks() 
                                            if block.get_color() != "gray")

        move_mino_cord = set(block.get_moved_cord(direction,mino.center_cord) for block in mino.get_blocks())

        for x,y in move_mino_cord:
            if x < 0 or x >= self.w or y < 0 or y >= self.h:
                return False

        collision_set = no_empty_cord & move_mino_cord

        if len(collision_set) == 0:
            ret = True
        else:
            ret = False

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

        if mino_type == 1:
            color = "cyan"
            self.center_cord = [FIELD_WIDTH / 2-0.5,0.5]
            cords = [
                [FIELD_WIDTH / 2-2,0],
                [FIELD_WIDTH / 2-1, 0],
                [FIELD_WIDTH / 2, 0],
                [FIELD_WIDTH / 2+1, 0],
            ]

        elif mino_type == 2:
            color = "yellow"
            self.center_cord = [FIELD_WIDTH / 2-0.5,0.5]
            cords = [
                [FIELD_WIDTH / 2,0],
                [FIELD_WIDTH / 2, 1],
                [FIELD_WIDTH / 2-1, 0],
                [FIELD_WIDTH / 2-1, 1],
            ]

        elif mino_type == 3:
            color = "orange"
            self.center_cord = [FIELD_WIDTH / 2,1]
            cords = [
                [FIELD_WIDTH / 2-1,1],
                [FIELD_WIDTH / 2, 1],
                [FIELD_WIDTH / 2+1, 1],
                [FIELD_WIDTH / 2+1, 0],
            ]

        elif mino_type == 4:
            color = "blue"
            self.center_cord = [FIELD_WIDTH / 2,1]
            cords = [
                [FIELD_WIDTH / 2-1,1],
                [FIELD_WIDTH / 2, 1],
                [FIELD_WIDTH / 2+1, 1],
                [FIELD_WIDTH / 2-1, 0],
            ]
        
        elif mino_type == 5:
            color = "green"
            self.center_cord = [FIELD_WIDTH / 2,1]
            cords = [
                [FIELD_WIDTH / 2, 0],
                [FIELD_WIDTH / 2, 1],
                [FIELD_WIDTH / 2+1, 0],
                [FIELD_WIDTH / 2-1, 1],
            ]
        
        elif mino_type == 6:
            color = "red"
            self.center_cord = [FIELD_WIDTH / 2,1]
            cords = [
                [FIELD_WIDTH / 2, 0],
                [FIELD_WIDTH / 2, 1],
                [FIELD_WIDTH / 2+1, 1],
                [FIELD_WIDTH / 2-1, 0],
            ]

        elif mino_type == 7:
            color = "magenta"
            self.center_cord = [FIELD_WIDTH / 2,1]
            cords = [
                [FIELD_WIDTH / 2, 0],
                [FIELD_WIDTH / 2, 1],
                [FIELD_WIDTH / 2+1, 1],
                [FIELD_WIDTH / 2-1, 1],
            ]

        for cord in cords:
            self.blocks.append(TetrisBlock(cord[0],cord[1],color))

    def get_blocks(self):
        return self.blocks
    
    def move(self, direction):
        cx,cy = self.center_cord
        for block in self.blocks:
            x,y = block.get_moved_cord(direction, self.center_cord)
            block.set_cord(x,y)
        if direction == MOVE_LEFT:
            self.center_cord = [cx-1,cy] 
        elif direction == MOVE_RIGHT:
            self.center_cord = [cx+1,cy] 
        elif direction == MOVE_DOWN:
            self.center_cord = [cx,cy+1]


class TetrisGame():
    
    def __init__(self,master):
        self.field = TetrisField()
        self.next_mino_container = []
        self.mino_container = []
        self.mino = None
        self.canvas = TetrisCanvas(master, self.field)
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
        if self.field.judge_game_over(self.mino):
            self.end_func()
            print("GAMEOVER")
        self.canvas.update(self.field, self.mino)

    def move_block(self, direction):
        if self.field.judge_can_move(self.mino, direction):
            self.mino.move(direction)
            self.canvas.update(self.field, self.mino)
        else:
            if direction == MOVE_DOWN:
                self.field.fix_mino(self.mino)
                self.field.delete_line()
                self.new_mino()

    def create_mino_container(self):
        container = [1,2,3,4,5,6,7]
        if len(self.next_mino_container) == 0:
            self.next_mino_container = random.sample(container,7)
        self.mino_container = self.next_mino_container
        self.next_mino_container = random.sample(container,7)


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

    def end_event(self):
        self.running = False

        self.timer_end()

        self.master.unbind("<KeyPress-a>")
        self.master.unbind("<KeyPress-d>")
        self.master.unbind("<KeyPress-s>")
        self.master.unbind("<KeyPress-f>")
        self.master.unbind("<KeyPress-r>")

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

    def leftspin_key_event(self, event):
        self.game.move_block(SPIN_LEFT)

    def rightspin_key_event(self, event):
        self.game.move_block(SPIN_RIGHT)
    
    def timer_event(self):
        self.down_key_event(None)

class Application(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.master.geometry("400x600")
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