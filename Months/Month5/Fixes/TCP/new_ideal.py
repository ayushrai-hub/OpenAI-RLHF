import socket
import threading
import json
import logging
from typing import List, Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Server configuration
HOST = '127.0.0.1'
PORT = 5555

# Global state (accessible for testing)
players: Dict[int, Dict[str, Any]] = {}
connections: List[socket.socket] = []
lock = threading.Lock()

def handle_client(conn: socket.socket, addr: tuple) -> None:
    """
    Handle individual client connections.
    Args:
        conn: Client socket connection
        addr: Client address tuple (ip, port)
    """
    player_id = addr[1]
    
    try:
        with lock:
            players[player_id] = {
                'position': [0.0, 0.0],
                'moving': False
            }
        
        while True:
            try:
                data = conn.recv(1024)
                if not data:
                    break

                packet = json.loads(data.decode('utf-8'))
                handle_packet(player_id, packet)
                
            except json.JSONDecodeError:
                logging.error(f"Invalid JSON from player {player_id}")
            except Exception as e:
                logging.error(f"Error handling client {player_id}: {str(e)}")
                break
                
    finally:
        cleanup_client(conn, player_id)

def handle_packet(player_id: int, packet: Dict[str, Any]) -> None:
    """
    Process incoming game packets.
    Args:
        player_id: Unique player identifier
        packet: Decoded packet data
    """
    packet_type = packet.get('type')
    
    with lock:
        # Initialize player data if it doesn't exist
        if player_id not in players:
            players[player_id] = {
                'position': [0.0, 0.0],
                'moving': False
            }
            
        if packet_type == 'move_request':
            players[player_id]['position'] = packet['target']
            players[player_id]['moving'] = True
            
        elif packet_type == 'update':
            players[player_id]['position'] = packet['position']
            
        elif packet_type == 'path_blocked':
            players[player_id]['moving'] = False
            
        elif packet_type == 'reached':
            players[player_id]['moving'] = False

    broadcast_positions()

def broadcast_positions() -> None:
    """Broadcast current positions of all players to all connected clients."""
    with lock:
        message = json.dumps({
            'type': 'sync',
            'players': {
                str(pid): {
                    'position': info['position'],
                    'moving': info['moving']
                }
                for pid, info in players.items()
            }
        })
        
        dead_connections = []
        for conn in connections:
            try:
                conn.sendall(message.encode('utf-8'))
            except:
                dead_connections.append(conn)
        
        # Cleanup dead connections
        for conn in dead_connections:
            if conn in connections:
                connections.remove(conn)
                try:
                    conn.close()
                except:
                    pass

def cleanup_client(conn: socket.socket, player_id: int) -> None:
    """
    Clean up resources when a client disconnects.
    Args:
        conn: Client socket connection
        player_id: Player's unique identifier
    """
    with lock:
        if player_id in players:
            del players[player_id]
        if conn in connections:
            connections.remove(conn)
    
    try:
        conn.close()
    except:
        pass
    
    broadcast_positions()

def start_server() -> None:
    """Initialize and start the game server."""
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:
        server_socket.bind((HOST, PORT))
        server_socket.listen(5)
        logging.info(f"Server started on {HOST}:{PORT}")
        
        while True:
            conn, addr = server_socket.accept()
            connections.append(conn)
            
            client_thread = threading.Thread(
                target=handle_client,
                args=(conn, addr),
                daemon=True
            )
            client_thread.start()
            
    except KeyboardInterrupt:
        logging.info("Server shutting down...")
    except Exception as e:
        logging.error(f"Server error: {str(e)}")
    finally:
        server_socket.close()
        
        # Cleanup all connections
        with lock:
            for conn in connections:
                try:
                    conn.close()
                except:
                    pass
            connections.clear()
            players.clear()

if __name__ == "__main__":
    start_server()