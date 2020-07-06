# UAVDataGenerator 

UAVDataTrafficGenerator is a UAV-RC data traffic generation tool based on the data distribution models derived from experimental UAV measurements. It is the outcome of our paper *[Experimental Data Traffic Modeling and Network Performance Analysis of UAVs]()*, which is presented at *[xxx]()*. 

## Dependencies
**[Python3](https://www.python.org/download/releases/3.0/)**
> sudo apt install python3-dev python3-pip

**[Matplotlib](https://matplotlib.org/), [NumPy](https://numpy.org/) and [Scapy](https://scapy.net/) libraries**
> pip3 install matplotlib numpy scapy 

## Usage
**Run the program**
> python3 generate_uavtraffic.py

**Optional Parameters**:
- *--uplink | -u* to generate packets for uplink channel
  - Otherwise, Downlink channel is the default
  - Only 1 channel can be selected at each run
- *-n* is the number of packets to generate

**Keep in Mind**
- You should generate at least **~5000 packets** to observe the distributions correctly.
- For more information regarding the traffic models, please refer to our paper.
- For graph-related settings, you may find them all in *config_matplotlibrc.py*, which is an excerpt of [matplotlibrc configuration file](https://matplotlib.org/3.2.1/tutorials/introductory/customizing.html). 

## Results
Generated results are saved in the folder *outputfiles/*:
- **.csv**: Statistical results in terms of packet inter-arrival, packet length and data rate
- **.pcap**: The record of the generated packets
- **.pdf**: The distribution graphs of the statistics in *.csv* file

## uav_datatraces.zip
Sample of original UDP data traces of the UAVs (DJI Spark, DJI Mavic and Parrot AR 2.0) are provided to observe the actual UAV data traffic. For the details of the measurements, you may refer to the Section III of the paper. 

Note that the MAC addresses are changed and the payloads are removed from the packets. 

## Copyright
This code is licensed under GNU General Public License v3.0. For further information, please refer to [LICENSE](LICENSE)
