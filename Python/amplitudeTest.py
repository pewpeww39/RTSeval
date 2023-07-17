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
from scipy.signal import find_peaks, find_peaks_cwt, savgol_filter
from scipy.signal import argrelmax
# from scipy import signal

def inport(fileLoc):
    data = pd.DataFrame(pd.read_feather(fileLoc))
    return data

fileLoc = "~\\skywaterTemp\\"

data = inport(fileLoc + 'RTS_B0_1uA1.feather')

# print(data.Column)
grouped = data.groupby(data.Column)
# print(grouped.get_group(str(1)))
for j in range(13,15):
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
        sig = savgol_filter(data2.Vgs, window_length=51, polyorder=3)
        y1,x1 = np.histogram(sig, bins=50)
        peaks = find_peaks(y1, distance=5, width=1, height=50)
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
            diff = (np.gradient(sig))
            print(*diff, sep = "\n")
            # threshold= xmax[steadyS] + min(rtsAmplitude)*.5
            threshold= (min(amplitude)*.8)
            dat = diff[0] >= threshold 
            rts = np.where(np.convolve(dat, [1, -1]) == -1)[0]
            print(threshold)

            # print(rts[0])
            rtsN = find_peaks(-data2.Vgs, height=np.mean(-data2.Vgs))
            plt.figure(figsize=(12,8))            
            plt.figtext(.5, .95, "Vg = 1.2 V, Vdd = 1.2 V, Samp Rate = " + str('2k') + " kHz, Ibias = " + str('1uA') +
                         ' A, Rts Amplitude = ' + str(amplitude) + ' (V)', horizontalalignment='center', fontsize = 10)
            plt.subplot(2,1,1)
            vgs = data2.Vgs
            ticks = data2.Ticks
            plt.plot(data2.Ticks, data2.Vgs)
            plt.plot(data2.Ticks, sig)
            plt.plot(ticks[rts], sig[rts], 'x')
            # plt.subplot(3,1,2)
            # # plt.plot(ticks[rtsN[0]], -vgs[rtsN[0]], 'x')
            # plt.plot(data2.Ticks, -data2.Vgs)
            plt.subplot(2,1,2)
            plt.hist(data2.Vgs, bins=50)
            plt.hist(sig, bins=50)
            plt.plot(xmax, ymax, 'o')
            plt.show(block=False)
            plt.pause(3)
            plt.close('all')
        print(rowRX)