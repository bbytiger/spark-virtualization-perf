import os
import time
import shutil
import inspect
import docker
import multiprocessing as mpc

# docker with shared memory design

tQ = mpc.Queue()

def copy_data_to_volume(volume): 
    data_script = "data.py"
    curr_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = curr_dir + "/data"
    dst_dir = volume["Mountpoint"]+f"/data"
    if os.path.exists(dst_dir):
        shutil.rmtree(dst_dir)
    shutil.copytree(data_dir, dst_dir)
    shutil.copy(curr_dir + "/" + data_script, volume["Mountpoint"]+f"/{data_script}")

def copy_file_to_volume(script: str, volume):
    curr_dir = os.path.dirname(os.path.abspath(__file__))
    scripts_dir = curr_dir + "/dockerscripts/"
    shutil.copy(scripts_dir+script, volume["Mountpoint"]+f"/{script}")

def send(pipe, container, dockercli, script: str, workdir: str):
    print(f"send {os.getpid()} container {container}")

    # exec write
    exec_id = dockercli.exec_create(container.id, f"python {script}", workdir=workdir)
    
    # exec and record time
    start = time.time()
    execo = dockercli.exec_start(exec_id)

    # wait until file is written
    pipe.send(True)

    # record final time
    end = time.time()
    tQ.put(end - start)

    # print output
    print(f"send output {execo}")

def recv(pipe, container, dockercli, script: str, workdir: str):
    print(f"recv {os.getpid()} container {container}")
     
    # create exec read
    exec_id = dockercli.exec_create(container.id, f"python {script}", workdir=workdir)
    
    # start timing
    start = time.time()

    # wait for msg from send
    msg = pipe.recv()
    if not msg:
        print("recv failed!")
        return

    # exec and record time
    execo = dockercli.exec_start(exec_id)
    end = time.time()
    tQ.put(end - start)

    print(f"recv output {execo}")

def main():
    # config
    read_script = "readshm.py"
    write_script = "writeshm.py"
    client = docker.from_env()
    image_name = 'python'

    # check if image exists, pull if not
    try:
        client.api.inspect_image(image_name)    
    except Exception as e:
        client.images.pull(image_name)

    # setup volume
    volume_name = 'dockershm'
    remote_volume = '/mnt/vol'
    try:
        volume = client.api.inspect_volume(volume_name)
    except Exception as e:
        volume = client.api.create_volume(volume_name)

    # setup containers
    bind = f"{volume['Mountpoint']}:{remote_volume}"
    print(f"bind {bind}")
    host_config = client.api.create_host_config(binds=[bind])
    send_container_id = client.api.create_container(image_name, detach=True, 
            tty=True, volumes=[remote_volume], host_config=host_config)
    recv_container_id = client.api.create_container(image_name, detach=True, 
            tty=True, volumes=[remote_volume], host_config=host_config)
    
    # get containers and start
    send_container = client.containers.get(send_container_id)
    recv_container = client.containers.get(recv_container_id)
    send_container.start()
    recv_container.start()

    # get scripts
    copy_file_to_volume(read_script, volume)
    copy_file_to_volume(write_script, volume)
    copy_data_to_volume(volume)

    # setup Pipe to synchronize
    read, write = mpc.Pipe()

    # setup processes and arguments
    sendproc = mpc.Process(target=send, args=(write, 
        send_container, client.api, write_script, remote_volume,))
    recvproc = mpc.Process(target=recv, args=(read, 
        recv_container, client.api, read_script, remote_volume,))

    # start and join all processes
    start = time.time()
    sendproc.start()
    recvproc.start()
    sendproc.join()
    recvproc.join()
    end = time.time()
    
    # get times
    t1 = tQ.get()
    t2 = tQ.get()
    print(f"----- t1: {t1} sec, t2: {t2} sec -----")
    print(f"----- total: {end - start} sec -----")

    # remove volume and clean containers
    send_container.stop()
    recv_container.stop()
    client.api.remove_volume(volume_name)
    client.api.remove_container(send_container_id)
    client.api.remove_container(recv_container_id)
    
    return end - start

if __name__ == "__main__":
    main()
