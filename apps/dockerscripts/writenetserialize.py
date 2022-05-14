import sys
import time
import socket
import pickle
import struct

from data import get_data

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Format: python3 writenetserialize.py <send_host> <send_port>")
    host = sys.argv[1]
    port = int(sys.argv[2]) 

    sendsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    print(f"send: connecting to {host}:{port}...")
    while True:
        try:
            sendsock.connect((host, port))
            print(f"connection accepted.")
            break
        except Exception as e:
            continue
    
    # get data
    data = get_data()
    start = time.time()
    serialize = pickle.dumps(data)
    end = time.time()
    print(f"time to serialize {end-start}")

    # simply send 
    print(f"send: sending {len(serialize)} bytes")
    len_hdr = struct.pack(">Q", len(serialize))
    sendsock.sendall(len_hdr)
    sendsock.sendall(serialize)

    # wait for confirmation message
    recvdata = sendsock.recv(1024)
    print(f"send: {recvdata}")
                            
    sendsock.close()
