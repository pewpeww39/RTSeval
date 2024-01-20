# from keithleyDriver import Keithley2600
import numpy as np
import math
import time
import pandas as pd
from datetime import datetime
from os import system, name
import serial
import matplotlib.pyplot as plt
import re
# import pywt
from scipy.signal import find_peaks, find_peaks_cwt, savgol_filter, gaussian, convolve
from scipy.signal import argrelmax, stft, peak_widths, welch, decimate, medfilt,detrend
from scipy.optimize import curve_fit
from pathlib import Path

p = Path.home()
debug = True

                                                    
def inport(fileLoc):
    data = pd.DataFrame(pd.read_feather(fileLoc))
    # data = pd.DataFrame(pd.read_csv(fileLoc))                                      # import function to pull in .feather files (binary)
    return data

fileLoc = str(p) + "\\skywaterTemp\\"
data = inport(fileLoc + 'rtsEval45.feather')
# data = inport(fileLoc + 'rtsEval.csv')
print(data.Column)
grouped = data.groupby(data.Column)                                                     # group the data by the column "Column"

columnRX = '44'
# columnRX = '36'

data1 = grouped.get_group(columnRX)                                           # gets the group with the specified column number
group = data1.groupby(data.Row)                                                 # group the data with the specified col # by column "Row"
vOut = group.get_group('1').reset_index(drop=True)                      # get the group with the spcified row number

print(vOut)

y,x = np.histogram(vOut['V_C Out'], bins=50)                                          # make a histogram of the signal selected by grouping
peak = find_peaks(y, distance=5, width=1, height=100)                           # find the peaks of the histogram
XMAX = x[peak[0]]                                                               # find the X values of the peaks in histogram 
YMAX = y[peak[0]]                                                               # find the Y values of the peaks in histogram
size = 100                                                                       # window size of savgol_filter
sig = savgol_filter(vOut['V_C Out'], window_length=size, polyorder=4)                 # filter the signal to reduce noise
y1,x1 = np.histogram(sig, bins=50)                                              # make a histogram of filtered signal
peaks = find_peaks(y1, width=1, height=100)                                     # find the peaks
xmax = x1[peaks[0]]                                                             # find X values of peaks in hist
ymax = y1[peaks[0]]                                                             # find Y values of peaks in hist

# if len(peaks[0]) >= 2:                                                          # determine if there is RTS by number of peaks in hist
for k in range(0, len(peaks[0])):
    if y1[peaks[0][k]] == max(ymax):                                        # find the steadystate value of filtered signal
        # print(max(ymax))
        steadyS = k
amplitude = x1[peaks[0]] - x1[peaks[0][0]]                           # find the rts amplitude for all rts levels
amplitude = amplitude[amplitude != 0.]                                      # don't include zero

certainty   = 11

slopeSig1   = (np.gradient(sig, vOut.Ticks, edge_order=2))
slopeSig    = savgol_filter(slopeSig1, window_length=100, polyorder=3)
slopeSigN1  = (np.gradient(-sig, vOut.Ticks, edge_order=2))
slopeSigN   = savgol_filter(slopeSigN1, window_length=10, polyorder=2)

# wSize = 250
sig2 = medfilt(vOut['V_C Out'], kernel_size=1001)

tick2 = medfilt(vOut['Ticks'], kernel_size=1001)

# slopeSig2 = np.gradient(sig2, tick2, edge_order=2)

# print(len(sig2))
# slopeSig2   = (np.gradient(sig2, vOut.Ticks, edge_order=2))
# slopeSig2    = savgol_filter(slopeSig1, window_length=100, polyorder=3)
# vOut['sig']    = savgol_filter(slopeSig2, window_length=wSize, polyorder=3)
# vOut['std']    = vOut['sig'].rolling(wSize).std()
# vOut['mean']   = vOut['sig'].rolling(wSize).mean()
std         = np.std(slopeSig)
mean        = np.mean(slopeSig)
sigma       = mean+std*(certainty)
print(max(vOut['V_C Out']))
print(sigma, std, mean)
# sigmas       = np.mean(vOut['mean']) + np.std(vOut['std'])*certainty
sigmaN      = mean-std*certainty
edges       = find_peaks(slopeSig, height=sigma, width = 3)
edgesF      = find_peaks(slopeSigN, height=np.abs(sigmaN), width = 3)

