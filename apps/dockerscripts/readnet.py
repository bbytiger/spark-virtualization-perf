import sys
import socket

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
    print(f"binding on {host_ip}:{recvport}")
    recvsock.bind((host_ip, recvport))
    recvsock.listen()
    
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

