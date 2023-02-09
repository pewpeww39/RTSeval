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
smu._write(value='smub.source.autorangei = smub.AUTORANGE_ON')  #set auto range for smua 
smu.set_integration_time(smu.smua, 0.001)                       # sets integration time in sec
smu._write(value= 'smua.source.limitv = 3.3')                   #set v liimit smua
smu._write(value= "smub.source.limitv = 3.3")                   #set v liimit smub
bkPS = serial.Serial('com6',9600)                               #set com port for BK power supply
bkdmm = serial.Serial('com7', 9600)                             #set com port for BK power supply
def logScale():
    decade1 = range(1,10)
    decade2 = range(10,100,10)
    decade3 = range(100,1000, 100)
    decade4 = range(1000,10000, 1000)
    decade5 = range(10000,110000, 10000)
    #decadeList = decade1.extend(decade2).extend(decade3).extend(decade4).extend(decade5)
    decadeList = np.append(decade1, decade2)
    decadeList = np.append(decadeList, decade3)
    decadeList = np.append(decadeList, decade4)
    decadeList = np.append(decadeList, decade5)
    #length = len(decadeList)
    return decadeList
    
def clear ():
    if name == 'nt':
        _ = system('cls')
    else:
        _ = system('clear')
def write_cmd(x):
    pico.write(bytes(x, 'utf-8'))
    time.sleep(0.05)
measArr = []
currIn = []
csData = pd.DataFrame(data=[], index=[], columns=[])  
pltData = pd.DataFrame(data=[], index=[], columns=[])         #create dataframe
bk.remoteMode(True, bkPS) #set remote mode for power supply
bk.setMaxVoltage(3.33, bkPS)   #set max voltage for PS
#bk.outputOn(True, bkPS)     #turn the powersupply on
#bk.volt(3.3, bkPS)    #set voltage for power supply

bkdmm.write(b'func volt:dc\n')                                  #set dmm to volt
bkdmm.write(b'volt:dc:rang:auto 1\n')                           #set ddm to auto range
debug = True
row = 0
counter = 0
voltIn = 0
currOut = 0
commandTX = 0
colSelect = 2
power = 9
colNum = 10      #int(input('How many colums do you want to test?'))
currentInc = 11   #int(input('How many steps for current?'))
voltInc = 34      #int(input('How many steps for Voltage?'))

smu.apply_current(smu.smua, 0)
colS = "Col001"   
pltY = " ampsIn E-9"
pltX = " voltOut0"
picLoc = "C:\\Users\\jacob\\miniconda3\\envs\\testequ\\RTSeval\\Python\\Data\\csCharacterization\\"
# picLoc = "~/miniconda3/envs/testequ/RTSeval/Python/Data/csCharacterization/"

opampI = smu.apply_current(smu.smub, -0.0005)
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
                                                # the current applied to currentSource
    
    if commandRX == 1:
        for a in range(46):
            currIns = decadeList[a] * .0000000001  
            #pltData.at[row, str(colS+pltY)] = smu.apply_current(smu.smua, pow(10, -power))
            currIn = np.append(currIn, currIns)
            smu.apply_current(smu.smua, currIns)
            #time.sleep(.1000)
            bkdmm.write(b'fetch?\n')                                                # requests the measurement from the bkdmm
            #pltData.at[row, str(colS+pltX)] = bkdmm.readline()                       # reads the measurement from the bkdmm
            measArr = np.append(measArr, float(bkdmm.readline().strip().decode()))
            #pltData.at[row, pltX] = smu.smub.measurev()
            row = row + 1
            # if a < 4:
            # if a == 4:
            #     csData[str(colS+pltX)] = np.fill_like(str(colS+pltY), currIn)
            pltY = re.sub(r'[0-9]+$',
                lambda x: f"{str(int(x.group())-1).zfill(len(x.group()))}",    # increments the number in the column name
                pltY)
            pltX = re.sub(r'[0-9]+$',
                lambda x: f"{str(int(x.group())+1).zfill(len(x.group()))}",    # increments the number in the column name
                pltX)
            
            # currIns = decadeList[a+1]*.0000000001
            # csData[str(colS+pltY)] = pltData[str(pltY)]
        #csData.to_csv('~/miniconda3/envs/testequ/RTSeval/Python/Data/csCharacterization/cscharData' + dt_string + '.csv')
        pltData["volt"] = measArr
        pltData["curr"] = currIn
        csData[colS+'volt'] = measArr
        csData[colS+'curr'] = currIn
        currIn = []
        measArr = []
        row = 0
        power = 9
        pltX = 'voltOut0'
        pltY = 'ampsIn E-9'
        if debug is True:
            print(measArr)
            print(currIn)
            print(csData)
            #plt.plot(pltData.Col001curr, pltData.Col001volt, label = "column1 row 1")
        pltData.plot(x="curr", xlabel="Current [A]", ylabel="Voltage [V]", sharey=True, title=(colS + "Current In vs. Voltage Out"), legend=True,
                    subplots=False, logx= False)
        # pltData.plot(x= 'Time', xlabel="Time", ylabel="Current Out", sharey=True, title="Current In vs. Current Out", legend=True,
        #             subplots=[(' ampsIn E-9',' ampsOut E-9'),(' ampsIn E-8',' ampsOut E-8'),(' ampsIn E-7',' ampsOut E-7'), 
        #             (' ampsIn E-6',' ampsOut E-6'),(' ampsIn E-5',' ampsOut E-5')])
        plt.savefig(picLoc + colS + ".png")
        fig = plt.show(block = False)
        plt.pause(3)
        plt.close(fig)
        colS = re.sub(r'[0-9]+$',
            lambda x: f"{str(int(x.group())+1).zfill(len(x.group()))}",    # increments the number in the column name
            colS)
        commandRX=0
        colSelect = colSelect + 1
#print(csData)
csData.to_csv('~/miniconda3/envs/testequ/RTSeval/Python/Data/csCharacterization/cscharData' + dt_string + '.csv')
smu._write(value='smua.source.output = smua.OUTPUT_OFF')
smu._write(value='smub.source.output = smub.OUTPUT_OFF')
#bk.outputOn(False, bkPS)     #turn the powersupply off
