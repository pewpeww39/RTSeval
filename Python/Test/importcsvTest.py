import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import xarray as xr
from datetime import datetime
from scipy.fft import fft, fftfreq
import time

dt_string = datetime.now().strftime("%Y_%m_%d-%I_%M_%S_%p")

### imports csv file, head = 0 for files with headers in col 0
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

# specData = pd.DataFrame(pd.read_csv('~\miniconda3\envs\\testequ\RTSeval\Python\Data\csCharacterization\cscharData2023_02_10-01_39_20_PM.csv',
#                      index_col=[0] , header=0), columns = ['Col001Vs', 'Col001Id', 'Col002Vs', 'Col002Id'])
# print(specData)
# C:\Users\jpew\miniconda3\envs\testequ\RTSeval\Python\Data\csCharacterization\cscharData2023_02_10-01_39_20_PM.csv
# fileLoc ="~\miniconda3\envs\\testequ\RTSeval\Python\Data\csCharacterization\cscharData2023_02_10-01_39_20_PM.csv"
# fileLoc ="~\miniconda3\envs\\testequ\RTSeval\Python\Data\\rtsData\\rtsLoopData.csv"
fileLoc = "~\miniconda3\envs\\testequ\RTSeval\Python\Data\\vdvgCharacterization\Bank 2\\vdvgcharDataBAK.csv"
# picLoc ="C:\\Users\\UTChattsat\\miniconda3\\envs\\testequ\\RTSeval\\Python\\Data\\rtsData\\rtsTS "
#specData = inport(fileLoc, 0, 0, ['Col001Vs','Col001Id'])
# spec = vGS(1.2, specData.columns[0])
def plotgm(file, colI, colV):
    specData = inport(fileLoc, 0, 0, ['Col001Vs','Col001Id'])
    current=specData.iloc[:,1]
    voltage = vGS(1.2, specData.iloc[:,0])
    delt, dy, dx = delta(current, voltage)
    gm = dy/dx
    plt.plot(current, voltage, label='idVgs')
    plt.title('Id vs Vgs')
    plt.yscale('log')
    fig = plt.show(block = False)
    plt.pause(1)
    plt.close(fig)
    plt.plot(delt)
    plt.plot(gm)
    plt.title('transconductance')
    plt.show(block = False)
    plt.pause(3)
    plt.close('all')
    plt.plot(1/gm)
    plt.title('1/gm')
    plt.show(block = False)
    plt.pause(5)

def plotrts(file, row):
    rtsData = inport(fileLoc, 0, 0, ['Row 1'])
    rtsData = rtsData.drop(range(0,4000))
    rtsData = rtsData.drop(range(5100,20001))
    # print(rtsData)
    plt.plot(rtsData['Row 1'], label='Vs')
    plt.title("RTS Data: Column 1")
    plt.figtext(.2, .15, "Vg = 1.2 V, Vdd = 1.2 V", fontsize = 10)
    plt.figtext(.2, .2, "Ibias = 1 nA, AmpBias = .5 mA", fontsize = 10)
    plt.figtext(.2, .25, "column = 1, row = " , fontsize = 10)
    plt.xlabel("Time [mSec]")
    plt.ylabel("Voltage [V]")
    plt.legend()
    plt.savefig(picLoc + dt_string + ".png")
    fig1 = plt.show(block = False)
    plt.pause(5)
    plt.close(fig1)
    plt.hist(rtsData['Row 1'], label = "Vs", bins=100)
    plt.title("RTS Data: Column 1")
    # plt.figtext(.2, .15, "Vg = 1.2 V, Vdd = 1.2 V", fontsize = 10)
    # plt.figtext(.2, .2, "Ibias = 1 nA, AmpBias = .5 mA", fontsize = 10)
    # plt.figtext(.2, .25, "column = 1, row = " , fontsize = 10)
    plt.ylabel("Time [Sec]")
    plt.xlabel("Voltage [V]")
    plt.legend()
    # plt.savefig(picLoc + " " + str(rowS) + dt_string + " " + " Hist.png")
    fig1 = plt.show(block = False)
    plt.pause(5)
    plt.close(fig1)
    # plt.close('all')
