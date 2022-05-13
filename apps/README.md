# CS260R Final Project: Investigating Performance of Spark using Virtualization

## Prototyping Networking and Shared Memory

This repository has several code examples of prototypes that we built to test the performance of docker on networking and shand memory. The `apps/` directory contains the following designs:
- `shm.py` 
- `net.py`
- `dockernet.py`
- `dockershm.py`

The implementation that we employed is the following: we have two processes (using `multiprocessing`), one sending and one receiving. The sending process will either write to shared memory or send it over the network. The receiving process will either read from the previously written shared memory, or wait to receive the data sent over network.

To model shared memory without docker, we simply used a file. To model shared memory using docker, we created a volume and used a file created in this volume as our region of shared memory. To model networking, we instantiated TCP sockets listening on the ports of the respective hosts, sending and receiving on these specified ports.
