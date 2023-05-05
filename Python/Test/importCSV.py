import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import xarray as xr
from datetime import datetime
from scipy.fft import fft, fftfreq
from scipy.signal import find_peaks
import time

def inport(file, idex, head, col):
    df = pd.DataFrame(pd.read_csv(file, index_col=[idex] , header=head), 
                            columns = col)
    return df
specData = pd.DataFrame(pd.read_csv('~\miniconda3\envs\\testequ\RTSeval\Files\RTS_Array_Cells.csv',
                     index_col=[0] , header=0), columns = ['W/L', 'Type'])
fileLoc = 'C:\\Users\\jpew\\miniconda3\\envs\\testequ\\RTSeval\\Python\\Data\\rtsData\\zoomRTS\\rtsData2023_04_12-03_44_48_PM.csv'
picLoc = 'C:\\Users\\jpew\\miniconda3\\envs\\testequ\\RTSeval\\Python\\Data\\rtsData\\zoomRTS\\rtsData'
data = inport(fileLoc, 0 ,0, ['Vs','Ticks','W/L', 'Type'])

plt.figure(figsize=(12,8))
plt.subplot(1,2,1)
plt.xlabel('Time(sec)')
plt.ylabel('Vs')
plt.plot(data['Ticks'], data['Vs'])
plt.subplot(1,2,2)
plt.xlabel('Vs')
plt.ylabel('Count')
y, x, _ = plt.hist(data['Vs'], bins='auto')
peaks, _ = find_peaks(y,  prominence=100, distance=5)
print(peaks)
i_maxPeaks = peaks[np.argmax(y[peaks])]
xMax = x[peaks]
rtsAmplitude = np.round(xMax[1]-xMax[0], 6)
plt.suptitle('RTS Data')
plt.figtext(.5,.9,"Vg = 1.2 V, Vdd = 1.2 V, Ibias= 10e-6 A,"+
             "Sample Rate = 1 kHz,  RTS Amplitude = " + str(rtsAmplitude) +
               " V", ha='center',  fontsize = 10)
plt.savefig(picLoc + 'Orig.png')
plt.show(block=False)
plt.pause(3)
plt.close()
j=1
for i in range(0,14,j):
    l = i+j
    i1 = i *1000
    i2 = i1 + (j*1000)
    rts=data.iloc[i1:i2, :]
    plt.figure(figsize=(12,8))
    plt.subplot(1,2,1)
    plt.xlabel('Time(sec)')
    plt.ylabel('Vs')
    plt.plot(rts['Ticks'], rts['Vs'])
    plt.subplot(1,2,2)
    plt.xlabel('Vs')
    plt.ylabel('Count')
    plt.hist(rts['Vs'])
    plt.suptitle('RTS Data')
    plt.figtext(.5,.9,"Vg = 1.2 V, Vdd = 1.2 V, Ibias= 10e-6 A, Sample Rate = 1 kHz", ha='center',  fontsize = 10)
    plt.savefig(picLoc +str(i)+'Sec_to_'+str(l)+'Sec'+ '.png')
    plt.show(block=False)
    plt.close()
