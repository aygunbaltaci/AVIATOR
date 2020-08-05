#!/usr/bin/env python3

#####################################################
# 25.05.2020
#
# This code generates UAV data traffic according to
# distribution models based on actual UAV data. 
# 
# Prerequisites: pip3 install matplotlib numpy scapy
#
# Author: Aygün Baltaci
# Institution: Technical University of Munich
#
# License: GNU General Public License v3.0
#
#####################################################

import argparse
import config_matplotlibrc
from datetime import datetime
import math
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from scapy.all import *
from scapy.utils import rdpcap
import time

# ======== variables - modify them as you wish =========
date = datetime.now().strftime('%Y%m%d_%H%M%S')

# graph-related
figure_dimensions = (25.6, 14.4)
figure_format = 'pdf'
label_x = ['Data Rate (kbps)', 'Packet Inter-arrival (ms)', 'Packet Length (bytes)']
label_y = 'Density'
legend = 'Simulated data'
legend_location = (0.5, 0.05)
numofbins = [25, 20, 15] # num of bins for hist plots. [15, 20, 10] 

# outputfiles-related
outputfile_packets_extension = 'pcap'
outputfile_statistics_extension = 'csv'
outputfile_statistics_headernames = ['Packet Inter-arrival (ms)', 'Packet Length (bytes)', 'Data Rate (kbps)']
outputfolder = 'outputfiles'

# packet-related 
ip_source = '10.0.0.201'
ip_destination = '10.0.0.208'
pkt_length_maximum = 1486
port_source = 47813 
port_destination = 47814

# ========================================
# Frequencies of data generation. 
# Each number corresponds to in how many  
# CPU cycles the parameter is generated.
# ========================================
frequency_buffer = 3
# downlink
frequency_land_takeoff = 7 # 7
frequency_pitch_roll = 3 # 2
frequency_throttle_yaw = 5 # 1
frequency_return_home = 13 # 5
frequency_test = 13
# uplink
frequency_batterystatus_camerastatus = 6
frequency_imustatus_rotorstatus = 3
frequency_video = 1

# ======== Send downlink data to UDP buffer
def data_to_buffer_downlink(buffer, i, land_takeoff, pitch_roll, return_home, throttle_yaw):
	# add data to UDP buffer
	if i % frequency_throttle_yaw == 0:
		buffer += (throttle_yaw)
	if i % frequency_pitch_roll == 0:
		buffer += (pitch_roll)
	if i % frequency_land_takeoff == 0:
		buffer += (land_takeoff)
	if i % frequency_return_home == 0:
		buffer += (return_home)
	return buffer

# ======== Send uplink data to UDP buffer
def data_to_buffer_uplink(batterystatus, buffer, camerastatus, 
		i, imustatus, rotorstatus, video):
	# add data to UDP buffer
	if i % frequency_video == 0:
		buffer += (video)
	if i % frequency_imustatus_rotorstatus == 0:
		buffer += (rotorstatus)
		buffer += (imustatus)
	if i % frequency_batterystatus_camerastatus == 0:
		buffer += (camerastatus)
		buffer += (batterystatus)
	return buffer

# ======== Generate data for downlink channel
def generate_data_downlink():
	land_takeoff = 't' * np.random.choice([2**5, 2**6, 2**7])
	pitch_roll = 'r' * np.random.choice([2**5 + 2**4, 2**5, 2**6])
	return_home = 'h' * np.random.choice([2**5 + 2**4, 2**6 + 2**4, 2**6])
	throttle_yaw =  'l' * np.random.choice([2**5, 2**5 + 2**4, 2**6])

	return land_takeoff, pitch_roll, return_home, throttle_yaw

# ======== Generate data for uplink channel
def generate_data_uplink():
	# telemetry data
	batterystatus =  'b' * np.random.choice([2**5, 2**6])
	camerastatus = 'm' * np.random.choice([2**5, 2**6])
	imustatus = 'i' * np.random.choice([2**5, 2**6])
	rotorstatus = 'o' * np.random.choice([2**5, 2**6])
	# video data
	video = 'v' * int(np.random.normal(3000, 1500)) 

	return batterystatus, camerastatus, imustatus, rotorstatus, video

