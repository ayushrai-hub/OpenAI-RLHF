import socket

def send_large_message(file_path: str, server_ip: str = '127.0.0.1', server_port: int = 65432, chunk_size: int = 1024 * 64) -> None:
    # Create a socket object
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        # Connect to the server
        s.connect((server_ip, server_port))
        
        with open(file_path, 'rb') as f:
            while True:
                # Read the file in chunks
                chunk = f.read(chunk_size)
                if not chunk:
                    break
                # Send each chunk to the server
                s.sendall(chunk)
        print("Finished sending the file.")

def listen_and_receive_large_message(output_file: str, server_ip: str = '127.0.0.1', server_port: int = 65432, chunk_size: int = 1024 * 64) -> None:
    # Create a socket object
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        # Bind the socket to the IP and port
        s.bind((server_ip, server_port))
        # Listen for incoming connections
        s.listen()
        print(f"Listening on {server_ip}:{server_port}...")

        conn, addr = s.accept()
        with conn:
            print(f"Connected by {addr}")
            with open(output_file, 'wb') as f:
                while True:
                    # Receive data in chunks
                    data = conn.recv(chunk_size)
                    if not data:
                        break
                    f.write(data)
            print(f"Finished receiving the file and saved as {output_file}")

def run_receiver(output_file: str, server_ip: str, server_port: int) -> None:
    listen_and_receive_large_message(output_file, server_ip, server_port)

def run_sender(file_path: str, server_ip: str, server_port: int) -> None:
    send_large_message(file_path, server_ip, server_port)