threshold = np.mean(sig[edges[0]])

# critPoint   = find_peaks(sig2, height = threshold,
#              rel_height=.5, width = 30000, distance = 300)

print("edges: " + str(edges[0]))
# print("critPoint: " + str(critPoint[0]))
# for i in range(0, len(vOut.Ticks)):
# stdThres  = np.mean(sig[critPoint[0]])
# print(threshold)
vOut['thres'] = np.full_like(vOut['V_C Out'], threshold)
vOut['Integrate'] = np.full_like(vOut['V_C Out'], None)
vOut['SteadyState'] = np.full_like(vOut['V_C Out'], None)
# print(vOut.int)
# point = critPoint[0] -int(wSize/2)
# print(sig[critPoint[0]])
critPoint = []
if len(critPoint) ==1:
    vOut.Integrate = vOut['V_C Out'].iloc[point[0]:]
    vOut.SteadyState = vOut['V_C Out'].iloc[:point[0]]
elif len(critPoint) == 2:
    vOut.Integrate = vOut['V_C Out'].iloc[point[0]:point[1]]
    # vOut.SteadyState = np.full_like(vOut['V_C Out'].iloc[point[0]:point[1]], None)
    vOut.SteadyState = np.where(((sig < vOut['thres'])), vOut['V_C Out'], None)
else:
    # vOut.SteadyState = pd.concat([(vOut['V_C Out'].iloc[:point[0]]), (vOut['V_C Out'].iloc[point[1]:])], axis = 0, ignore_index=True)
    #  = ((vOut['V_C Out'].iloc[:point[0]]) & (vOut['V_C Out'].iloc[point[1]:])) 
    vOut.Integrate = np.where(sig2 > threshold, vOut['V_C Out'], None)
    vOut.SteadyState = np.where(((sig2 < threshold) & (vOut['Ticks'] < max(vOut['Ticks'])*.75)), vOut['V_C Out'], None)
# vOut.SteadyState = np.where(((sig < vOut['thres'])), vOut['V_C Out'], None)
    # vOut['int'] = 1
# vOut.int =  np.where(vOut.int == 1, vOut['V_C Out'], None)

# print(vOut.int)
# plt.figure(figsize=(12,8))
layout = [
    ["A", "A", "A"],
    ["B", "B", "C"],
    ["D", "D", "E"]
]
fig, axd = plt.subplot_mosaic(layout, figsize=(12,8))
print("Threshold: " + str(threshold))
# print("STD Threshold: " + str(stdThres))
# plt.subplot(3, 3, 1)
axd["A"].plot(vOut['Ticks'], vOut['Integrate'], label = "$V_{C}$ Out Integrate Mode", color='#B22222')
axd["A"].plot(vOut['Ticks'], vOut['SteadyState'], label = "$V_{C}$ Out Steady State", color='dimgrey')
axd["A"].plot(vOut['Ticks'], sig, label = "Filterd Signal", color='darkorange')
# axd["A"].plot(vOut['Ticks'][critPoint[0]-wSize/2], vOut['V_C Out'][critPoint[0]-wSize/2], 'x', color='black')
axd['A'].hlines(threshold, 0, max(vOut['Ticks']), color="darkgreen")
# axd['A'].hlines(stdThres, 0, max(vOut['Ticks']), color="black")
axd["A"].set_xlabel("Time (sec)")
axd["A"].set_ylabel("$V_{cout}$ [V]")
axd["A"].set_title("RTS Data: Col: " + str(columnRX) + " Row: " + str(0)) # spec[0]) + " " + str(spec[1]))

axd["A"].legend()

# plt.subplot(3,3,4)
dataTemp = pd.DataFrame(data=[], index=[], columns=[])
dataTemp['data'] = vOut['Integrate']
dataTemp['Ticks'] = vOut.Ticks
dataTemp['data'] = np.where(vOut['Ticks']>max(vOut['Ticks'])*.45, dataTemp.data, None)
dataTemp = dataTemp.dropna()
print('Lenth of Integrate: ' + str(len(dataTemp)))
filtI = savgol_filter(dataTemp.data, window_length=11, polyorder=3)


