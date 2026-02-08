from math import hypot
from socket import socket, AF_INET, SOCK_STREAM
from pygame import *
from threading import Thread
from random import randint
from menu import ConnectWindow

win = ConnectWindow()
win.mainloop()

nickname = win.name
host = win.host
port = win.port



sock = socket(AF_INET, SOCK_STREAM)
sock.connect((host, port))
pacets = sock.recv(64).decode().strip().split('|')
pacet = pacets[0]
print(pacet)
my_data = list(
    map(
        int,
        pacet.split(',')
    )
)

my_id = my_data[0]
my_player = my_data[1:]
sock.setblocking(False)

init()
window = display.set_mode((1000, 1000))
clock = time.Clock()
f = font.Font(None, 50)
all_players = []
running = True
lose = False


def read_packet(packet):
    #0,0,1,20,nickname
    parts = packet.split(',')
    id , x,y,radius = map(int,parts[:4])
    nickname = parts[4]
    return [id,x,y,radius,nickname]

def receive_data():
   global all_players, running, lose
   while running:
       try:
           data = sock.recv(4096).decode().strip()
           if data == "LOSE":
               lose = True
           elif data:
               parts = data.strip('|').split('|')
               all_players = [read_packet(p) for p in parts if len(p.split(',')) == 5]
       except:
           pass


Thread(target=receive_data, daemon=True).start()


class Eat:
   def __init__(self, x, y, r, c):
       self.x = x
       self.y = y
       self.radius = r
       self.color = c

   def check_collision(self, player_x, player_y, player_r):
       dx = self.x - player_x
       dy = self.y - player_y
       return hypot(dx, dy) <= self.radius + player_r


eats = [Eat(randint(-2000, 2000), randint(-2000, 2000), 10,
           (randint(0, 255), randint(0, 255), randint(0, 255)))
       for _ in range(300)]
name_font = font.Font(None, 20)

while running:
   for e in event.get():
       if e.type == QUIT:
           running = False

   window.fill((255, 255, 255))
   scale = max(0.3, min(50 / my_player[2], 1.5))

   for p in all_players:
       if p[0] == my_id: continue
       sx = int((p[1] - my_player[0]) * scale + 500)
       sy = int((p[2] - my_player[1]) * scale + 500)
       draw.circle(window, (255, 0, 0), (sx, sy), int(p[3] * scale))
       name_text = name_font.render(f"{p[4]}",1,(0,0,0))
       window.blit(name_text, (sx, sy))
   draw.circle(window, (0, 255, 0), (500, 500), int(my_player[2] * scale))

   to_remove = []
   for eat in eats:
       if eat.check_collision(my_player[0], my_player[1], my_player[2]):
           to_remove.append(eat)
           my_player[2] += int(eat.radius * 0.2)
       else:
           sx = int((eat.x - my_player[0]) * scale + 500)
           sy = int((eat.y - my_player[1]) * scale + 500)
           draw.circle(window, eat.color, (sx, sy), int(eat.radius * scale))

   for eat in to_remove:
       eats.remove(eat)

   if lose:
       t = f.render('U lose!', 1, (244, 0, 0))
       window.blit(t, (400, 500))

   display.update()
   clock.tick(60)

   if not lose:
       keys = key.get_pressed()
       if keys[K_w]: my_player[1] -= 10
       if keys[K_s]: my_player[1] += 10
       if keys[K_a]: my_player[0] -= 10
       if keys[K_d]: my_player[0] += 10

       try:
           msg = f"{my_id},{my_player[0]},{my_player[1]},{my_player[2]},{nickname}"
           sock.send(msg.encode())
       except:
           pass

quit()