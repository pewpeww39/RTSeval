import numpy as np
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt
import pandas as pd


def inport(file, idex, head, col):
    df = pd.DataFrame(pd.read_csv(file, index_col=[idex] , header=head), 
                            columns = col)
    return df

fileLoc = 'C:\\Users\\jpew\\miniconda3\\envs\\testequ\\RTSeval\\Python\\Data\\rtsData\\zoomRTS\\rtsData2023_04_12-03_44_48_PM.csv'

# Define the function to fit to the random telegraph signal
def rtw_signal(t, tau1, tau2, A1, A2):
    return A1 + (A2 - A1) * np.exp(-(t / tau1)) * np.cos(2 * np.pi * t / tau2)

def step_function(t, A, t0):
    return A * np.abs(t > t0)
data = inport(fileLoc, 0 ,0, ['Vs','Ticks','W/L', 'Type'])
# Generate some example random telegraph signal data
# t = np.linspace(0, 10, 100)
t = data['Ticks']
tau_true = 2.5
A1_true = 0.0
A2_true = 1.0
# y = rtw_signal(t, tau_true, A1_true, A2_true)
thres=np.mean(data['Vs']) - 0.0002
# Find the indices of the steps in the data
step_indices = np.where(np.diff(np.sign(data['Vs']- thres)))[0]
plt.plot(data['Ticks'], data['Vs'])
plt.plot(data['Ticks'][step_indices], data['Vs'][step_indices])
plt.show(block=False)
plt.pause(1)
plt.close()
j=1
for i in range(0,14,j):
    l = i+j
    i1 = i *1000
    i2 = i1 + (j*1000)
    rts=data.iloc[i1:i2, :]
    # print(rts)
    plt.figure(figsize=(12,8))
    plt.subplot(1,2,1)
    plt.xlabel('Time(sec)')
    plt.ylabel('Vs')
    plt.step(rts['Ticks'], rts['Vs'])
    avg = np.mean(rts['Vs'])
    thres=np.mean(rts['Vs']) - 0.0002
    AVG = np.sign(rts['Vs'] - thres)
    diff = np.diff(AVG)
    step_indices = np.where(diff)[0]
    change = np.abs(AVG) > 0.0002
    print(diff)
    # step_indices = np.where(change)[0]

    if i > 0:
        step_indices=step_indices+i1
    # print(step_indices)
    plt.plot(rts['Ticks'][step_indices], rts['Vs'][step_indices], 'ro', label='Steps')
    plt.subplot(1,2,2)
    plt.xlabel('Vs')
    plt.ylabel('Count')
    plt.hist(rts['Vs'])
    plt.suptitle('RTS Data')
    plt.figtext(.5,.9,"Vg = 1.2 V, Vdd = 1.2 V, Ibias= 10e-6 A, Sample Rate = 1 kHz", ha='center',  fontsize = 10)
    # plt.savefig(picLoc +str(i)+'Sec_to_'+str(l)+'Sec'+ '.png')
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
