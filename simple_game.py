"""
Simple Catch-the-Balls game using tkinter.

Controls:
- Left arrow: move paddle left
- Right arrow: move paddle right

Objective: catch falling balls with the paddle. Each catch gives +1 score.
You have 3 lives; missing a ball removes a life. Game over when lives reach 0.

Run: python /workspace/simple_game.py
No external packages required.
"""

import tkinter as tk
import random

WIDTH = 500
HEIGHT = 400
PADDLE_WIDTH = 100
PADDLE_HEIGHT = 12
BALL_RADIUS = 12
BALL_FALL_SPEED = 4  # pixels per frame
SPAWN_INTERVAL = 1200  # milliseconds between new balls
UPDATE_DELAY = 20  # ms per frame (~50 FPS)


class Ball:
    def __init__(self, canvas, x, y, r, color="red"):
        self.canvas = canvas
        self.r = r
        self.id = canvas.create_oval(x - r, y - r, x + r, y + r, fill=color, outline="")

    def move(self, dx, dy):
        self.canvas.move(self.id, dx, dy)

    def pos(self):
        coords = self.canvas.coords(self.id)
        # coords = [x1,y1,x2,y2]
        x = (coords[0] + coords[2]) / 2
        y = (coords[1] + coords[3]) / 2
        return x, y

    def remove(self):
        self.canvas.delete(self.id)


class Game:
    def __init__(self, root):
        self.root = root
        root.title("Simple Catch Game")
        self.canvas = tk.Canvas(root, width=WIDTH, height=HEIGHT, bg="#f0f0f0")
        self.canvas.pack()

        # paddle
        self.paddle_x = WIDTH / 2
        self.paddle = self.canvas.create_rectangle(
            self.paddle_x - PADDLE_WIDTH / 2,
            HEIGHT - 30 - PADDLE_HEIGHT,
            self.paddle_x + PADDLE_WIDTH / 2,
            HEIGHT - 30,
            fill="#333333",
        )

        # stats
        self.score = 0
        self.lives = 3
        self.score_text = self.canvas.create_text(10, 10, anchor="nw", text=f"Score: {self.score}", font=(None, 14))
        self.lives_text = self.canvas.create_text(WIDTH - 10, 10, anchor="ne", text=f"Lives: {self.lives}", font=(None, 14))

        # control
        self.move_left = False
        self.move_right = False
        root.bind("<KeyPress-Left>", lambda e: self.set_move(-1))
        root.bind("<KeyRelease-Left>", lambda e: self.set_move(0))
        root.bind("<KeyPress-Right>", lambda e: self.set_move(1))
        root.bind("<KeyRelease-Right>", lambda e: self.set_move(0))

        self.balls = []
        self.game_over = False

        # start loops
        self.root.after(SPAWN_INTERVAL, self.spawn_ball)
        self.update()

    def set_move(self, dir):
        # dir: -1 left, 0 stop, 1 right; prefer simple overwrite so last key wins
        if dir == -1:
            self.move_left = True
            self.move_right = False
        elif dir == 1:
            self.move_right = True
            self.move_left = False
        else:
            # stop both
            self.move_left = False
            self.move_right = False

    def spawn_ball(self):
        if self.game_over:
            return
        x = random.randint(BALL_RADIUS, WIDTH - BALL_RADIUS)
        ball = Ball(self.canvas, x, -BALL_RADIUS, BALL_RADIUS)
        self.balls.append(ball)
        self.root.after(SPAWN_INTERVAL, self.spawn_ball)

    def update(self):
        if self.game_over:
            return

        # move paddle
        dx = 0
        speed = 8
        if self.move_left:
            dx = -speed
        elif self.move_right:
            dx = speed
        if dx != 0:
            self.canvas.move(self.paddle, dx, 0)
            self.paddle_x += dx
            # clamp
            left = self.paddle_x - PADDLE_WIDTH / 2
            right = self.paddle_x + PADDLE_WIDTH / 2
            if left < 0:
                shift = -left
                self.canvas.move(self.paddle, shift, 0)
                self.paddle_x += shift
            if right > WIDTH:
                shift = WIDTH - right
                self.canvas.move(self.paddle, shift, 0)
                self.paddle_x += shift

        # move balls
        to_remove = []
        for ball in list(self.balls):
            ball.move(0, BALL_FALL_SPEED)
            x, y = ball.pos()
            # check collision with paddle
            if y + ball.r >= HEIGHT - 30 - PADDLE_HEIGHT:  # near paddle y
                # determine paddle bounds
                paddle_coords = self.canvas.coords(self.paddle)
                px1, py1, px2, py2 = paddle_coords
                if px1 <= x <= px2:
                    # caught
                    self.score += 1
                    self.canvas.itemconfigure(self.score_text, text=f"Score: {self.score}")
                    ball.remove()
                    self.balls.remove(ball)
                    continue
            # if it goes past bottom
            if y - ball.r > HEIGHT:
                # missed
                self.lives -= 1
                self.canvas.itemconfigure(self.lives_text, text=f"Lives: {self.lives}")
                ball.remove()
                self.balls.remove(ball)
                if self.lives <= 0:
                    self.end_game()
                continue

        # schedule next frame
        if not self.game_over:
            self.root.after(UPDATE_DELAY, self.update)

    def end_game(self):
        self.game_over = True
        self.canvas.create_text(
            WIDTH / 2,
            HEIGHT / 2,
            text=f"Game Over\nScore: {self.score}",
            font=(None, 24),
            fill="#aa0000",
            justify="center",
        )
        # instruction to restart
        self.canvas.create_text(
            WIDTH / 2,
            HEIGHT / 2 + 60,
            text="Press R to play again",
            font=(None, 12),
            fill="#333333",
        )
        self.root.bind("r", lambda e: self.restart())

    def restart(self):
        # clear canvas and reset
        self.canvas.delete("all")
        self.paddle_x = WIDTH / 2
        self.paddle = self.canvas.create_rectangle(
            self.paddle_x - PADDLE_WIDTH / 2,
            HEIGHT - 30 - PADDLE_HEIGHT,
            self.paddle_x + PADDLE_WIDTH / 2,
            HEIGHT - 30,
            fill="#333333",
        )
        self.score = 0
        self.lives = 3
        self.score_text = self.canvas.create_text(10, 10, anchor="nw", text=f"Score: {self.score}", font=(None, 14))
        self.lives_text = self.canvas.create_text(WIDTH - 10, 10, anchor="ne", text=f"Lives: {self.lives}", font=(None, 14))
        self.balls = []
        self.game_over = False
        self.root.after(SPAWN_INTERVAL, self.spawn_ball)
        self.update()


def main():
    root = tk.Tk()
    game = Game(root)
    root.mainloop()


if __name__ == "__main__":
    main()
