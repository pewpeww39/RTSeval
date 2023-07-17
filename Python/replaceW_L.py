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

fileLoc = 'C:\\Users\\jpew\\miniconda3\\envs\\testequ\\RTSeval\\Python\\Data\\rtsData\\zoomRTS2\\rtsData_Loop10nA'
picLoc = 'C:\\Users\\jpew\\miniconda3\\envs\\testequ\\RTSeval\\Python\\Data\\rtsData\\zoomRTS2\\rtsData_10nA_bank2.csv'

# inport specdata
# inport recorded data
# if col == col in spec data
#   replace w/l value

data = inport(fileLoc+'.csv', 0 , 0, ['Vs','Vgs', 'Ids', 'Sample_Rate', 'Ticks', 'Column','Row','W_L', 'Type', 'DieX', 'DieY'])
print(data)
data.Sample_Rate = 2
for col in range(32, 64, 1):
    data.loc[data["Column"] == col, "W_L"] = specData.iat[col, 0]
    # data.loc[data["Column"] == col+1, "Column"] = col
print(data)

data.to_csv(picLoc)
# data.to_csv(fileLoc+'f.csv')