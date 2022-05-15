# CS260R Final Project: Investigating Performance of Spark using Virtualization

This is the source code for the final project for Harvard's 2022 iteration of CS260R: Topics and Close Readings in Software Systems. Work on this project was done by William Cooper, Andrew Sima, and Jaylen Wang.

## Design: Prototyping Networking and Shared Memory

This repository has several code examples of prototypes that we built to test the performance of docker on networking and shand memory. The `apps/` directory contains the following designs:
- `shm.py` 
- `net.py`
- `dockernet.py`
- `dockershm.py`
- `netserialize.py`
- `dockernetserialize.py`

The implementation that we employed is the following: we have two processes (using `multiprocessing`), one sending and one receiving. The sending process will either write to shared memory or send it over the network. The receiving process will either read from the previously written shared memory, or wait to receive the data sent over network.

To model shared memory without docker, we simply used a file. To model shared memory using docker, we created a volume and used a file created in this volume as our region of shared memory. To model networking, we instantiated TCP sockets listening on the ports of the respective hosts, sending and receiving on these specified ports. To model serialization, we used the default serialization scheme provided by the `pickle` module.

## Setup

We recommend running the project in a Python virtual environment. After setting up your virtual environment and installing the requirements through `pip install -r requirements.txt`, make sure that Docker Engine is running and you should be good to go. 

## Running Experiments

The driver code for running experiments is the `experiments.py` file in the root directory. To do so simply run 

```python
python3 experiments.py
```

After finishing, the script will print the average execution times for each of the six prototypes. By default, this will run 10 iterations on the `airbnb.csv` dataset. If you would like to change the dataset, you can modify `./apps/data.py` to select a different dataset from the `./apps/data` directory. 
