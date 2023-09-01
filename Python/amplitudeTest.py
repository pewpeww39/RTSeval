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
from scipy.signal import find_peaks, find_peaks_cwt, savgol_filter, gaussian, convolve
from scipy.signal import argrelmax
# from scipy import signal

def inport(fileLoc):
    data = pd.DataFrame(pd.read_feather(fileLoc))
    return data
def rolling_average(signal, window_size):
    window = np.ones(window_size) / window_size
    return np.convolve(signal, window, mode='valid')
def check_amplitude_shift(data, size, threshold):
    # Initialize an empty list to store amplitude shift indices
    shift_indices = [0]
    indices=[]
    shiftI = 0
    # Iterate over the data starting from the 6th element
    for i in range(size, len(data)):
        # Calculate the average of the previous 5 data points
        previous_avg = np.mean(data[i-size:i])

        # Check if the current data point deviates significantly from the average
        # if np.abs(np.diff(data) - previous_avg) >= threshold:
        # notIncluded = [i - x for x in list([0,1,2,3,4])]
        # print(notIncluded)
        if  np.abs(data[i] - previous_avg) >= threshold: # and shift_indices[shiftI] != [x for x in [notIncluded]]:
            shift_indices.append(i)
            # shiftI += 1
            # print(list(range(shiftI))[shiftI-4:])

            # print(shift_indices)

    for j in range(len(shift_indices)):
        if shift_indices[j] >= shift_indices[j-1]+20: # and shift_indices[j] != shift_indices[j-1]+2 and shift_indices[j] != shift_indices[j-1]+3 and shift_indices[j] != shift_indices[j-1]+4 and shift_indices[j] != shift_indices[j-1]+5 and shift_indices[j] != shift_indices[j-1]+6 and shift_indices[j] != shift_indices[j-1]+7 and shift_indices[j] != shift_indices[j-1]+8 and shift_indices[j] != shift_indices[j-1]+9 and shift_indices[j] != shift_indices[j-1]+10: #-  [x for x in list([0,1,2,3,4])]
            indices.append(shift_indices[j])
            # print(indices)

    return indices


fileLoc = "~\\skywaterTemp\\"

