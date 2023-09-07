from keithleyDriver import Keithley2600
import numpy as np
import math
import time
import pandas as pd
from datetime import datetime
from os import system, name
import serial
import matplotlib.pyplot as plt
import re
import pywt
from scipy.signal import find_peaks, find_peaks_cwt, savgol_filter, gaussian, convolve
from scipy.signal import argrelmax, stft
from scipy.fft import fft

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
        if  np.abs(data[i] - previous_avg) >= threshold: # and shift_indices[shiftI] != [x for x in [notIncluded]]:
            shift_indices.append(i)

    for j in range(len(shift_indices)):
        if shift_indices[j] >= shift_indices[j-1]+20: # and shift_indices[j] != shift_indices[j-1]+2 and shift_indices[j] != shift_indices[j-1]+3 and shift_indices[j] != shift_indices[j-1]+4 and shift_indices[j] != shift_indices[j-1]+5 and shift_indices[j] != shift_indices[j-1]+6 and shift_indices[j] != shift_indices[j-1]+7 and shift_indices[j] != shift_indices[j-1]+8 and shift_indices[j] != shift_indices[j-1]+9 and shift_indices[j] != shift_indices[j-1]+10: #-  [x for x in list([0,1,2,3,4])]
            indices.append(shift_indices[j])
            # print(indices)

    return indices

fileLoc = "~\\skywaterTemp\\"
data = inport(fileLoc + 'RTS_B0_1uA1.feather')
grouped = data.groupby(data.Column)

for j in range(14,21):
    for i in range(1,22):

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
        # plt.plot(data2.Ticks, sig)
        # plt.title(str(i))
        # plt.show(block=True)
#         # avg = rolling_average(data2.Vgs, 5)
        y1,x1 = np.histogram(sig, bins=50)
        peaks = find_peaks(y1, width=1, height=100)
        xmax = x1[peaks[0]]
        ymax = y1[peaks[0]]

        
#         # if rts is detected by a two or more order gaussian step into this block
        
        if len(peaks[0]) >= 2:
            for k in range(0, len(peaks[0])):
                if y1[peaks[0][k]] == max(ymax):
                    # print(max(ymax))
                    steadyS = k
            amplitude = x1[peaks[0]] - x1[peaks[0][steadyS]]        # find the rts amplitude for all rts levels
            amplitude = amplitude[amplitude != 0.]                  # exlude the steadystate rts amplitude
            # print(amplitude)
            if np.abs(min(amplitude)) >= 0.0002:
                certainty = 4
            elif np.abs(min(amplitude)) < 0.0002:
                certainty = 3

            # certainty = 3
#             print(xmax[steadyS])
#             diff = (np.diff(sig))
#             threshold = (min(abs(amplitude))*.9)
#             amplitude_shifts = check_amplitude_shift(sig, size=51, threshold=threshold)
#             plt.figure(figsize=(12,8))            
#             plt.figtext(.5, .95, "Vg = 1.2 V, Vdd = 1.2 V, Samp Rate = " + str('2k') + " kHz, Ibias = " + str('1uA') +
#                          ' A, Rts Amplitude = ' + str(amplitude) + ' (V)', horizontalalignment='center', fontsize = 10)
#             plt.subplot(2,1,1)
#             vgs = data2.Vgs
#             ticks = data2.Ticks
#             plt.plot(data2.Ticks, data2.Vgs, '-')
#             plt.plot(data2.Ticks, sig)
#             plt.plot(ticks[amplitude_shifts], sig[amplitude_shifts], 'o')
#             plt.subplot(2,1,2)
#             plt.hist(data2.Vgs, bins=50)
#             plt.hist(sig, bins=50)
#             plt.plot(xmax, ymax, 'o')
#             plt.show(block=True)
#             plt.pause(3)
#             plt.close('all')

#         print(rowRX)

