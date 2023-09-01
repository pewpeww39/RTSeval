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
from scipy.signal import argrelmax, stft, peak_widths, welch, hilbert, argrelextrema
from scipy.signal.windows import gaussian
from scipy.optimize import curve_fit
from scipy.ndimage import gaussian_filter
import ruptures as rpt


debug = False
changepointDetection = False

def square_wave(x, a, b, p):
    level = np.random.choice([0, 1], size=len(x), p=[0.5 * (1 - p), 0.5 * (1 + p)])
    return a + b * level

def model_func(x, a, b, p):
    return square_wave(x, a, b, p)

                                                    
def inport(fileLoc):
    data = pd.DataFrame(pd.read_feather(fileLoc))                                      # import function to pull in .feather files (binary)
    return data

def two_state_model(t, A, tau1, tau2):
    return A * (np.exp(-t / tau1) - np.exp(-t / tau2))


fileLoc = "~\\skywaterTemp\\"
# data = inport(fileLoc + 'RTS_B2_100nA82.feather')
data = inport(fileLoc + 'RTS_B0_1uA1.feather')
grouped = data.groupby(data.Row)                                                     # group the data by the column "Column"

def rtsEval():
    # print(data)
    for j in range(2,21):
        for i in range(1,33):
            rollingD = pd.DataFrame(data=[],columns=['sig','stdev'], index=[])
            rowRX = re.sub(r'[0-9]+$',
                            lambda x: f"{str(int(x.group())-1).zfill(len(x.group()))}",    # decrements the number in the row number
                            str(j))  
            colRX = re.sub(r'[0-9]+$',
                            lambda x: f"{str(int(x.group())-1).zfill(len(x.group()))}",    # decrements the number in the col number
                            str(i))  
            data1 = grouped.get_group(str(rowRX)).reset_index(drop=True)                                           # gets the group with the specified column number
            group = data1.groupby(data.Column)                                                 # group the data with the specified col # by column "Row"
            data2 = group.get_group(str(colRX)).reset_index(drop=True)                      # get the group with the spcified row number
            y,x = np.histogram(data2.Vgs, bins='auto')                                          # make a histogram of the signal selected by grouping
            peak = find_peaks(y, distance=5, width=1, height=100)                           # find the peaks of the histogram
            XMAX = x[peak[0]]                                                               # find the X values of the peaks in histogram 
            YMAX = y[peak[0]]                                                               # find the Y values of the peaks in histogram
            size = 11                                                                       # window size of savgol_filter
            rollingD['sig'] = savgol_filter(data2.Vgs, window_length=10, polyorder=3)   
            # sig = savgol_filter(data2.Vgs, window_length=size, polyorder=3)                 # filter the signal to reduce noise
            y1,x1 = np.histogram(rollingD.sig, bins='auto')                                              # make a histogram of filtered signal
            peaks = find_peaks(y1, width=10, height=100)                                     # find the peaks
            mins = argrelextrema(y1, np.less)
            xmax = x1[peaks[0]]                                                             # find X values of peaks in hist
            ymax = y1[peaks[0]]                                                             # find Y values of peaks in hist
            xmin = x1[mins]
            # ymin = y1[mins].tolist()
            # print(xmax)
            # plt.hist(sig, bins=50)
            # if len(xmin) >=1:
            #     plt.axvline(np.mean(xmin))
            # plt.show(block=True) 
            if len(peaks[0]) >= 2:  
                print(xmin)
            
                # for mins in range(len(xmin)-1):
                #     if xmin[mins] < xmax[0] or xmin[mins] > xmax[len(xmax)-1]:
                #         xmin.remove(xmin[mins])
            
                amplitude = x1[peaks[0]] - x1[peaks[0][0]]
                # amplitude = x1[peaks[0]] - x1[peaks[0][steadyS]]                            # find the rts amplitude for all rts levels
                amplitude = amplitude[amplitude != 0.]                                      # don't include zero
                windowSize = 20
                wSize = 10
                rollingD['stdev'] = rollingD.sig.rolling(wSize).std()
                # stdRolling['rolling'] = data2.Vgs.rolling(20).std()
                meanRolling = data2.Vgs.rolling(wSize).mean()
                # threshold = x1[peaks[0][0]] + rollingD.stdev*np.ones_like(rollingD.stdev)*3
                #############################
                
                # xmin = xmin[xmin > xmax[0]]
                # xmin = xmin[xmin < xmax[len(xmax)-1]]
                # if len(xmin) >= 2:
                #     xmin = np.mean(xmin)
                #     print('Minimums: ', xmin)
                # else:
                # threshold = xmin
            # if len(trial) >= 2:
                    # Plot some stuff 

                plt.figure(figsize=(14,14))
                plt.subplot(3, 1, 1)
                # if debug is False:
                plt.plot(data2.Ticks, data2.Vgs, label='Vgs', color='gray')
                plt.plot(data2.Ticks, rollingD.sig, label='Filtered Vgs', color='red')
                # plt.plot(data2.Ticks[trial], sig[trial], 'x', color='blue')
                # plt.plot(data2.Ticks[level1[0]], sig[level1[0]], 'x', color='blue')
                # plt.plot(data2.Ticks[level2[0]], sig[level2[0]], 'x', color='green')
                # plt.plot(data2.Ticks[trial2], sig[trial2], 'x', color='green')
                # plt.xlabel('Time (s)')
                
                plt.ylabel('Amplitude')
                plt.title('Vgs of row ' + str(82) + ' col '+ str(colRX))
                
                plt.legend()


                plt.subplot(3,2,3)

                frq, P1d = welch(data2.Vgs, fs=2000, window='hann', nperseg=40000,               #  Compute PSD using welch method
                                    noverlap=None, nfft=40000, scaling='density')
                p1dSmooth = savgol_filter(P1d, window_length=5, polyorder=1)
                
                num_bins = 100  # Number of logarithmic bins
                log_bins = np.logspace(np.log10(frq[0]), np.log10(frq[-1]), num_bins)
                binned_psd, _ = np.histogram(frq, bins=log_bins, weights=P1d)
                binned_frequencies = (log_bins[:-1] + log_bins[1:]) / 2.0
                fit_func = lambda x, a, b: a * x + b
                # fit_params, _ = np.polyfit(np.log10(binned_frequencies), np.log10(binned_psd), deg=1)
                # slope = fit_params[0]
                # intercept = fit_params[1]
                # tim = np.arange(len(data2.Vgs))
                # # Perform the curve fitting
                # params, _ = curve_fit(two_state_model, tim, data2.Vgs, p0=[0, 1, 0])
                f1 = 2000/40000  # Frequency 1 (lower frequency)
                f2 = 2000/2  # Frequency 2 (higher frequency)

                # Set the initial guesses for tau1 and tau2
                tau1 = .1
                tau2 = 0.1

                # Set the convergence threshold for the iteration
                convergence_threshold = 1e-6

                # Iterate until convergence
                i = 0
                while True:
                    # Calculate the slope of the line on a log-log plot
                    i+=1
                    slope = (np.log10(P1d[frq == f2]) - np.log10(P1d[frq == f1])) / (np.log10(f2) - np.log10(f1))

                    # Update tau2 based on the current tau1
                    tau2_new = tau1 * (f2 / f1) ** slope

                    # Update tau1 based on the new tau2
                    tau1_new = tau2 / (f2 / f1) ** slope

                    # Check convergence
                    if (np.abs(tau1_new - tau1) < convergence_threshold and np.abs(tau2_new - tau2) < convergence_threshold) or i == 10000:
                        break

                    # Update tau1 and tau2 for the next iteration
                    tau1 = tau1_new
                    tau2 = tau2_new
                # tau1 = params[1]
                # tau2 = params[2]
                # tau2 = tau1 * (f2 / f1)**slope

                print(tau1)
                print(tau2)



                plt.yscale('log')
                plt.xscale('log')
                plt.plot(frq[5:], P1d[5:], color='gray')
                plt.plot(frq[5:], p1dSmooth[5:], color='red')
                plt.xlabel('Frequency')
                # plt.ylabel('PSD')
                plt.title('1/f Noise')

                plt.subplot(3, 2, 4)            
                plt.hist(data2.Vgs, bins='auto', color='gray')
                plt.hist(rollingD.sig, bins='auto', color='red')
                plt.plot(xmax, ymax, 'o')
                plt.title('Rts amplitude ' + str(amplitude))

                plt.subplot(3, 2, 5)
                # plt.hist(results_W/2000, bins=100, color='gray')
                # meanTauE = np.mean(results_W)/2000
                # plt.xlabel=("Time (Sec)")
                # plt.title('Mean emission time (Sec): ' + str(meanTauE))

                plt.subplot(3, 2, 6)
                # plt.hist((results_NW/2000), bins=100, color='gray')
                # meanTauC = np.mean(results_NW)/2000
                # plt.xlabel=("Time (Sec)")
                # plt.title('Mean capture time: ' + str(meanTauC))

                plt.tight_layout()
                # plt.show()
                if changepointDetection is False:
                    plt.show(block=False)
                else:
                    plt.show(block=False)
                plt.pause(3)
                plt.close()
                rollingD = rollingD.reset_index(drop=True, inplace=True)  

rtsEval()