from socket import socket, AF_INET, SOCK_STREAM
import time
from threading import Thread

sock = socket(AF_INET, SOCK_STREAM)
sock.bind(('localhost', 8080))
sock.listen(5)
sock.setblocking(False)


players = {}
conn_id = {}
id_conter = 0


def handle_client():
    global id_conter
    while True:
        time.sleep(0.01)
        player_data = {}
        to_remove =[]


        for conn in list(players):
            try:
                data = conn.recv(64).decode().strip("|")
                if "," in data:
                    parts = data.split(",")
                    if len(parts) == 4:
                        pid, x, y, radius = map(int, parts)
                        players[conn] = {
                            "id": pid,
                            "x": x,
                            "y": y,
                            "radius": radius
                        }
                        player_data[conn] = players[conn]

            except:
                continue

        eliminated =[]
        for conn in player_data:
            if conn1 in eliminated: continue
            p1 = player_data[conn1]
            for conn2 in player_data:
                if conn1  == conn2 or conn2 in eliminated: continue
                p2 = player_data[conn2]
                dx , dy = p1['x'] - p2['x'], p1['y'] - p2['y']
                distance = (dx**2 + dy**2)**0.5
                if distance < p1['radius'] + p2['radius'] and p1['radius'] > p2['radius'] * 1.1:
                    p1['radius'] += int(p2['radius'] * 0.5)
                    players[conn1] = p1
                    eliminated.append(conn2)


        for conn in list(players.keys()):
            if conn in eliminated:
                try:
                    conn.send("LOSE".encode())
                except:
                    pass
                to_remove.append(conn)
                continue

            try:
                packet = '|'.join(f"{p['id']},{p['x']},{p['y']},{p['radius']}" for c , p in players.items() if c != conn and c not in eliminated) + '|'
                conn.send(packet.encode())
            except:
                to_remove.append(conn)

        for conn in to_remove:
            players.pop(conn, None)
            conn_ids.pop(conn, None)


Thread(target=handle_client, daemon=True).start()
print('Server running...')

while True:
    try:
        conn, addr = sock.accept()
        conn.setblocking(False)
        id_conter += 1
        players[conn] = {'id': id_conter, 'x': 0, 'y': 0, 'radius': 20}
        conn_ids[conn] = id_conter
        conn.send(f"{id_conter},0,0,20".encode())
    except:
        pass

