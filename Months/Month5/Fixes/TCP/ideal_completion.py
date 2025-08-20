import socket
import threading
import json

# Global state
players = {}
connections = []
lock = threading.Lock()

def handle_client(conn, addr):
    """Handle individual client connections."""
    player_id = addr[1]  # Use client's port number as player ID
    
    # Initialize player state immediately on connection
    with lock:
        players[player_id] = {'position': [0, 0], 'moving': False}
        if conn not in connections:
            connections.append(conn)
    
    try:
        while True:
            try:
                data = conn.recv(4096)
                if not data:
                    break
                
                packet = json.loads(data.decode('utf-8'))
                packet_type = packet.get('type')
                
                with lock:
                    if packet_type == 'move_request':
                        target = packet.get('target', [0, 0])
                        if isinstance(target, list) and len(target) == 2:
                            players[player_id]['position'] = target
                            players[player_id]['moving'] = True
                    
                    elif packet_type == 'update':
                        position = packet.get('position', [0, 0])
                        if isinstance(position, list) and len(position) == 2:
                            players[player_id]['position'] = position
                    
                    elif packet_type == 'pathObstructed':
                        players[player_id]['moving'] = False
                    
                    elif packet_type == 'destinationReached':
                        players[player_id]['moving'] = False
                
                broadcast_positions()
            
            except json.JSONDecodeError:
                # Log the error or notify about the invalid JSON, but do not terminate or skip further processing
                print("Received invalid JSON from client:", addr)
                continue  # Continue the loop to read the next data packet

    finally:
        with lock:
            if player_id in players:
                del players[player_id]
            if conn in connections:
                connections.remove(conn)
        conn.close()


def broadcast_positions():
    """Broadcast current positions to all connected clients."""
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
        
        # Create a copy to avoid modification during iteration
        current_connections = connections.copy()
        
        for conn in current_connections:
            try:
                conn.sendall(message_json)
            except:
                # Failed connections will be cleaned up by their respective handler threads
                continue