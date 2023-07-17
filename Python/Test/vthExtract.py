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
fileLoc = 'C:\\Users\\jpew\\miniconda3\\envs\\testequ\\RTSeval\\Python\\Data\\idvgsCharacterization\\Bank 1\\idvgscharDataBAK1.csv'
picLoc = 'C:\\Users\\jpew\\miniconda3\\envs\\testequ\\RTSeval\\Python\\Data\\idvgsCharacterization\\Bank 2\\vthExtract'
data = inport(fileLoc, 0 ,0, ['Type', 'Vs', 'Vgs','Id','W/L', 'Gm', 'Row', 'Column'])
pltData = pd.DataFrame(data=[], index=[], columns=[])
group = data.groupby(data['Column'])
colData = group.get_group(1)
group1 = colData.groupby(colData['Row'])
pltData = group1.get_group(1)
print(pltData)
pltData.loc[:,'VgsSqrt'] = np.sqrt(pltData['Vgs'])
pltData['GmSqrt'] = pltData['Gm'] **(1/2)
maxVal = max(pltData['GmSqrt'])
print(maxVal)
vthData = pltData.groupby(pltData['GmSqrt'])
vthdata = vthData.get_group(maxVal)
print(vthdata)
maxVal1 = np.full_like(pltData.VgsSqrt, maxVal)
vth = (maxVal*vthdata.VgsSqrt-vthdata.Id)/maxVal
vthVal = np.full_like(pltData.VgsSqrt, vth)
vthLine = maxVal1*pltData.loc[:,'VgsSqrt'] - maxVal1*vthVal
print(vthLine)
plt.figure(figsize=(12,8))
plt.xlabel('Vgs^(1/2)')
plt.ylabel('Id')
plt.yscale('log')
plt.plot(pltData['VgsSqrt'], vthLine, label='vth')
plt.plot(pltData['Vgs'], pltData['Id'], label='Vgs')
plt.plot(pltData['VgsSqrt'], pltData['Id'], label='Vgs^(1/2)')
plt.legend()
# plt.subplot(1,2,2)
# plt.xlabel('Vs')
# plt.ylabel('Count')
# y, x, _ = plt.hist(data['Vs'], bins='auto')
# peaks, _ = find_peaks(y,  prominence=100, distance=5)
# print(peaks)
# i_maxPeaks = peaks[np.argmax(y[peaks])]
# xMax = x[peaks]
# rtsAmplitude = np.round(xMax[1]-xMax[0], 6)
# plt.suptitle('RTS Data')
# plt.figtext(.5,.9,"Vg = 1.2 V, Vdd = 1.2 V, Ibias= 10e-6 A,"+
#              "Sample Rate = 1 kHz,  RTS Amplitude = " + str(rtsAmplitude) +
#                " V", ha='center',  fontsize = 10)
# plt.savefig(picLoc + 'Orig.png')
plt.show(block=False)
plt.pause(3)
plt.close()
# j=1
# for i in range(0,14,j):
#     l = i+j
#     i1 = i *1000
#     i2 = i1 + (j*1000)
#     rts=data.iloc[i1:i2, :]
#     plt.figure(figsize=(12,8))
#     plt.subplot(1,2,1)
#     plt.xlabel('Time(sec)')
#     plt.ylabel('Vs')
#     plt.plot(rts['Ticks'], rts['Vs'])
#     plt.subplot(1,2,2)
#     plt.xlabel('Vs')
#     plt.ylabel('Count')
#     plt.hist(rts['Vs'])
#     plt.suptitle('RTS Data')
#     plt.figtext(.5,.9,"Vg = 1.2 V, Vdd = 1.2 V, Ibias= 10e-6 A, Sample Rate = 1 kHz", ha='center',  fontsize = 10)
#     plt.savefig(picLoc +str(i)+'Sec_to_'+str(l)+'Sec'+ '.png')
#     plt.show(block=False)
#     plt.close()
