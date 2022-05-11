import os
import tempfile
import multiprocessing as mpc

def send(pipe, fname: str):
    print(f"send {os.getpid()} fname {fname}")

    f = open(fname, "a+")
    print("send writing to shared mem...")
    f.write("a very simple message recv")
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
    print(f"recv data: {contents}")
    f.close()

if __name__ == "__main__":
    # create a tmp file
    tf = tempfile.NamedTemporaryFile(delete=False)
    fname = tf.name
    tf.close()

    # setup Pipe to synchronize 
    read, write = mpc.Pipe()

    # setup processes and arguments
    sendproc = mpc.Process(target=send, args=(write, fname,))
    recvproc = mpc.Process(target=recv, args=(read, fname,))

    # start and join all processes
    sendproc.start()
    recvproc.start()
    sendproc.join()
    recvproc.join()

    # close file
    os.unlink(fname)

