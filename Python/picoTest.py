from os import system, name
import serial
import sys
import time
import re
import pandas as pd
import matplotlib.pyplot as plt
from keithley2600 import Keithley2600
from BKPrecision import lib1785b as bk



pico = serial.Serial('COM12', baudrate=115200, timeout = 30)
# smu = Keithley2600('TCPIP0::192.168.4.11::INSTR')               #set ip addr for smu
# smu._write(value='smua.source.autorangei = smua.AUTORANGE_ON')  #set auto range for smua 
# smu.set_integration_time(smu.smua, 0.001)                       # sets integration time in sec
# smu._write(value= 'smua.source.limitv = 3.3')                   #set v liimit smua
# smu._write(value= "smub.source.limitv = 3.3")                   #set v liimit smub
# bkPS = serial.Serial('com6',9600)                               #set com port for BK power supply
# bkdmm = serial.Serial('com7', 9600)                             #set com port for BK power supply

def clear ():
    if name == 'nt':
        _ = system('cls')
    else:
        _ = system('clear')
def write_cmd(x):
    pico.write(bytes(x, 'utf-8'))
    time.sleep(0.05)

csData = pd.DataFrame(data=[], index=[], columns=[])           #create dataframe
# bk.remoteMode(True, bkPS) #set remote mode for power supply
# bk.setMaxVoltage(3.33, bkPS)   #set max voltage for PS
# bk.outputOn(True, bkPS)     #turn the powersupply on
# bk.volt(3.3, bkPS)    #set voltage for power supply

# bkdmm.write(b'func volt:dc\n')                                  #set dmm to volt
# bkdmm.write(b'volt:dc:rang:auto 1\n')                           #set ddm to auto range
row = 0
counter = 0
voltIn = 0
currOut = 0
commandTX = 0

colNum = 256      #int(input('How many colums do you want to test?'))
currentInc = 11   #int(input('How many steps for current?'))
voltInc = 34      #int(input('How many steps for Voltage?'))

#smu.apply_current(smu.smua, 0)
cOut = "CurrOut001"                                            #variable to store column names
cOutDF = "csData.CurrOut001"
vOut = "VoltOut001"
cIn = "CurrIn"
fileName = "~/miniconda3/envs/testequ/RTSeval/Python/Data/cdCharacterization/cs001.png"
time.sleep(1)
c = 1 
for c in range(colNum):

    if counter > 0:
        cOut = re.sub(r'[0-9]+$',
             lambda x: f"{str(int(x.group())+1).zfill(len(x.group()))}",    # increments the number in the column name
             cOut)
        cOutDF = re.sub(r'[0-9]+$',
             lambda x: f"{str(int(x.group())+1).zfill(len(x.group()))}",    # increments the number in the column name
             cOutDF)
        fileName = re.sub(r'[0-9]+$',
             lambda x: f"{str(int(x.group())+1).zfill(len(x.group()))}",    # increments the number in the column name
             fileName)
    WC = write_cmd(str(2))                                                  # increments the column to test
    column = pico.write(c)
    RFID = pico.read_until()                                                      # checks if pico is done with shift register
    commandRX = RFID.decode()
    if RFID == b'1\r\n':
        currIn = 0.000005                                                   # the current applied to currentSource
        # smu.apply_current(smu.smua, currIn)
    commandRX = 0
    startT = (time.perf_counter())
    timer = (time.perf_counter() - startT)
    print(startT)
    while time.perf_counter() - startT <= 60:                # checks if the run time has reached 60 sec
        # csData.at[row, str(cIn)] = smu.smua.measurei()
        # csData.at[row, str(cOut)] = smu.smub.measurei()
        row = row + 1
        time.sleep(.1)
    # plt.plot(csData.CurrIn, cOutDF, label = str(cOut))
    # plt.title("Current In vs Current Out")
    # plt.xlabel("Current Into AMPBIAS")
    # plt.ylabel("Currnet Out Vout Bypass")
    # plt.legend()
    # plt.savefig(fileName)
    # plt.show()
    # plt.close()
    row = 0
    counter = counter + 1
    time.sleep(.2)
        
# print(csData)
# csData.to_csv('~/miniconda3/envs/testequ/RTSeval/Python/Data/cscharData.csv')
# smu._write(value='smua.source.output = smua.OUTPUT_OFF')
# smu._write(value='smub.source.output = smub.OUTPUT_OFF')
# bk.outputOn(False, bkPS)     #turn the powersupply off