data = inport(fileLoc + 'RTS_B0_1uA1.feather')
# data = inport(fileLoc+'feather\\RTS_B0_10nA.feather')
# print(data.Column)
grouped = data.groupby(data.Column)
# print(grouped.get_group(str(1)))
for j in range(13,18):
    for i in range(1,33):

        rowRX = re.sub(r'[0-9]+$',
                        lambda x: f"{str(int(x.group())-1).zfill(len(x.group()))}",    # decrements the number in the row number
                        str(j))  
        colRX = re.sub(r'[0-9]+$',
                        lambda x: f"{str(int(x.group())-1).zfill(len(x.group()))}",    # decrements the number in the row number
                        str(i))  
        data1 = grouped.get_group(str(colRX))
        group = data1.groupby(data.Row)
        data2 = group.get_group(str(rowRX)).reset_index(drop=True)
        y,x = np.histogram(data2.Vgs, bins=50)
        peak = find_peaks(y, distance=5, width=1, height=100)
        XMAX = x[peak[0]]
        YMAX = y[peak[0]]
        size = 11
        sig = savgol_filter(data2.Vgs, window_length=size, polyorder=3)
        # avg = rolling_average(data2.Vgs, 5)
        y1,x1 = np.histogram(sig, bins=50)
        peaks = find_peaks(y1, width=1, height=100)
        xmax = x1[peaks[0]]
        ymax = y1[peaks[0]]
        if len(peaks[0]) >= 2:
            for k in range(0, len(peaks[0])):
                if y1[peaks[0][k]] == max(ymax):
                    print(max(ymax))
                    steadyS = k
            amplitude = x1[peaks[0]] - x1[peaks[0][steadyS]]
            amplitude = amplitude[amplitude != 0.]
            print(amplitude)
            print(xmax[steadyS])
            # rts = find_peaks(sig, height=np.mean(data2.Vgs), prominence=min(rtsAmplitude)*.8)
            diff = (np.diff(sig))
            # print(*diff, sep = "\n")
            # threshold= xmax[steadyS] + min(rtsAmplitude)*.5
            threshold = (min(abs(amplitude))*.9)
            # print(*diff)
            # dat = diff >= threshold 
            # print(dat)
            # convo = convolve(diff, np.array([1, 0, -1]), mode = 'same')
            # rts = np.where(convo >= threshold)[0]
            amplitude_shifts = check_amplitude_shift(sig, size=51, threshold=threshold)
            # print(amplitude_shifts)
            # ampShift = np.where(np.diff(sig[amplitude_shifts])>1)
            # print(amplitude_shifts)
            # transitions = sig[amplitude_shifts]
            # print(transitions)
            # indices = []
            # for j in range(len(transitions)):
            #     if transitions[j] - transitions[j-1] >= .9*min(abs(amplitude)): # and shift_indices[j] != shift_indices[j-1]+2 and shift_indices[j] != shift_indices[j-1]+3 and shift_indices[j] != shift_indices[j-1]+4 and shift_indices[j] != shift_indices[j-1]+5 and shift_indices[j] != shift_indices[j-1]+6 and shift_indices[j] != shift_indices[j-1]+7 and shift_indices[j] != shift_indices[j-1]+8 and shift_indices[j] != shift_indices[j-1]+9 and shift_indices[j] != shift_indices[j-1]+10: #-  [x for x in list([0,1,2,3,4])]
            #         indices.append(transitions[j])
                    # print(indices)
            # indices = sig[sig == indices]
            # print(indices[0])
            # kernel_size = 5
            # sigma = 1
            # kernel = np.exp(-np.arange(-(kernel_size//2), kernel_size//2 + 1)**2 / (2*sigma**2))
            # kernel = kernel / np.sum(kernel)
            # filtered = convolve(dat, kernel, mode='same')

            # Compute first derivative and threshold
            # dx = np.diff(filtered)
            # dx = np.insert(dx, 0, 0)
            # print(*dx)
            # threshold = 0.2 * np.max(dx)
            # print(*convo)
            # dif = np.where(np.diff(rts) >= abs(min(amplitude)*.8))
            # print(rts)
            # edges = np.where(np.diff(sig[rts]) >= abs(min(amplitude)*.8))
            # print(*edges)
            # print(sig[edges[0]])
            # Find rising edges
            # rising_edges = np.where()[0] # dat is True)[0]
            # print(rts)
            # print(len(dx[:-1]))


            # print(rts[0])
            # rtsN = find_peaks(-data2.Vgs, height=np.mean(-data2.Vgs))
            plt.figure(figsize=(12,8))            
            plt.figtext(.5, .95, "Vg = 1.2 V, Vdd = 1.2 V, Samp Rate = " + str('2k') + " kHz, Ibias = " + str('1uA') +
                         ' A, Rts Amplitude = ' + str(amplitude) + ' (V)', horizontalalignment='center', fontsize = 10)
            plt.subplot(2,1,1)
            vgs = data2.Vgs
            ticks = data2.Ticks
            plt.plot(data2.Ticks, data2.Vgs, '-')
            plt.plot(data2.Ticks, sig)
            plt.plot(ticks[amplitude_shifts], sig[amplitude_shifts], 'o')
            # plt.subplot(3,1,2)
            # # plt.plot(ticks[rtsN[0]], -vgs[rtsN[0]], 'x')
            # plt.plot(data2.Ticks, -data2.Vgs)
            plt.subplot(2,1,2)
            plt.hist(data2.Vgs, bins=50)
            plt.hist(sig, bins=50)
            plt.plot(xmax, ymax, 'o')
            plt.show(block=True)
            plt.pause(3)
            plt.close('all')

        # else:
            # plt.subplot(2,1,1)
            # vgs = data2.Vgs
            # ticks = data2.Ticks
            # plt.plot(data2.Ticks, data2.Vgs, '-')
            # plt.plot(data2.Ticks, sig)
            # # plt.plot(ticks[rts], sig[rts], 'o')
            # # plt.subplot(3,1,2)
            # # # plt.plot(ticks[rtsN[0]], -vgs[rtsN[0]], 'x')
            # # plt.plot(data2.Ticks, -data2.Vgs)
            # plt.subplot(2,1,2)
            # plt.hist(data2.Vgs, bins=50)
            # plt.hist(sig, bins=50)
            # # plt.plot(xmax, ymax, 'o')
            # plt.show(block=True)
            # plt.pause(3)
            # plt.close('all')
        print(rowRX)