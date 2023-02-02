import serial
import sys
import time
import re
import pandas as pd
import matplotlib.pyplot as plt
from keithley2600 import Keithley2600
from BKPrecision import lib1785b as bk
from os import system, name

pico = serial.Serial('COM4', baudrate=115200)
smu = Keithley2600('TCPIP0::192.168.4.11::INSTR')               #set ip addr for smu
smu._write(value='smua.source.autorangei = smua.AUTORANGE_ON')  #set auto range for smua
smu._write(value='smub.source.autorangev = smub.AUTORANGE_ON')  #set auto range for smua 

smu.set_integration_time(smu.smua, 0.001)                       # sets integration time in sec
smu._write(value= 'smua.source.limitv = 3.3')                   #set v liimit smua
smu._write(value= "smub.source.limitv = 3.3")                   #set v liimit smub
bkPS = serial.Serial('com6',9600)                               #set com port for BK power supply
bkdmm = serial.Serial('com7', 9600)                             #set com port for BK multimeter
def clear ():
    if name == 'nt':
        _ = system('cls')
    else:
        _ = system('clear')
def write_cmd(x):
    pico.write(bytes(x, 'utf-8'))
    time.sleep(0.05)

dmmData = pd.DataFrame(data=[], index=[], columns=[])           #create dataframe
bk.remoteMode(True, bkPS) #set remote mode for power supply
bk.setMaxVoltage(3.3, bkPS)   #set max voltage for PS
bk.outputOn(True, bkPS)     #turn the powersupply on
bk.volt(3.3, bkPS)    #set voltage for power supply

bkdmm.write(b'func volt:dc\n')                                  #set dmm to volt
bkdmm.write(b'volt:dc:rang:auto 1\n')                           #set ddm to auto range
row = 0
counter = 0
voltIn = 0
currOut = 0
NMOS = 1
PMOS = 2
currentInc = 11   #int(input('How many steps for current?'))
voltInc = 1.7      #int(input('How many steps for Voltage?'))

smu.apply_current(smu.smua, 0)
vIn = "VIn1"                                            #variable to store column names
vOut = "VoltOut001"
cIn = "CurrIn001"
#bkPS.outputON(True, bkPS)
commandTX = write_cmd(str(NMOS))  
time.sleep(1)
currIn = -0.0005                                                            #the current applied to ampBias
smu.apply_current(smu.smua, currIn) 
v = 1
for v in range(2,4):
    row = 0
    if counter > 0:
        vIn = re.sub(r'[0-9]+$',
             lambda x: f"{str(int(x.group())+1).zfill(len(x.group()))}",    # increments the number in the column name
             vIn)
        vOut = re.sub(r'[0-9]+$',
             lambda x: f"{str(int(x.group())+1).zfill(len(x.group()))}",    # increments the number in the column name
             vOut)

    counter = counter + 1
    time.sleep(.2)
    #for v in range(voltInc):
    voltIn = voltInc/(5-v)                                   #the voltage applied to vout_byp
    smu.apply_voltage(smu.smub, voltIn)             # turns on and applies 10V to SMUAstartT = round(time.perf_counter(), 4)
    startT = round(time.perf_counter(), 4)
    while round(time.perf_counter(), 4) - startT <= 10.1:
        currentTime = round(time.perf_counter(), 4) - startT
        bkdmm.write(b'fetch?\n')                        #requests the measurement from the bkdmm
        dmmVolt = bkdmm.readline()                      #reads the measurement from the bkdmm
        currVOut = smu.smua.measure.v()                 #measure the voltage at ampBias
        dmmData.at[row, str(vIn)] = currentTime - startT       #records the current applied to the ampBias
        dmmData.at[row, str(vOut)] = float(dmmVolt)     #records the output voltage
        row = row + 1
        print(currentTime)
        time.sleep(.1000)
    print('CAPTURE!')
    time.sleep(10)
commandTX = write_cmd(str(9))          
print(dmmData)
dmmData.to_csv('~/miniconda3/envs/testequ/Skywater/Data/ampcharData.csv')
smu._write(value='smua.source.output = smua.OUTPUT_OFF')
smu._write(value='smub.source.output = smub.OUTPUT_OFF')
bk.outputOn(False, bkPS)     #turn the powersupply on

plt.plot(dmmData.VIn1, dmmData.VoltOut001, label = "0 mA")
plt.plot(dmmData.VIn2, dmmData.VoltOut002, label = "0.1 mA")
#plt.plot(dmmData.VIn3, dmmData.VoltOut003, label = "0.2 mA")
#plt.plot(dmmData.VIn4, dmmData.VoltOut004, label = "0.3 mA")
# plt.plot(dmmData.VoltIn, dmmData.VoltOut005, label = "0.4 mA")
# plt.plot(dmmData.VoltIn, dmmData.VoltOut006, label = "0.5 mA")
# plt.plot(dmmData.VoltIn, dmmData.VoltOut007, label = "0.6 mA")
# plt.plot(dmmData.VoltIn, dmmData.VoltOut008, label = "0.7 mA")
# plt.plot(dmmData.VoltIn, dmmData.VoltOut009, label = "0.8 mA")
# plt.plot(dmmData.VoltIn, dmmData.VoltOut010, label = "0.9 mA")
# plt.plot(dmmData.VoltIn, dmmData.VoltOut011, label = "1 mA")
plt.title("Vin vs Vout")
plt.xlabel("Vin")
plt.ylabel("Vout")
plt.legend()
plt.savefig("C:\\Users\\jacob\\miniconda3\\envs\\testequ\\RTSeval\\Python\\Data\\ampCharacterization\\amp0TS_VoVsVin.png")
fig = plt.show()
plt.pause(3)
plt.close(fig)

# plt.plot(dmmData.CurrIn001, dmmData.CurrVOut001, label = "AmpBias V 01")
# plt.plot(dmmData.CurrIn002, dmmData.CurrVOut002, label = "AmpBias V 02")
# plt.plot(dmmData.CurrIn003, dmmData.CurrVOut003, label = "AmpBias V 03")
# plt.plot(dmmData.CurrIn004, dmmData.CurrVOut004, label = "AmpBias V 04")
# plt.plot(dmmData.CurrIn005, dmmData.CurrVOut005, label = "AmpBias V 05")
# plt.plot(dmmData.CurrIn006, dmmData.CurrVOut006, label = "AmpBias V 06")
# plt.plot(dmmData.CurrIn007, dmmData.CurrVOut007, label = "AmpBias V 07")
# plt.plot(dmmData.CurrIn008, dmmData.CurrVOut008, label = "AmpBias V 08")
# plt.plot(dmmData.CurrIn009, dmmData.CurrVOut009, label = "AmpBias V 09")
# plt.plot(dmmData.CurrIn010, dmmData.CurrVOut010, label = "AmpBias V 10")
# plt.plot(dmmData.CurrIn011, dmmData.CurrVOut011, label = "AmpBias V `11")
# plt.title("Voltage at AMPBIAS vs Current Into AMPBIAS")
# plt.xlabel("Current Into AMPBIAS")
# plt.ylabel("Voltage at AMPBIAS")
# plt.legend()
# plt.savefig("C:\\Users\\jacob\\miniconda3\\envs\\testequ\\RTSeval\\Python\\Data\\ampCharacterization\\amp0_ampVin_vs_ampCin.png")
# fig = plt.show()
# plt.pause(3)
# plt.close(fig)