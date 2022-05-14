import sys
import socket
import struct

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Format: python3 readnet.py <receive_port>")

    # get port from args
    host = socket.gethostname() 
    recvport = int(sys.argv[1])

    # use IPv4 and TCP
    recvsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            
    # configure to allow port reuse
    recvsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # bind and listen
    host_ip = socket.gethostbyname(host)
    print(f"recv: binding on {host_ip}:{recvport}")
    recvsock.bind((host_ip, recvport))
    recvsock.listen()
    
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

    # cleanup
    conn.sendall(f"data of size {len(data)} received".encode())
    conn.close()
 
    # cleanup recieve socket
    recvsock.shutdown(socket.SHUT_RDWR)
    recvsock.close()

