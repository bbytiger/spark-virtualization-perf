import os
import time
import multiprocessing as mpc
import socket

# TODO: integrate pyspark

def get_port():
    # going to hardcode for now
    pass

def send(port: int, host: str, pipe):
    print(f"send pid {os.getpid()} port {port}")
    
    # use Pipe to synchronize
    msg = pipe.recv()
    if not msg:
        return

    # use IPv4 and TCP
    sendsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sendsock.connect((host, port))
    
    # simply send
    sendsock.sendall(b"my simple message")
    data = sendsock.recv(1024)
    print(f"send {data}")
    
    sendsock.close()

def recv(port: int, host: str, pipe):
    print(f"recv pid {os.getpid()} port {port}")

    # use IPv4 and TCP
    recvsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    # configure to allow port reuse
    recvsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # bind and listen
    print(f"recv binding on {host}:{port}")
    recvsock.bind((host, port))
    recvsock.listen()

    # only send confirmation after listening
    pipe.send(True)

    print("recv waiting for connection...")
    conn, addr = recvsock.accept()
    print(f"Got a connection from {addr}")

    data = conn.recv(1024)
    print(f"recv {data}")

    # cleanup
    conn.sendall(b"data received")
    conn.close()
    
    # cleanup recieve socket
    recvsock.shutdown(socket.SHUT_RDWR)
    recvsock.close()

if __name__ == "__main__":
    # pipe for IPC
    read, write = mpc.Pipe()

    # setup processes
    LISTENING_PORT = 8001
    HOSTNAME = socket.gethostname()
    HOSTIP = socket.gethostbyname(HOSTNAME)

    sendproc = mpc.Process(target=send, args=(LISTENING_PORT, HOSTIP, read,))
    recvproc = mpc.Process(target=recv, args=(LISTENING_PORT, HOSTIP, write,))
    
    # start and join processes
    start = time.time() 
    sendproc.start()
    recvproc.start()
    sendproc.join()
    recvproc.join()
    end = time.time()

    print(f"----- {end - start} sec -----")
