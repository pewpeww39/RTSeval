import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import xarray as xr
from datetime import datetime
from scipy.fft import fft, fftfreq



def inport(file, idex, head, col):
    df = pd.DataFrame(pd.read_csv(file, index_col=[idex] , header=head), 
                            columns = col)
    return df

def delta(yVal, xVal):
    dy = np.gradient(yVal)
    dx = np.gradient(xVal)
    delt = np.gradient(yVal, xVal)
    return delt, dy, dx

def vGS(vg, vs):
    vgs = (vg) - (vs)
    return vgs


def plotgm(file, colI, colV):
    specData = inport(fileLoc, 0, 0, ['Col000Vgs','Col000Id'])
    
    current = specData.iloc[0:46, 1]
    voltage = specData.iloc[0:46, 0] #vGS(1.2, specData.iloc[:,0])
    print(current)
    delt, dy, dx = delta(current, voltage)
    gm = dy/dx
    plt.plot(voltage, current, label='idVgs')
    plt.title('Id vs Vgs')
    plt.yscale('log')
    plt.ylabel("Current [A]")
    plt.xlabel("Voltage [V]")
    fig = plt.show(block = False)
    plt.pause(5)
    plt.close(fig)
    plt.plot(delt, voltage)
    # plt.plot(gm)
    plt.title('transconductance')
    plt.show(block = False)
    plt.pause(5)
    # plt.close('all')
    # plt.plot(1/gm)
    # plt.title('1/gm')
    # plt.show(block = False)
    # plt.pause(2)


fileLoc ="~\miniconda3\envs\\testequ\RTSeval\Python\Data\\idvgsCharacterization\\Bank 1\\idvgscharData2023_02_22-Bank1.csv"
picLoc ="C:\\Users\\UTChattsat\\miniconda3\\envs\\testequ\\RTSeval\\Python\\Data\\rtsData\\rtsTS "
plotgm(fileLoc, 2, 3)