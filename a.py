import pygame
from pygame import *
from threading import Thread
from random import randint
from math import hypot
from socket import socket, AF_INET, SOCK_STREAM

# Припускаємо, що menu.py існує у вашій папці
try:
    from menu import ConnectWindow

    win = ConnectWindow()
    win.mainloop()
    nickname = win.name
    host = win.host
    port = win.port
except ImportError:
    # Дефолтні налаштування для тестування, якщо немає menu.py
    nickname = "Player"
    host = "127.0.0.1"
    port = 5000

# Підключення до сервера
sock = socket(AF_INET, SOCK_STREAM)
try:
    sock.connect((host, port))
    pacets = sock.recv(64).decode().strip().split('|')
    pacet = pacets[0]
    my_data = list(map(int, pacet.split(',')))
    my_id = my_data[0]
    my_player = my_data[1:]  # [x, y, radius]
    sock.setblocking(False)
except Exception as e:
    print(f"Помилка підключення: {e}")
    exit()

init()
WIDTH, HEIGHT = 1000, 1000
window = display.set_mode((WIDTH, HEIGHT))
clock = time.Clock()
f = font.Font(None, 50)
name_font = font.Font(None, 20)

all_players = []
running = True
lose = False


def read_packet(packet):
    # Формат: id, x, y, radius, nickname
    parts = packet.split(',')
    if len(parts) >= 5:
        return [int(parts[0]), int(parts[1]), int(parts[2]), int(parts[3]), parts[4]]
    return None


def receive_data():
    global all_players, running, lose
    while running:
        try:
            data = sock.recv(4096).decode().strip()
            if "LOSE" in data:
                lose = True
            elif data:
                parts = data.strip('|').split('|')
                new_players = []
                for p in parts:
                    parsed = read_packet(p)
                    if parsed: new_players.append(parsed)
                all_players = new_players
        except:
            pass


def draw_minimap(window, players, eats, map_size, minimap_size):
    # 1. Налаштування позиції міні-карти
    mx = 10  # Відступ зліва
    my = 10  # Відступ зверху
    scale = minimap_size / map_size
    offset = map_size // 2  # Якщо карта від -2000 до 2000, то зміщення 2000

    # 2. Малюємо рамку та фон міні-карти
    minimap_rect = pygame.Rect(mx, my, minimap_size, minimap_size)
    pygame.draw.rect(window, (50, 50, 50), minimap_rect)  # Темний фон
    pygame.draw.rect(window, (255, 255, 255), minimap_rect, 1)  # Біла рамка

    # 3. Малюємо їжу (дуже маленькі крапки)
    for eat in eats:
        ex = mx + int((eat.x + offset) * scale)
        ey = my + int((eat.y + offset) * scale)
        # Малюємо тільки якщо крапка потрапляє в межі міні-карти
        if minimap_rect.collidepoint(ex, ey):
            pygame.draw.circle(window, eat.color, (ex, ey), 1)

    # 4. Малюємо інших гравців (червоні крапки)
    for p in players:
        if p[0] == my_id: continue  # Пропускаємо себе в списку, бо намалюємо окремо
        px = mx + int((p[1] + offset) * scale)
        py = my + int((p[2] + offset) * scale)
        if minimap_rect.collidepoint(px, py):
            pygame.draw.circle(window, (255, 0, 0), (px, py), 2)

    # 5. МАЛЮЄМО СЕБЕ (Яскраво-зелена крапка)
    # Використовуємо локальні координати my_player, щоб не було затримок
    my_x = mx + int((my_player[0] + offset) * scale)
    my_y = my + int((my_player[1] + offset) * scale)

    # Перевіряємо, чи ми в межах карти, і малюємо більшу зелену крапку
    if minimap_rect.collidepoint(my_x, my_y):
        pygame.draw.circle(window, (0, 255, 0), (my_x, my_y), 4)


class Eat:
    def __init__(self, x, y, r, c):
        self.x = x
        self.y = y
        self.radius = r
        self.color = c

    def check_collision(self, player_x, player_y, player_r):
        return hypot(self.x - player_x, self.y - player_y) <= player_r


# Створення їжі (діапазон -2000...2000, отже розмір карти 4000)
eats = [Eat(randint(-2000, 2000), randint(-2000, 2000), 10,
            (randint(0, 255), randint(0, 255), randint(0, 255)))
        for _ in range(300)]

Thread(target=receive_data, daemon=True).start()

while running:
    for e in event.get():
        if e.type == QUIT:
            running = False

    window.fill((240, 240, 240))  # Світло-сірий фон

    # Масштабування камери
    scale = max(0.3, min(50 / my_player[2], 1.5))

    # Відображення інших гравців
    for p in all_players:
        if p[0] == my_id:
            # Оновлюємо радіус нашого гравця з даних сервера (якщо потрібно)
            my_player[2] = p[3]
            continue

        sx = int((p[1] - my_player[0]) * scale + 500)
        sy = int((p[2] - my_player[1]) * scale + 500)

        draw.circle(window, (255, 0, 0), (sx, sy), int(p[3] * scale))
        name_text = name_font.render(f"{p[4]}", 1, (0, 0, 0))
        window.blit(name_text, (sx, sy))

    # Малюємо нашого гравця в центрі
    draw.circle(window, (0, 255, 0), (500, 500), int(my_player[2] * scale))

    # Робота з їжею
    to_remove = []
    for eat in eats:
        if eat.check_collision(my_player[0], my_player[1], my_player[2]):
            to_remove.append(eat)
            my_player[2] += 1  # Збільшуємо радіус
        else:
            sx = int((eat.x - my_player[0]) * scale + 500)
            sy = int((eat.y - my_player[1]) * scale + 500)
            # Малюємо їжу тільки якщо вона в межах екрана
            if -50 < sx < 1050 and -50 < sy < 1050:
                draw.circle(window, eat.color, (sx, sy), int(eat.radius * scale))

    for eat in to_remove:
        eats.remove(eat)

    # Виклик міні-карти (Карта 4000 пікселів, міні-карта 150)
    draw_minimap(window, all_players, eats, 4000, 150)

    if lose:
        t = f.render('GAME OVER', 1, (255, 0, 0))
        window.blit(t, (WIDTH // 2 - 100, HEIGHT // 2))

    display.update()
    clock.tick(60)

    # Управління
    if not lose:
        keys = key.get_pressed()
        if keys[K_w]: my_player[1] -= 5
        if keys[K_s]: my_player[1] += 5
        if keys[K_a]: my_player[0] -= 5
        if keys[K_d]: my_player[0] += 5

        # Відправка даних на сервер
        try:
            msg = f"{my_id},{my_player[0]},{my_player[1]},{my_player[2]},{nickname}|"
            sock.send(msg.encode())
        except:
            pass

quit()