# ideal_completion.py
import socket
import threading
import json
from typing import Dict, List, Any, Optional

CONFIG = {
    'HOST': '127.0.0.1',
    'PORT': 5555,
    'BUFFER_SIZE': 4096,
    'TIMEOUT': 60,
    'MAX_PLAYERS': 100
}

players: Dict[int, Dict[str, Any]] = {}
connections: List[socket.socket] = []
lock = threading.Lock()

def validate_position(pos: Any) -> bool:
    """Validate position data format and values."""
    try:
        return (isinstance(pos, list) and 
                len(pos) == 2 and 
                all(isinstance(x, (int, float)) for x in pos))
    except:
        return False

def handle_client(conn: socket.socket, addr: tuple) -> None:
    """Handle individual client connections and their messages."""
    player_id = addr[1]
    connection_added = False
    
    try:
        conn.settimeout(CONFIG['TIMEOUT'])
        
        with lock:
            if len(players) >= CONFIG['MAX_PLAYERS']:
                return
                
            players[player_id] = {'position': [0, 0], 'moving': False}
            connections.append(conn)
            connection_added = True
        
        while True:
            try:
                data = conn.recv(CONFIG['BUFFER_SIZE'])
                if not data:
                    break
                    
                packet = json.loads(data.decode('utf-8'))
                packet_type = packet.get('type', '')
                
                with lock:
                    if player_id not in players:
                        break
                        
                    if packet_type == 'move_request':
                        target = packet.get('target', [0, 0])
                        if validate_position(target):
                            players[player_id]['position'] = target
                            players[player_id]['moving'] = True
                            
                    elif packet_type == 'update':
                        position = packet.get('position', [0, 0])
                        if validate_position(position):
                            players[player_id]['position'] = position
                            
                    elif packet_type == 'pathObstructed':
                        players[player_id]['moving'] = False
                        
                    elif packet_type == 'destinationReached':
                        players[player_id]['moving'] = False
                
                broadcast_positions()
                
            except json.JSONDecodeError:
                continue
            except socket.timeout:
                break
                
    except Exception as e:
        pass
    finally:
        with lock:
            if player_id in players:
                del players[player_id]
            if connection_added and conn in connections:
                connections.remove(conn)
        try:
            conn.close()
        except:
            pass

def broadcast_positions() -> None:
    """Broadcast updated positions to all connected clients."""
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
        
        disconnected = []
        for conn in connections[:]:
            try:
                conn.sendall(message_json)
            except:
                disconnected.append(conn)
                
        for conn in disconnected:
            try:
                if conn in connections:
                    connections.remove(conn)
            except:
                pass