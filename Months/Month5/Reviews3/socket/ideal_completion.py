# ideal_completion.py
import socket
import os
import threading

def listen_and_receive_large_message(output_file: str, server_ip: str = '127.0.0.1', server_port: int = 65432, chunk_size: int = 1024 * 64):
    """Listens on the given IP and port, receiving a large message in chunks and saving it to an output file."""
    try:
        # Create a socket object
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((server_ip, server_port))
            s.listen(1)
            print(f"Listening on {server_ip}:{server_port}...")

            # Accept a connection
            conn, addr = s.accept()
            with conn:
                print(f"Connected by {addr}")
                total_bytes = 0
                with open(output_file, 'wb') as f:
                    while True:
                        # Receive data in chunks
                        data = conn.recv(chunk_size)
                        if not data:
                            break
                        f.write(data)
                        total_bytes += len(data)
                        
                        # Log progress only after every 50 MB
                        if total_bytes >= 50 * 1024 * 1024 and total_bytes % (50 * 1024 * 1024) < chunk_size:
                            print(f"Received {total_bytes // (1024 * 1024)} MB...")
                print(f"Finished receiving the file. Total size: {total_bytes // (1024 * 1024)} MB.")
    except Exception as e:
        print(f"Error: {e}")

def send_large_message(file_path: str, server_ip: str = '127.0.0.1', server_port: int = 65432, chunk_size: int = 1024 * 64):
    """Sends a large message from the specified file to the server in chunks."""
    try:
        # Check if the file exists before sending
        if not os.path.exists(file_path):
            print(f"File {file_path} does not exist.")
            return
        
        file_size = os.path.getsize(file_path)

        # Create a socket object
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((server_ip, server_port))

            sent_bytes = 0
            with open(file_path, 'rb') as f:
                while True:
                    chunk = f.read(chunk_size)
                    if not chunk:
                        break
                    s.sendall(chunk)
                    sent_bytes += len(chunk)
                    
                    # Log progress only after every 50 MB
                    if sent_bytes >= 50 * 1024 * 1024 and sent_bytes % (50 * 1024 * 1024) < chunk_size:
                        print(f"Sent {sent_bytes // (1024 * 1024)} MB...")

            print(f"Finished sending the file. Total size: {sent_bytes // (1024 * 1024)} MB.")
    except Exception as e:
        print(f"Error: {e}")

def run_receiver(output_file: str, server_ip: str, server_port: int):
    listen_and_receive_large_message(output_file, server_ip, server_port)

def run_sender(file_path: str, server_ip: str, server_port: int):
    send_large_message(file_path, server_ip, server_port)

if __name__ == "__main__":
    # Define parameters for sender and receiver
    output_file = "received_large_file.bin"
    file_path = "large_file.bin"
    
    # IP and port settings
    server_ip = input("Enter the IP address (default is 127.0.0.1): ").strip() or '127.0.0.1'
    server_port = int(input("Enter the port number (default is 65432): ").strip() or 65432)

    # Create threads for both the sender and receiver
    receiver_thread = threading.Thread(target=run_receiver, args=(output_file, server_ip, server_port))
    sender_thread = threading.Thread(target=run_sender, args=(file_path, server_ip, server_port))

    # Start both threads
    receiver_thread.start()
    sender_thread.start()

    # Wait for both threads to finish
    receiver_thread.join()
    sender_thread.join()

    print("File transfer completed.")