# import numpy as np
            # import matplotlib.pyplot as plt
            slopeSig1 = (np.gradient(sig, data2.Ticks, edge_order=1))
            slopeSig = savgol_filter(slopeSig1, window_length=10, polyorder=2)
            slopeSigN1 = (np.gradient(-sig, data2.Ticks, edge_order=1))
            slopeSigN = savgol_filter(slopeSigN1, window_length=10, polyorder=2)
            # edges = find_peaks(slopeSig, height=np.abs(max(slopeSig/2)), distance = 13)
            # edgesF = find_peaks(slopeSigN, height=np.abs(max(slopeSig/2)), distance = 13)
            std = np.std(slopeSig)
            mean = np.mean(slopeSig)
            sigma=mean+std*certainty
            sigmaN=mean-std*certainty
            edges = find_peaks(slopeSig, height=sigma, width = 3)
            # edges = np.where((sig[edges[0]])> np.mean(sig) + min(amplitude)*.5)
            # print(edges)
            edgesF = find_peaks(slopeSigN, height=np.abs(sigmaN), width = 3)
            wavelet_name = 'db4'  # Choose the desired wavelet
            coeffs = pywt.wavedec(sig, wavelet_name, level=5)  # Perform wavelet decomposition
            # print(coeffs)
            level = 4  # Choose the desired level for detecting edges
            detail_coeffs = coeffs[level]
            threshold = np.abs(min(amplitude)*.9)  # Set the threshold for edge detection

            rising_edges = np.where(np.abs(detail_coeffs) > threshold)[0]
            # Plot the signal, slope, and halfway points
            # plt.subplot(3, 1, 1)
            
# Compute STFT
            # frequencies, times, Z = stft(sig, fs=2000.0, nperseg=100, noverlap=80)
            fft_result = np.fft.fft(slopeSig)
            tim = data2.Ticks[1]-data2.Ticks[0]
            # print(fft_result)
            # Frequency values corresponding to FFT coefficients
            freq = np.fft.fftfreq(len(sig), d=tim)
            # print(freq)
            # Plot the spectrogram

            plt.figure(figsize=(12,8))
            plt.subplot(3, 1, 1)
            plt.plot(data2.Ticks, sig, label='Vgs')
            plt.plot(data2.Ticks[edges[0]], sig[edges[0]], 'x', color='red')
            plt.plot(data2.Ticks[edgesF[0]], sig[edgesF[0]], 'x', color='green')
            plt.xlabel('Time (s)')
            plt.ylabel('Amplitude')
            plt.title('Vgs of row ' + str(j) + ' col '+ str(i) + 'RTS Amplitude = '+ str(min(amplitude)))

            plt.subplot(3, 1, 2)
            
            y2,x2 = np.histogram(slopeSig, bins=50)
            peaks2 = find_peaks(y2, width=1, height=100)
            print(y2[peaks2[0]])
            xmax2 = x2[peaks2[0]]
            ymax2 = (y2[peaks2[0]])
            # if peaks2 >= 2:

            plt.hist(slopeSig, bins=50)
            plt.plot(xmax2, ymax2 , 'o')
            # # plt.pcolormesh(times, frequencies, np.abs(Z), shading='auto')
            # # plt.colorbar(label='Magnitude')
            # plt.plot(freq, np.abs(fft_result))
            # plt.xlabel('Frequency')
            # plt.ylabel('Magnitude')
            # plt.title('FFT Spectrum')
            # plt.xlabel('Time')
            # plt.ylabel('Frequency')
            # plt.title('STFT Spectrogram')
            # plt.hist(sig, bins=50)
            # plt.plot(data2.Ticks, -sig)
            # plt.xlabel('Time (s)')
            # plt.ylabel('Amplitude')
            # plt.title('Negative Noisy Signal')
            plt.subplot(3, 1, 3)
            # plt.subplot(2, 1, 2)
            plt.plot(data2.Ticks, slopeSig1)
            plt.plot(data2.Ticks, slopeSig)

            plt.plot(data2.Ticks[edges[0]], slopeSig[edges[0]],
                        'x', color='red')
            plt.plot(data2.Ticks[edgesF[0]], slopeSig[edgesF[0]], 'x',
                        color='green')
            plt.plot(data2.Ticks, np.ones_like(data2.Ticks)*sigma)
            plt.plot(data2.Ticks, np.ones_like(data2.Ticks)*sigmaN)
            plt.xlabel('Time (s)')
            plt.ylabel('Slope')
            plt.title('Slope of the Signal')

            plt.legend()
            plt.tight_layout()
            plt.show()