# axd["B"].plot(dataTemp["Ticks"], dataTemp['data'], color='#B22222')
# axd["B"].plot(dataTemp.Ticks, filtI, color='darkorange')# axd["B"].hlines(sigma, 0, max(vOut['Ticks']), color='darkgreen')
axd["B"].plot(tick2, sig2, color='darkgrey')# axd["B"].hlines(sigma, 0, max(vOut['Ticks']), color='darkgreen')
axd['B'].hlines(threshold, 0, max(tick2), color="darkgreen")
# print(critPoint[0])
# axd["B"].plot(vOut["Ticks"][critPoint[0]], sig2[critPoint[0]], 'x')
axd["B"].set_xlabel("Time (sec)")
axd["B"].set_ylabel("$V_{cout}$ [V] STD")
axd["B"].get_legend()
# axd["B"].plot(dataTemp['Ticks'], dataTemp['data'], label = "$V_{C}$ Out Integrate Mode", color='#B22222')
# axd["B"].plot(dataTemp['Ticks'], filtI, label = "Filtered Signal", color='darkorange')
# axd["B"].set_xlabel("Time (sec)")
# axd["B"].set_ylabel("$V_{cout}$ [V]")
# axd["B"].get_legend()

# plt.subplot(3,3,6) 
y1, x1 = np.histogram(filtI, bins=50)
peak = find_peaks(y1, width=1, height=100, distance=5)
YMAX = y1[peak[0]]
XMAX = x1[peak[0]]
axd["C"].hist(dataTemp['data'], label = "$V_{C}$ Out Integrate", histtype="stepfilled", bins=50, color='#B22222')
axd["C"].hist(filtI, label = 'Filtered Signal', histtype="stepfilled", bins=50, color='darkorange')
axd["C"].plot(XMAX, YMAX, 'o')
axd["C"].set_ylabel("Frequency")
axd["C"].set_xlabel("$V_{C}$ Out [V]")
axd["C"].set_title('RTS Amplitude = ' + "???" + ' (V)')
axd["C"].get_legend()

# plt.subplot(3,3,7)
dataTemp = pd.DataFrame(data=[], index=[], columns=[])
dataTemp['data'] = vOut['SteadyState']
dataTemp['Ticks'] = vOut.Ticks
# dataTemp = dataTemp.dropna()
dataTemp['data'] = np.where(dataTemp['Ticks'] > max(dataTemp['Ticks'])*.75, None, dataTemp['data'])

dataTemp = dataTemp.dropna()
filtI = savgol_filter(dataTemp.data, window_length=11, polyorder=3)
axd["D"].plot(dataTemp['Ticks'], dataTemp['data'], label = "$V_{C}$ Out Steady State", color='dimgrey')
axd["D"].plot(dataTemp['Ticks'], filtI, label = "Filtered Signal", color='darkorange')
axd["D"].set_xlabel("Time (sec)")
axd["D"].set_ylabel("$V_{cout}$ [V]")
axd["D"].get_legend()

# plt.subplot(3,3,9) 
y1, x1 = np.histogram(filtI, bins=50)
peak = find_peaks(y1, width=1, height=100, distance=5)
YMAX = y1[peak[0]]
XMAX = x1[peak[0]]
axd["E"].hist(dataTemp['data'], label = "$V_{C}$ Out Integrate", histtype="stepfilled", bins=50, color='dimgrey')
axd["E"].hist(filtI, label = 'Filtered Signal', histtype="stepfilled", bins=50, color='darkorange')
axd["E"].plot(XMAX, YMAX, 'o')
axd["E"].set_ylabel("Frequency")
axd["E"].set_xlabel("$V_{C}$ Out [V]")
axd["E"].set_title('RTS Amplitude = ' + "???" + ' (V)')
axd["E"].get_legend()
plt.tight_layout()
plt.show(block=True)
