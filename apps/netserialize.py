import os
import time
import multiprocessing as mpc
import pickle
import socket
import struct

from .data import get_data

# TODO: integrate pyspark

def get_port():
    # going to hardcode for now
    pass

def send(port: int, host: str, data: str, pipe):
    print(f"send: pid {os.getpid()} port {port}")
    
    # use Pipe to synchronize
    msg = pipe.recv()
    if not msg:
        return

    # use IPv4 and TCP
    sendsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sendsock.connect((host, port))
    
    # simply send
    serialized_data = pickle.dumps(data)
    print(f"send: sending {len(serialized_data)} bytes")
    len_hdr = struct.pack(">Q", len(serialized_data))
    sendsock.sendall(len_hdr)
    sendsock.sendall(serialized_data)
    
    # wait for confirmation
    recvdata = sendsock.recv(1024)
    print(f"send: {recvdata}")
    
    sendsock.close()

def recv(port: int, host: str, pipe):
    print(f"recv: pid {os.getpid()} port {port}")

    # use IPv4 and TCP
    recvsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    # configure to allow port reuse
    recvsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # bind and listen
    print(f"recv: binding on {host}:{port}")
    recvsock.bind((host, port))
    recvsock.listen()

    # only send confirmation after listening
    pipe.send(True)

    print("recv: waiting for connection...")
    conn, addr = recvsock.accept()
    print(f"recv: got a connection from {addr}")
    
    # get data length
    HDR_SIZE = 8
    BUF_SIZE = 4096
    len_hdr = conn.recv(HDR_SIZE)
    (length,) = struct.unpack(">Q", len_hdr)
   
    # batch read data
    data = b''
    while len(data) < length:
        bytes_left = length - len(data)
        data += conn.recv(BUF_SIZE if bytes_left > BUF_SIZE else bytes_left)
    print(f"recv: received {len(data)} bytes")

    deserialized_data = pickle.loads(data)

    # cleanup
    conn.sendall(f"data of size {len(deserialized_data)} received".encode())
    conn.close()
    
    # cleanup recieve socket
    recvsock.shutdown(socket.SHUT_RDWR)
    recvsock.close()

def main():
    # pipe for IPC
    read, write = mpc.Pipe()

    # setup processes
    LISTENING_PORT = 8001
    HOSTNAME = socket.gethostname()
    HOSTIP = socket.gethostbyname(HOSTNAME)

    sendproc = mpc.Process(target=send, args=(LISTENING_PORT, HOSTIP, get_data(), read,))
    recvproc = mpc.Process(target=recv, args=(LISTENING_PORT, HOSTIP, write,))
    
    # start and join processes
    start = time.time() 
    sendproc.start()
    recvproc.start()
    sendproc.join()
    recvproc.join()
    end = time.time()

    print(f"----- {end - start} sec -----")
    return end - start

if __name__ == "__main__":
    main()

