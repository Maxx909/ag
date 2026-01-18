from math import hypot
from random import randint, choice, randrange
from math import hypot

import pygame
from pygame import *
from pygame import key

init()
window = display.set_mode((800, 800))
clock = time.Clock()

font1 = font.Font(None, 30)

class Food:
    def __init__(self, x, y, radius, color):
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color
        self.rect = Rect(0, 0, self.radius*2, self.radius*2)




    def check_colide(self, x, y , r):
        dx = self.x - x
        dy = self.y - y
        return hypot(dx, dy) <= self.radius + r



eats = []

colors = [
    (1,45,64),
    (45,98,12),
    (28,94,157)
]

for _ in range(300):
    x = randrange(-1200, 1200,randint(50,60))
    y = randrange(-1200,1200, 50)
    s = randint(5,30)
    color = choice(colors)
    eat = Food(x, y, s, color)
    eats.append(eat)



my_player = [0,0,50]
speed = 3
step = 3


running = True
while running:
    for e in event.get():
        if e.type == QUIT:
            running = False

    window.fill((100,100,100))

    scale = max(0.3, min(50 / my_player[2], 1.5))


    for eat in eats:
        sx = int((eat.x - my_player[0])*scale + 400)
        sy = int((eat.y - my_player[1])*scale + 400)

        if eat.check_colide(my_player[0], my_player[1], my_player[2]):
            if eat.radius <= my_player[2]:
                my_player[2] += step
                eats.remove(eat)

        eat.rect.center = (sx, sy)

        draw.circle(window,eat.color,(sx,sy),int(eat.radius * scale))

    draw.circle(window, (55,255,25), (400,400), int(my_player[2] * scale))

    keys = key.get_pressed()
    if keys[K_w]: my_player[1] -= speed
    if keys[K_s]: my_player[1] += speed
    if keys[K_a]: my_player[0] -= speed
    if keys[K_d]: my_player[0] += speed

    text = font1.render(f"Балів: {my_player[2]}", 1, (0,0,0))
    window.blit(text, (20, 40))

    display.update()
    clock.tick(60)