# ======== Generate distribution graphs
def graph_generate(datarate, downlink, filename_extension, pkt_interarrival, pkt_length):
	cnt = 0
	fig, host = prepare_graph()
	datarate = list(filter(None, datarate)) # remove empty entries
	#print(datarate)
	for i in [datarate, pkt_interarrival, pkt_length]:
		host[0, cnt] = histogram(numofbins[cnt], i, label_x[cnt], label_y, host[0, cnt]) # generate hist graphs
		cnt += 1
	return fig

# ======== Generate histogram plot
def histogram(bins, data, label_x, label_y, plot):
	plot.hist(
			data,
			bins = bins,
			color = 'steelblue',
			edgecolor = 'dimgrey',
			density = True,
			bottom = 0,
			align = 'left',
			label = legend,
			orientation = 'vertical')
	plot.set_xlabel(label_x)
	plot.set_ylabel(label_y)
	plot.locator_params(nbins = 5) # number of ticks in the graphs
	return plot

# ======== Application layer - Generate data based on the applications
def layer_application(buffer, downlink, i, uplink):
	if downlink:
		land_takeoff, pitch_roll, return_home, throttle_yaw = generate_data_downlink() # fetch data
		buffer = data_to_buffer_downlink(buffer, i, land_takeoff, pitch_roll, # send data to buffer
				return_home, throttle_yaw)
	else:
		batterystatus, camerastatus, imustatus, rotorstatus, video = generate_data_uplink() # fetch data
		buffer = data_to_buffer_uplink(batterystatus, buffer, camerastatus, i, # send data to buffer
				imustatus, rotorstatus, video)
	return buffer

# ======== Transport layer - Check the UDP buffer and generate packets
def layer_transport(buffer, datarate, downlink, firstrun, i, num_packets,
		pkt_interarrival, pkt_length, pkt_length_total, pkt_list, time_previous, uplink):
	if i % frequency_buffer == 0:
		first_loop = True
		j, k = 0, 0
		buffer_length = len(buffer)
		if downlink: 
			sleep_dl = np.random.exponential(0.2) * 0.01 + 0.015 # generate processing delay
			time.sleep(sleep_dl)
		while True:
			if (downlink and len(buffer) == 0) or (uplink and (j == math.ceil(buffer_length / pkt_length_maximum))): # buffer is emptied, exit the loop
				break
			delayProb = np.random.uniform(0, 1)
			
			#if buffer[len(buffer) - 1 - k] == 'l' and buffer[len(buffer) - 2 - k] != 'l': # generate packets based on one parameter - old method
			if (downlink and (buffer[len(buffer) - 1 - k] != buffer[len(buffer) - 2 - k])) or uplink: # generate packets per parameter - new method
				if not first_loop and ((downlink and delayProb > 0.95) or (uplink and delayProb > 0.8)): # probability for processing delay. Probability for dl and ul different to make the 2nd peak obvious on DL
					# time_sleep = 0 # np.random.exponential(0.2) * 0.05 # generate processing delay#time_sleep = np.random.uniform(0, frequency_buffer / 20) # generate processing delay for dl
					time_sleep = np.random.exponential(0.2) * 0.05 # generate processing delay for ul
					time.sleep(time_sleep)
				if not first_loop and (delayProb > 0.97):
					sleep_ul = np.random.exponential(1) * 0.01 + 0.025
					time.sleep(sleep_ul)

			#if downlink and buffer[len(buffer) - 1 - k] == 'l' and buffer[len(buffer) - 2 - k] != 'l': # generate packets based on one parameter - old method
			if downlink and (buffer[len(buffer) - 1 - k] != buffer[len(buffer) - 2 - k]): # generate downlink packets
				pkt = pkt_create(buffer[len(buffer) - 1 - k:]) # generate packet
				buffer = buffer[:len(buffer) - 1 - k] # remove packet from buffer
				datarate, firstrun, pkt, pkt_interarrival, pkt_length, pkt_length_total, pkt_list, time_previous = statistics_results(datarate, # generate stats
						firstrun, pkt, pkt_interarrival, pkt_length, pkt_length_total, pkt_list, time_previous)
				k = 0
			elif downlink and k == len(buffer): 
				pkt = pkt_create(buffer) # generate packet
				buffer = '' # remove packet from buffer
				datarate, firstrun, pkt, pkt_interarrival, pkt_length, pkt_length_total, pkt_list, time_previous = statistics_results(datarate, # generate stats
						firstrun, pkt, pkt_interarrival, pkt_length, pkt_length_total, pkt_list, time_previous)
				k = 0
			elif downlink: 
				k += 1
			elif uplink: # generate uplink packets
				if j == math.ceil(buffer_length / pkt_length_maximum) - 1: # last pkt
				 	pkt = pkt_create(buffer) # generate packet
				 	buffer = '' # buffer[:len(buffer) - 1 - pkt_length_maximum] # remove packet from buffer
				 	datarate, firstrun, pkt, pkt_interarrival, pkt_length, pkt_length_total, pkt_list, time_previous = statistics_results(datarate, # generate stats
				 			firstrun, pkt, pkt_interarrival, pkt_length, pkt_length_total, pkt_list, time_previous)
				else: 
					pkt = pkt_create(buffer[len(buffer) - 1 - pkt_length_maximum:]) # generate packet
					buffer = buffer[:len(buffer) - 1 - pkt_length_maximum] # remove packet from buffer
					datarate, firstrun, pkt, pkt_interarrival, pkt_length, pkt_length_total, pkt_list, time_previous = statistics_results(datarate, # generate stats
							firstrun, pkt, pkt_interarrival, pkt_length, pkt_length_total, pkt_list, time_previous)
				j += 1

			first_loop = False	
		sys.stdout.write("Number of generated packets = %d out of %d   \r" %(len(pkt_interarrival), num_packets))
		sys.stdout.flush()
	return buffer, datarate, firstrun, pkt_interarrival, pkt_length, pkt_length_total, pkt_list, time_previous

