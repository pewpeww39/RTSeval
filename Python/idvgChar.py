from os import system, name
import serial
import sys
import time
import re
import pandas as pd
import matplotlib.pyplot as plt
from keithley2600 import Keithley2600
from BKPrecision import lib1785b as bk
from datetime import datetime
import numpy as np

dt_string = datetime.now().strftime("%Y_%m_%d-%I_%M_%S_%p")

pico = serial.Serial('COM4', baudrate=115200)
smu = Keithley2600('TCPIP0::192.168.4.11::INSTR')               #set ip addr for smu
smu._write(value='smua.source.autorangei = smua.AUTORANGE_ON')  #set auto range for smua 
smu._write(value='smub.source.autorangev = smub.AUTORANGE_ON')  #set auto range for smua 
smu.set_integration_time(smu.smua, 0.001)                       # sets integration time in sec
smu._write(value= 'smua.source.limitv = 3.3')                   #set v liimit smua
smu._write(value= "smub.source.limitv = 3.3")                   #set v liimit smub
# bkPS = serial.Serial('com6',9600)                               #set com port for BK power supply
# bkdmm = serial.Serial('com7', 9600)                             #set com port for BK power supply
def logScale():
    decade1 = range(1,10)
    decade2 = range(10,100,10)
    decade3 = range(100,1000, 100)
    decade4 = range(1000,10000, 1000)
    decade5 = range(10000,100000, 10000)    
    decade6 = range(100000,1000000, 100000)
    decade7 = range(1000000,10000000, 1000000)
    decade8 = range(10000000,60000000, 10000000)
    decadeList = np.append(decade1, decade2)
    decadeList = np.append(decadeList, decade3)
    decadeList = np.append(decadeList, decade4)
    decadeList = np.append(decadeList, decade5)
    decadeList = np.append(decadeList, decade6)
    decadeList = np.append(decadeList, decade7)
    decadeList = np.append(decadeList, decade8)
    print(len(decadeList))
    return decadeList
    
def clear ():
    if name == 'nt':
        _ = system('cls')
    else:
        _ = system('clear')
def write_cmd(x):
    pico.write(bytes(x, 'utf-8'))
    time.sleep(0.05)
currIn = []
measVs = []
measVI = []
vGS = []
spec=[]
csData = pd.DataFrame(data=[], index=[], columns=[])  
pltData = pd.DataFrame(data=[], index=[], columns=[])         #create dataframe
specData = pd.DataFrame(pd.read_csv('~\miniconda3\envs\\testequ\RTSeval\Files\RTS_Array_Cells.csv',
                     index_col=[0] , header=0), columns = ['W', 'L', 'Type'])
debug = True
row = 0
counter = 0
voltIn = 0
currOut = 0
commandTX = 0
colSelect = 2
power = 9
colNum = 32      #int(input('How many colums do you want to test?'))
currentInc = 11   #int(input('How many steps for current?'))
voltInc = 34      #int(input('How many steps for Voltage?'))

smu.apply_current(smu.smua, 0.0)
smu.apply_current(smu.smub, 0.0)
colS = "Col001"   
picLoc = "C:\\Users\\jacob\\miniconda3\\envs\\testequ\\RTSeval\\Python\\Data\\csCharacterization\\"
time.sleep(1)
decadeList = logScale()
print(decadeList)
for c in range(colNum):
    commandTX = write_cmd(str(3))                                                   # selects the switch case on the pico
    commandRX = pico.read_until().strip().decode()                                  # confirms mode selected
    time.sleep(.5)
    print('pico confirmed: ' + str(commandRX))
    column = write_cmd(str(colSelect))                                              # increments the column to test
    columnRX = pico.read_until().strip().decode()                                   # confirms column selected
    print('pico selected column: ' + str(columnRX))
    commandRX = int(pico.read_until().strip().decode())                             # confirms shift registers are loaded
    spec = list(specData.iloc[c+1])
    if commandRX == 1:
        for a in range(len(decadeList)):
            currIn = np.append(currIn, decadeList[a] * .000000000001)
            smu.apply_current(smu.smua, decadeList[a] * .000000000001)
            measVI = np.append(measVI, smu.smua.measure.v())
            measVs = np.append(measVs, float(smu.smub.measure.v()))
            vGS = 1.2 - measVs
            row = row + 1
        pltData["Vgs"] = measVs
        pltData["Id"] = currIn
        csData[colS+'Vs'] = measVs
        csData[colS+'Id'] = currIn
        csData[colS+'Vi'] = measVI
        if debug is True:
            print(measVs)
            print(vGS)
        plt.plot(vGS, pltData.Id, label = "Vs")
        plt.yscale('log')
        plt.title(colS + '' + str(spec) +" Id vs Vgs")
        plt.xlabel("Vgs [V]")
        plt.ylabel("Id [A]")
        plt.legend()
        plt.savefig(picLoc + colS + str(spec) + "idvg.png")
        fig = plt.show(block = False)
        plt.pause(3)
        plt.close(fig)
        pltData.plot(x="Id", xlabel="Current [A]", ylabel="Voltage [V]", sharey=True, title=(colS + '' + 
                        str(spec) + " Current In [Id] vs. Voltage Out [Vs]"), legend=True,
                    subplots=False, logx= True)
        plt.savefig(picLoc + colS + str(spec) + "idvs.png")
        fig = plt.show(block = False)
        plt.pause(3)
        plt.close(fig)
        colS = re.sub(r'[0-9]+$',
            lambda x: f"{str(int(x.group())+1).zfill(len(x.group()))}",    # increments the number in the column name
            colS)
        currIn = []
        measVs = []
        measVI = []
        vGS = []
        row = 0
        power = 9
        commandRX=0
        colSelect = colSelect + 1
csData.to_csv('~/miniconda3/envs/testequ/RTSeval/Python/Data/csCharacterization/cscharData' + dt_string + '.csv')
print(csData)
smu._write(value='smua.source.output = smua.OUTPUT_OFF')
smu._write(value='smub.source.output = smub.OUTPUT_OFF')
