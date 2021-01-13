# uAV communIcation dAta Traffic generatOR (AVIATOR) 

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

AVIATOR is a UAV-RC data traffic generation tool based on the data distribution models derived from our experimental UAV measurements. It generates UDP packets according to the data rate, inter-packet interval and packet length distributions of commercial UAV-RC traffic (DJI Spark, DJI Mavic Air and Parrot Spark). AVIATOR records the generated packets as well as their statistical results. It is the outcome of our paper *[Experimental Data Traffic Modeling and Network Performance Analysis of UAVs]()*, to be presented at *[2021 IEEE International Conference on Computer Communications (INFOCOM)](https://infocom2021.ieee-infocom.org/)*. 

AVIATOR can be used in variety of UAV-related applications. Having scientific studies as the primary use-case in mind, AVIATOR can be used to study the UAV traffic characteristics, to design UAV/airborne communication systems, to provide input traffic data for UAV/airborne simulators as well as emulators, or simply as a data traffic generator for other internet applications.   

## Citation

Please cite AVIATOR in your work if you find it useful:  

```bibtex
@inproceedings{aviator,
  doi = {TBD},
  url = {TBD},
  year = {2021},
  month = may,
  publisher = {{IEEE}},
  author = {A. {Baltaci} and M. {Kluegel} and F. {Geyer} and S. {Duhovnikov} and V. {Bajpai} and J. {Ott} and D. {Schupke}},
  title = {Experimental UAV Data Traffic Modeling and Network Performance Analysis},
  booktitle = {2021 {IEEE} International Conference on Computer Communications ({INFOCOM})}
}
```

## Dependencies
**[Python3](https://www.python.org/download/releases/3.0/)**
> sudo apt install python3-dev python3-pip

**[Matplotlib](https://matplotlib.org/), [NumPy](https://numpy.org/) and [Scapy](https://scapy.net/) libraries**
> pip3 install matplotlib numpy scapy 

## Usage
**Run the program**
> python3 generate_uavtraffic.py

**Optional parameters**:
- *--uplink | -u* to generate packets for uplink channel
  - Otherwise, Downlink channel is the default
  - Only 1 channel can be selected at each run
- *-n* is the number of packets to generate

**Keep in mind**
- You should generate **~15000 packets for DL and 30000 packets for UL** channels to observe the distributions correctly.
- For more information regarding the traffic models, please refer to our paper.
- For graph-related settings, you may find them all in *config_matplotlibrc.py*, which is an excerpt of [matplotlibrc configuration file](https://matplotlib.org/3.2.1/tutorials/introductory/customizing.html). 

## Results
Generated results are saved in the folder *outputfiles/*:
- **.csv**: Statistical results in terms of packet inter-arrival, packet length and data rate
- **.pcap**: The record of the generated packets
- **.pdf**: The distribution graphs of the statistics in *.csv* file

## uav_datatraces.zip
Sample of original UDP data traces of the UAVs (DJI Spark, DJI Mavic and Parrot AR 2.0) are provided to observe the actual UAV data traffic. For the details of the measurements, you may refer to the Section III of the paper. Note that the MAC addresses are changed and the payloads are removed from these traces. 

## Copyright
This code is licensed under GNU General Public License v3.0. For further information, please refer to [LICENSE](LICENSE)