# ======== Main function
def main():
	buffer = ''
	pkt_list, pkt_interarrival, pkt_length, datarate = [], [], [], []
	i, time_previous, pkt_length_total, j = 0, 0, 0, 0
	args, filename_extension, title = parse_args()
	firstrun = True
	
	print("\nPacket generation begins on %s channel" %title)
	starttime = time.time()
	# main loop
	while True:
		buffer = layer_application(buffer, args.downlink, i, args.uplink) # run app layer
		buffer, datarate, firstrun, pkt_interarrival, pkt_length, pkt_length_total, pkt_list, time_previous = layer_transport( # run transport layer
				buffer, datarate, args.downlink, firstrun, i, int(args.n), pkt_interarrival, pkt_length, 
				pkt_length_total, pkt_list, time_previous, args.uplink)
		i += 1
		
		if len(pkt_interarrival) >= int(args.n): break # requested number of packets generated

	print("\nPacket generation is completed!\nGraph is being prepared, please hold on...")
	exectime = float(time.time()) - starttime
	print("Total execution time: %d s" %exectime)
	fig = graph_generate(datarate, args.downlink, filename_extension, pkt_interarrival, pkt_length) # generate graph
	save_output(datarate, fig, filename_extension, pkt_interarrival, pkt_length, pkt_list, title) # save all output files
	print("\n\nDone!")
	show_graph()

# ======== Parse user inputs
def parse_args():
	parser = argparse.ArgumentParser(description = "UAV Data Traffic Generator")

	parser.add_argument('-n',
						action = "store",
						help = "Number of packets to generate. 5000 is default",
						default = 5000,
						required = False)

	parser.add_argument('--uplink', '-u',
						action = "store_true",
						help = "Generate packets for uplink channel. Otherwise, downlink channel is default.",
						default = False,
						required = False)

	args = parser.parse_args()

	if not args.uplink:
		args.downlink = True
		filename_extension = '_downlink'
		title = 'Downlink'
	else:
		args.downlink = False
		filename_extension = '_uplink'
		title = 'Uplink'

	try:
		args.n = int(args.n)
	except ValueError:
		print("Your input for -n is not valid.\nPlease provide an integer.")
		sys.exit(0)

	return args, filename_extension, title

