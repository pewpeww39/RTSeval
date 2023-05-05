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
picLoc = "C:\\Users\\UTChattsat\\Documents\\SkywaterData\\idvgsCharacterization\\Bank 1\\gm_grouped"
fileLoc = '~\\Documents\\SkywaterData\\idvgsCharacterization\\Bank 1\\idvscharData2023_04_12-10_31_33_AM.csv'
data = inport(fileLoc, 0 ,0, ['Site', 'Type', 'Vs', 'Vgs', 'Id','W/L', 'Temp(K)', 'Die X', 'Die Y', 'Gm', 'Row', 'Column',])

data["IdSq"] = abs(data["Id"]**(1/2))
data["VgsSq"] = abs(data["Vgs"]**(1/2))
# plt.plot(data["Vgs"], data["IdSq"])
gData = data.groupby(data['Row'])
for i in range(5):  #len(gData)
    pltData = gData.get_group(i)
    # print(pltData)
    # plt.figure(figsize=(12,8))
# plt.subplot(1,2,1)
    # plt.plot(pltData["Vgs"], pltData["IdSq"])
    pltData["dGm"] = (pltData["Gm"].diff()/ pltData["Vgs"].diff())
    # pltData["dGm"] = np.gradient(pltData.Gm, pltData.Vgs)
    pltData['GmSqrt'] = (np.sqrt(pltData.Gm)) #max(pltData["dGm"])
    print(max(pltData['GmSqrt']))
    grouped = pltData.groupby(pltData['GmSqrt'])
    slope = max(pltData['GmSqrt']) 
    vthData1 = grouped.get_group(slope)
    slope1 = np.full_like(pltData['GmSqrt'], max(pltData['GmSqrt']))
    maxGm1 = max(np.gradient(pltData.Id, pltData.Vgs, edge_order=2)) **(1/2)
    print('maxGm 1 ' ,maxGm1)
    # pltData['Vth'] = vthData1.Vgs - vthData1.Gm / maxGm1
    vth =(vthData1['VgsSq'] * slope - vthData1["Id"]) / slope
    print(vthData1)
    print(vth)
    pltData['Vth'] = (pltData['Vgs'] * slope - ((pltData["Id"]))) / slope
    # maxVal = pltData[pltData["dIds"] == maxVal].index
    plt.plot(vth, 0, 'x', label='vth')
    plt.plot(pltData['VgsSq'], pltData['Vth'])
    plt.plot(pltData['VgsSq'], pltData['Id'])
    
    # plt.figtext(.5,.95,"Vth = " + str(vth[99]) , ha='center',  fontsize = 10)
    # plt.plot(pltData['Vth'], pltData["Vgs"], label='vth')
    plt.legend()
    # indexA =[pltData["dIds"] == maxVal].index
    # print(maxVal)
# pltData["dIds"].iloc[indexA]
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
# plt.title('Gm Characterization Across Column 0')
plt.title('Id vs Vgs^1/2')
plt.xlabel('Vgs^1/2')
plt.ylabel('Id')
# plt.ylim((0, 0.01))
# plt.xscale('log')
# plt.yscale('log')
plt.savefig(picLoc + '_Column0.png')
plt.show(block=False)
plt.pause(3)
plt.close()
j=1
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
