import numpy as np
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt
import pandas as pd
from scipy.signal import find_peaks, argrelmax, peak_widths, peak_prominences, argrelextrema, savgol_filter
from scipy.ndimage import gaussian_filter1d
def inport(file, idex, head, col):
    df = pd.DataFrame(pd.read_csv(file, index_col=[idex] , header=head),
                            columns = col)
    return df
specData = pd.DataFrame(pd.read_csv('~\miniconda3\envs\\testequ\RTSeval\Files\RTS_Array_Cells.csv',
                     index_col=[0] , header=0), columns = ['W/L', 'Type'])
fileLoc = 'C:\\Users\\jpew\\miniconda3\\envs\\testequ\\RTSeval\\Python\\Data\\rtsData\\zoomRTS2\\rtsData_Loop1.csv'
picLoc = 'C:\\Users\\jpew\\miniconda3\\envs\\testequ\\RTSeval\\Python\\Data\\rtsData\\zoomRTS2\\rtsData'
data1 = inport(fileLoc, 0 ,0, ['Vs','Ticks', 'Column','Row','W/L', 'Type'])
columns = data1.groupby(data1.Column)
colGet = columns.get_group(54)
dataG = colGet.groupby(colGet.Row, as_index=False)
data = dataG.get_group(3).reset_index()
data['Vgs'] = np.full_like(data['Vs'], 1.2) - data['Vs']
plt.figure(figsize=(12,8))
plt.subplot(1,2,1)
plt.xlabel('Time(sec)')
plt.ylabel('Vgs')
plt.plot(data.Ticks, data.Vgs,label='Vgs')
plt.subplot(1,2,2)
plt.xlabel('Vgs')
plt.ylabel('Count')
y, x, _ = plt.hist(data['Vgs'], bins='auto')
peaks = (argrelmax(y,  order=5))
xMax = x[peaks]
yMax = y[peaks]
print(yMax)
rtsAmplitude = np.round(xMax[1]-xMax[0], 6)
plt.plot(xMax,yMax, 'x')
plt.suptitle('RTS Data')
plt.figtext(.5,.9,"Vg = 1.2 V, Vdd = 1.2 V, Ibias= 10e-6 A,"+
             "Sample Rate = 1 kHz,  RTS Amplitude = " + str(rtsAmplitude) +
               " V", ha='center',  fontsize = 10)
plt.savefig(picLoc + 'Orig.png')
plt.show(block=True)
plt.pause(3)
plt.close()
j=2
for i in range(0,14,j):
    l = i+j
    i1 = i *1000
    i2 = i1 + (j*1000)
    rts=data.iloc[i1:i2, :]
    # print(rts)
    plt.figure(figsize=(12,8))
    # plt.subplot(1,2,1)
    plt.xlabel('Time(sec)')
    plt.ylabel('Vgs')
    plt.step(rts['Ticks'], rts['Vgs'])
    avg = np.mean(rts['Vgs'])
    thres = avg + 0.0002
    AVG = np.sign(rts['Vgs'] - thres)
    diff = np.diff(AVG)
    step_indices = np.where(diff)[0]
    change = np.abs(AVG) > 0.0002
    print(step_indices)
    # step_indices = np.where(change)[0]
    if i > 0:
        step_indices=step_indices+i1
    # print(step_indices)
    # plt.plot(rts['Ticks'][step_indices], rts['Vgs'][step_indices], 'ro', label='Steps')
    # plt.subplot(1,2,2)
    # plt.xlabel('Vs')
    # plt.ylabel('Count')
    # plt.hist(rts['Vs'])
    # plt.suptitle('RTS Data')
    plt.figtext(.5,.9,"Vg = 1.2 V, Vdd = 1.2 V, Ibias= 10e-6 A, Sample Rate = 1 kHz, RTS Amplitude = " +
                 str(rtsAmplitude) +" V", ha='center',  fontsize = 10)
    plt.savefig(picLoc +str(i)+'Sec_to_'+str(l)+'Sec'+ '.png')
    plt.show(block=False)
    plt.pause(3)
    plt.close()
# plt.pause(3)
# plt.close()
# p0=[np.mean(data['Vs']), 0.00025]
# # Fit the function to the data to extract the time constant
# popt, pcov = curve_fit(step_function, t, data['Vs'], p0=p0)
# A1_fit, A2_fit = popt
# plt.plot(popt)
# plt.show()
# print("True tau: ", tau_true)
# print("Fit tau: ", tau1_fit)
# print("Fit tau: ", tau2_fit)