import sys
import time
import socket
import pickle

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Format: python3 writenet.py <send_host> <send_port>")
    host = sys.argv[1]
    port = int(sys.argv[2]) 

    sendsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    print(f"connecting to {host}:{port}...")
    while True:
        try:
            sendsock.connect((host, port))
            print(f"connection accepted.")
            break
        except Exception as e:
            continue

    # simply send 
    msg = "my simple message"
    serialize = pickle.dumps(msg)
    sendsock.sendall(serialize)

    # wait for confirmation message
    data = sendsock.recv(1024)
    print(f"write connection received: {data}")
                            
    sendsock.close()
