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

dt_string = datetime.now().strftime("%Y_%m_%d-%I_%M_%S_%p")

pico = serial.Serial('COM4', baudrate=115200)
smu = Keithley2600('TCPIP0::192.168.4.11::INSTR')               #set ip addr for smu
smu._write(value='smua.source.autorangei = smua.AUTORANGE_ON')  #set auto range for smua 
smu._write(value='smub.source.autorangev = smub.AUTORANGE_ON')
smu.set_integration_time(smu.smua, 0.001)                       # sets integration time in sec
smu._write(value= 'smua.source.limitv = 3.3')                   #set v liimit smua
smu._write(value= "smub.source.limitv = 3.3")                   #set v liimit smub
bkPS = serial.Serial('com6',9600)                               #set com port for BK power supply
bkdmm = serial.Serial('com7', 9600)                             #set com port for BK power supply

def clear ():
    if name == 'nt':
        _ = system('cls')
    else:
        _ = system('clear')
def write_cmd(x):
    pico.write(bytes(x, 'utf-8'))
    time.sleep(0.05)

csData = pd.DataFrame(data=[], index=[], columns=[])  
pltData = pd.DataFrame(data=[], index=[], columns=[])         #create dataframe
bk.remoteMode(True, bkPS) #set remote mode for power supply
bk.setMaxVoltage(3.33, bkPS)   #set max voltage for PS
#bk.outputOn(True, bkPS)     #turn the powersupply on
#bk.volt(3.3, bkPS)    #set voltage for power supply

bkdmm.write(b'func volt:dc\n')                                  #set dmm to volt
bkdmm.write(b'volt:dc:rang:auto 1\n')                           #set ddm to auto range
debug = False
row = 0
counter = 0
voltIn = 0
currOut = 0
commandTX = 0
colSelect = 1
power = 9
colNum = 1      #int(input('How many colums do you want to test?'))
currentInc = 11   #int(input('How many steps for current?'))
voltInc = 34      #int(input('How many steps for Voltage?'))

smu.apply_current(smu.smua, 0)
cOut = "CS000"   
pltY = " ampsOut E-9"
pltX = " ampsIn E-9"
picLoc = "C:\\Users\\jacob\\miniconda3\\envs\\testequ\\RTSeval\\Python\\Data\\csCharacterization\\"
# picLoc = "~/miniconda3/envs/testequ/RTSeval/Python/Data/csCharacterization/"

time.sleep(1)
for c in range(colNum):
    if counter > 0:
        cOut = re.sub(r'[0-9]+$',
             lambda x: f"{str(int(x.group())+1).zfill(len(x.group()))}",    # increments the number in the column name
             cOut)
    commandTX = write_cmd(str(3))                                                   # increments the column to test
    commandRX = pico.read_until().strip().decode()
    time.sleep(.5)
    print('pico confirmed: ' + str(commandRX))
    column = write_cmd(str(colSelect))
    columnRX = pico.read_until().strip().decode()
    print('pico selected column: ' + str(columnRX))
    commandRX = int(pico.read_until().strip().decode())
    if commandRX == 1:
        for a in range(5):
            currIn = pow(10, -power)                                                   # the current applied to currentSource
            smu.apply_current(smu.smua, currIn)
            startT = round(time.perf_counter(), 4)
            while round(time.perf_counter(), 4) - startT <= 1.1:
                currentTime = round(time.perf_counter(), 4) - startT
                if counter == 0:
                    pltData.at[row, 'Time'] = currentTime
                #pltData.at[row, pltX] = smu.smua.measurei()
                pltData.at[row, pltY] = smu.smub.measure.i()
                row = row + 1
                time.sleep(.1000)
            csData['Time'] = pltData['Time']
            csData[str(cOut+pltY)] = pltData[str(pltY)]
            if a < 4:
                pltY = re.sub(r'[0-9]+$',
                lambda x: f"{str(int(x.group())-1).zfill(len(x.group()))}",    # increments the number in the column name
                pltY)
                pltX = re.sub(r'[0-9]+$',
                lambda x: f"{str(int(x.group())-1).zfill(len(x.group()))}",    # increments the number in the column name
                pltX)
            row = 0
            power = power - 1
        power = 9
        pltX = 'ampsIn E-9'
        ampVal = 'ampsOut E-9'
        if debug is True:
            print(pltData)
        pltData.plot(xlabel="Volt Out", ylabel="Current In", sharey=True, title="Volt In vs. Current Out", legend=True,
                    subplots=False)
        # pltData.plot(x= 'Time', xlabel="Time", ylabel="Current Out", sharey=True, title="Current In vs. Current Out", legend=True,
        #             subplots=[(' ampsIn E-9',' ampsOut E-9'),(' ampsIn E-8',' ampsOut E-8'),(' ampsIn E-7',' ampsOut E-7'), 
        #             (' ampsIn E-6',' ampsOut E-6'),(' ampsIn E-5',' ampsOut E-5')])
        plt.savefig(picLoc + cOut + ".png")
        fig = plt.show(block = False)
        plt.pause(3)
        plt.close(fig)
    commandRX=0
    counter = counter + 1
    colSelect = colSelect + 1
print(csData)
csData.to_csv('~/miniconda3/envs/testequ/RTSeval/Python/Data/csCharacterization/cscharData' + dt_string + '.csv')
smu._write(value='smua.source.output = smua.OUTPUT_OFF')
smu._write(value='smub.source.output = smub.OUTPUT_OFF')
#bk.outputOn(False, bkPS)     #turn the powersupply off
