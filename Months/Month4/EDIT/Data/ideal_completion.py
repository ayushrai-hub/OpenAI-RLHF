import socket
import threading
import json

# Shared state and threading lock
players = {}
connections = []
lock = threading.Lock()


def handle_client(conn, addr):
    """Handle incoming client connection."""
    player_id = addr[1]

    # Initialize player state
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

                with lock:
                    if packet_type == 'move_request':
                        target = packet.get('target')
                        if isinstance(target, list) and len(target) == 2:
                            players[player_id]['position'] = target
                            players[player_id]['moving'] = True

                    elif packet_type == 'update':
                        position = packet.get('position')
                        if isinstance(position, list) and len(position) == 2:
                            players[player_id]['position'] = position

                    elif packet_type == 'pathObstructed':
                        players[player_id]['moving'] = False

                    elif packet_type == 'destinationReached':
                        players[player_id]['moving'] = False

                broadcast_positions()

            except json.JSONDecodeError:
                # Log malformed JSON and continue
                print(f"Malformed packet from {addr}")
                continue

    except Exception as e:
        print(f"Error handling client {addr}: {e}")

    finally:
        # Clean up the player state and connections
        with lock:
            if player_id in players:
                del players[player_id]
            if conn in connections:
                connections.remove(conn)
        conn.close()


def broadcast_positions():
    """Broadcast the positions of all players to connected clients."""
    with lock:
        message = {
            'type': 'sync',
            'players': [
                {'player_id': pid, 'position': pdata['position'], 'moving': pdata['moving']}
                for pid, pdata in players.items()
            ]
        }
        message_json = json.dumps(message).encode('utf-8')

        for conn in list(connections):  # Iterate over a copy to avoid modification issues
            try:
                conn.sendall(message_json)
            except Exception:
                # Remove connection if sending fails
                with lock:
                    connections.remove(conn)