# plotgm(fileLoc, 1, 0)

def logScale(start, stop, power):
    powers = power
    decade = []
    for dec in range(abs(powers)):
        start = 10**(power-1)
        stop = 10** power
        inc = 10**(powers-dec)
        stop = 10**power
        for i in range(10):
            start = start+inc
            decade = np.append(decade, range(start, stop))
        power = power - 1
    return decade

def fourT (fileLoc):
    rtsData = inport(fileLoc, 0, 0, ['Row 1'])
    print(rtsData)
    N = 5000 * 3900
    y = fft(rtsData)
    x = fftfreq(N, 1/5000)

    return x, y


# def xarraytoDF(specData):
# data = specData/
# datax= specData['Col001Vs']
# dataY = specData['Col001Id']
# rowNm = range(95)
# for name in rowNm:
#     print(name)
# xarray_3d = xr.Dataset(
#     {"Col001": (("row", "mSec"), np.random.randn(2, 95))},
#     coords={
#         "row": [0, 1],
#         "mSec": rowNm, #["Q1", "Q2", "Q3", "Q4", "Q5"],
#         "Col002": ("row", np.random.randn(2)),
#         "Col003": 50,
#     },
# )
# plotgm(fileLoc,0, 1)
# plotrts(fileLoc, 0)
# x, y = fourT(fileLoc)
# print(y)
# plt.plot(x, np.abs(y))
# df_3d = xarray_3d.to_dataframe()

# df_3d.to_csv('~/miniconda3/envs/testequ/RTSeval/Python/Test/Data/tesData.csv')
# print(df_3d)
# for v in range(len(specData)):
#     spec = list(specData.iloc[v])
#     print(str(spec))

# ###### relist col types and w/L
# start = 0
# stop = 0
# incsv = "C:\\Users\\jacob\\Downloads\\idvgscharDataBAK1.csv"
# specData = pd.DataFrame(pd.read_csv('~\miniconda3\envs\\testequ\RTSeval\Files\RTS_Array_Cells.csv',
#                      index_col=[0] , header=0), columns = ['W/L', 'Type']) 
# data = pd.DataFrame(pd.read_csv(incsv, header=0))
# # print(data)
# typecounter = 0
# counter = 0
# counterb = 0
# print(specData.iloc[typecounter, 0])
# print(specData.iloc[1, 0])
# print(specData)
# for r in range(0,len(data)):
# # for r in range(2000):
#     # for i in range(0+start, 32+stop):
#     data.iat[r,6] = specData.iat[typecounter, 0]
#     data.iat[r,2] = specData.iat[typecounter, 1]
#     counterb = counterb + 1
#     counter = counter + 1
#     # print(data.iat[typecounter, 5])
#     if counterb >= 50:
#         # print(typecounter)
#         # print(specData.iat[typecounter, 0])
#         print(data.iat[r,2] + ' ' + data.iat[r, 6] + " " + str(typecounter))
#         typecounter = typecounter + 1
#         counterb = 1
#     if counter > 1599:
#         typecounter = 0
#         counter = 0
#         counterb = 1


#     # print(r)

# # print(data)
# data.to_csv('~/miniconda3/envs/testequ/RTSeval/Python/Data/rtsData/rtsDataidvgsMod.csv')

# data = inport(fileLoc, 0 , 0, ['Site', 'Type', 'Vd', 'Vg', 'Id', 'W/L', 'Vth', 'Gm'])
# grouped = data.groupby(data.Gm) 
# vthData1 = grouped.get_group(max(data.Gm))
# vthEx = vthData1.Vd - 1
# print(vthEx)
list = np.linspace(3.3, 0)
vdList = [0.1, 0.8] 
print(list)