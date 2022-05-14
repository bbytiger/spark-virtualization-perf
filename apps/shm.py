import os
import time
import tempfile
import multiprocessing as mpc

from .data import get_data

def send(pipe, fname: str, data: str):
    print(f"send {os.getpid()} fname {fname}")

    f = open(fname, "a+")
    print("send: writing to shared mem...")
    f.write(data)
    f.close()

    # wait until file is written
    pipe.send(True)

def recv(pipe, fname: str):
    print(f"recv {os.getpid()} fname {fname}")

    # wait for msg from send
    msg = pipe.recv()
    if not msg:
        print("recv failed!")
        return
    
    # open, read contents, and close
    f = open(fname, "r")
    contents = f.read()
    print(f"recv: received data")
    f.close()

def main():
    # create a tmp file
    tf = tempfile.NamedTemporaryFile(delete=False)
    fname = tf.name
    tf.close()

    # setup Pipe to synchronize 
    read, write = mpc.Pipe()

    # setup processes and arguments
    data = get_data()
    sendproc = mpc.Process(target=send, args=(write, fname, data,))
    recvproc = mpc.Process(target=recv, args=(read, fname,))

    # start and join all processes
    start = time.time()
    sendproc.start()
    recvproc.start()
    sendproc.join()
    recvproc.join()
    end = time.time()

    # close file
    os.unlink(fname)
    
    print(f"----- {end - start} sec -----")
    return end - start

if __name__ == "__main__":
    main()
