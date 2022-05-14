import sys
import time
import socket
import struct

from data import get_data

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Format: python3 writenet.py <send_host> <send_port>")
    host = sys.argv[1]
    port = int(sys.argv[2]) 

    sendsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    print(f"send: connecting to {host}:{port}...")
    while True:
        try:
            sendsock.connect((host, port))
            print(f"send: connection accepted.")
            break
        except Exception as e:
            continue
   
    # get data
    raw_data = get_data()
    start = time.time()
    data = raw_data.encode()
    end = time.time()
    print(f"time to encode: {end-start}")

    # simply send
    print(f"send: sending {len(data)} bytes")
    len_hdr = struct.pack(">Q", len(data))
    sendsock.sendall(len_hdr)
    sendsock.sendall(data)

    # wait for confirmation
    recvdata = sendsock.recv(1024)
    print(f"send: {recvdata}")
                            
    sendsock.close()
