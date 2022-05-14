import os
import time
import docker
import shutil
import multiprocessing as mpc

# docker with networking

tQ = mpc.Queue()

def copy_data_to_volume(volume_dir: str):
    data_script = "data.py"
    curr_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = curr_dir + "/data"
    dst_dir = volume_dir+f"/data"
    if os.path.exists(dst_dir):
        shutil.rmtree(dst_dir)
    shutil.copytree(data_dir, dst_dir)
    shutil.copy(curr_dir + "/" + data_script, volume_dir+f"/{data_script}")

def remove_data_from_volume(volume_dir: str):
    data_script = "data.py"
    dst_dir = volume_dir+f"/data"
    if os.path.exists(dst_dir):
        shutil.rmtree(dst_dir)
    if os.path.exists(volume_dir+f"/{data_script}"):
        os.remove(volume_dir+f"/{data_script}")

def send(port: int, script: str, remote_host: str, 
        workdir: str, dockercli, container):
    exec_id = dockercli.exec_create(container.id, 
            f"python {script} {remote_host} {port}", workdir=workdir)
    
    # exec with timing
    start = time.time()
    execo = dockercli.exec_start(exec_id)
    end = time.time()
    tQ.put(end - start)

    # print output
    print(f"send output {execo}")

def recv(port: int, script: str, workdir: str, 
        dockercli, container):
    exec_id = dockercli.exec_create(container.id, 
            f"python {script} {port}", workdir=workdir)
    
    # exec with timing
    start = time.time()
    execo = dockercli.exec_start(exec_id)
    end = time.time()
    tQ.put(end - start)

    # print output
    print(f"recv output {execo}")

def main():
    # config
    port = 8001
    read_script = "readnet.py"
    write_script = "writenet.py"
    curr_dir = os.path.dirname(os.path.abspath(__file__))
    scripts_dir = curr_dir + "/dockerscripts"
    remote_volume = "/scripts"
    network_name = 'dockernet'
    image_name = 'python'

    # init client
    client = docker.from_env()

    # check if image exists, pull if not
    try:
        client.api.inspect_image(image_name)    
    except Exception as e:
        client.images.pull(image_name)

    # setup docker network
    nw = client.api.create_network(network_name)
    nw_config = client.api.create_networking_config({
        network_name: client.api.create_endpoint_config()
    })

    # create containers
    abs_scripts_dir = os.path.abspath(scripts_dir)
    bind = f"{abs_scripts_dir}:{remote_volume}"
    host_config = client.api.create_host_config(binds=[bind]) 
    send_container_id = client.api.create_container(image_name, detach=True,
            tty=True, networking_config=nw_config, volumes=[remote_volume], 
            host_config=host_config)
    recv_container_id = client.api.create_container(image_name, detach=True,
            tty=True, networking_config=nw_config, volumes=[remote_volume], 
            host_config=host_config) 

    # get containers and start
    send_container = client.containers.get(send_container_id)
    recv_container = client.containers.get(recv_container_id)
    send_container.start()
    recv_container.start()
    
    # get remote host
    container_info = client.api.inspect_container(recv_container_id["Id"])
    nw_info = container_info["NetworkSettings"]["Networks"]
    remote_host = nw_info[network_name]["IPAddress"]

    print("remote_host", remote_host)

    # setup data and scripts in volume
    copy_data_to_volume(abs_scripts_dir)

    # create processes
    sendproc = mpc.Process(target=send, args=(port, write_script, remote_host, 
        remote_volume, client.api, send_container,))
    recvproc = mpc.Process(target=recv, args=(port, read_script, remote_volume, 
        client.api, recv_container,))

    # start and join processes
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
    
    # remove network and clean containers
    send_container.stop()
    recv_container.stop() 
    client.api.remove_container(send_container_id)
    client.api.remove_container(recv_container_id)
    client.api.remove_network(nw["Id"])
    remove_data_from_volume(abs_scripts_dir)
    
    # return total time
    return end - start

if __name__ == "__main__":
    main()
