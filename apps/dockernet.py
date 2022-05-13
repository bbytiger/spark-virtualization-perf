import docker
import multiprocessing

# docker with networking

def send():
    pass

def recv():
    pass

if __name__ == "__main__":
    read_script = "readnet.py"
    write_script = "writenet.py"
    client = docker.from_env()
    image_name = 'python'

    # check if image exists, pull if not
    try:
        client.api.inspect_image(image_name)    
    except Exception as e:
        client.images.pull(image_name)

    # setup docker network

    # get containers and start
    send_container = client.containers.get(send_container_id)
    recv_container = client.containers.get(recv_container_id)
    send_container.start()
    recv_container.start()

    # remove volume and clean containers
    send_container.stop()
    recv_container.stop()
    client.api.remove_volume(volume_name)
    client.api.remove_container(send_container_id)
    client.api.remove_container(recv_container_id)