# ======== Create packet
def pkt_create(payload):
	pkt = IP() / UDP() / Raw(load = payload) # add IP & UDP layers to the payload
	pkt[IP].src = ip_source
	pkt[IP].dst = ip_destination
	pkt[UDP].sport = port_source 
	pkt[UDP].dport = port_destination
	return pkt

# ======== Prepare subplots
def prepare_graph(): 
	plt.rcParams.update(config_matplotlibrc.parameters) # fetch parameters from config_matplotlibrc.py
	fig, host = plt.subplots(
			1,  
			3,  
			figsize = figure_dimensions, 
			squeeze = False)
	return fig, host

# ======== Round up the input to the nearest base. Taken from: https://stackoverflow.com/questions/26454649/python-round-up-to-the-nearest-ten 
def round_up(x, base):
	return int(math.ceil(x / base)) * base

# ======== Save all output files
def save_output(datarate, fig, filename_extension, pkt_interarrival, pkt_length, pkt_list, title):
	save_graph(fig, filename_extension, title)
	save_packets(filename_extension, pkt_list)
	save_statistics(datarate, filename_extension, pkt_interarrival, pkt_length)

# ======== Save generated packets to a pcap file
def save_packets(filename_extension, pkt_list):
	wrpcap(outputfolder + os.sep + date + filename_extension + '.' + outputfile_packets_extension, pkt_list)

# ======== Save statistical results to a csv file
def save_statistics(datarate, filename_extension, pkt_interarrival, pkt_length):
	with open(outputfolder + os.sep + date + filename_extension + '.' + outputfile_statistics_extension, 'w') as outputfile: 
		outputfile.write("{}, {}, {}\n".format("Packet Inter-arrival (ms)", "Packet Length (bytes)", "Data Rate (kbps)"))
		for x in zip(pkt_interarrival, pkt_length, datarate):
			outputfile.write("{}, {}, {}\n".format(x[0], x[1], x[2]))

# ======== Save graph
def save_graph(fig, filename_extension, title):
	handles, labels = plt.gca().get_legend_handles_labels() # to avoid duplicate labels. Taken from: https://stackoverflow.com/questions/13588920/stop-matplotlib-repeating-labels-in-legend
	by_label = dict(zip(labels, handles))
	fig.legend(
			by_label.values(),
			by_label.keys(), 
			bbox_to_anchor = legend_location)
	fig.suptitle(title)
	fig.savefig(
			'%s' %outputfolder + os.sep + 
			'%s.%s' %(date + filename_extension, figure_format), 
			bbox_inches = 'tight', 
			format = figure_format)

# ======== Show graph
def show_graph():
	plt.show()

# ======== Statistics of the generated data - data rate, packet inter-arrival, packet length
def statistics_results(datarate, firstrun, pkt, pkt_interarrival, pkt_length, pkt_length_total, pkt_list, time_previous):
	time_difference = float(pkt.time - time_previous) * 1000 if time_previous != 0 else 0 # multiply by 1000 to convert into ms
	pkt_interarrival.append(float(time_difference))
	pkt_length.append(int(len(pkt)))
	if int(time_previous) != int(pkt.time): 
		if not firstrun: datarate.append(float(pkt_length_total * 8 / 1000)) # multiply by 8 to convert bytes to bits, divide by 1000 to convert into kbps
		if pkt_length_total != 0: firstrun = False # to skip the first second 
		pkt_length_total = 0
	else:
		datarate.append(float())
	pkt_length_total += len(pkt)	
	pkt_list.append(pkt) # list_pkt are the generated packets to be sent to the MAC layer for transmission
	time_previous = pkt.time
	return datarate, firstrun, pkt, pkt_interarrival, pkt_length, pkt_length_total, pkt_list, time_previous

main()