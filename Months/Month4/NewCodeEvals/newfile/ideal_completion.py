import socket
import threading
import json

players = {}
connections = []
lock = threading.Lock()

def handle_client(conn, addr):
    player_id = addr[1]  # Use client's port number as player ID
    with lock:
        players[player_id] = {'position': [0, 0], 'moving': False}
        connections.append(conn)
    try:
        while True:
            data = conn.recv(4096)
            if not data:
                break
            try:
                packet = json.loads(data.decode('utf-8'))
                packet_type = packet.get('type')
                if packet_type == 'move_request':
                    target = packet.get('target', [0, 0])
                    if isinstance(target, list) and len(target) == 2:
                        with lock:
                            players[player_id]['position'] = target
                            players[player_id]['moving'] = True
                elif packet_type == 'update':
                    position = packet.get('position', [0, 0])
                    if isinstance(position, list) and len(position) == 2:
                        with lock:
                            players[player_id]['position'] = position
                elif packet_type == 'pathObstructed':
                    with lock:
                        players[player_id]['moving'] = False
                elif packet_type == 'destinationReached':
                    with lock:
                        players[player_id]['moving'] = False
                # Broadcast positions after handling packet
                broadcast_positions()
            except json.JSONDecodeError:
                # Invalid JSON data received
                pass
    finally:
        with lock:
            if player_id in players:
                del players[player_id]
            if conn in connections:
                connections.remove(conn)
        conn.close()

def broadcast_positions():
    with lock:
        player_list = []
        for pid, pdata in players.items():
            player_info = {
                'player_id': pid,
                'position': pdata['position'],
                'moving': pdata['moving']
            }
            player_list.append(player_info)
        message = {
            'type': 'sync',
            'players': player_list
        }
        message_json = json.dumps(message).encode('utf-8')
        for conn in connections:
            try:
                conn.sendall(message_json)
            except:
                pass