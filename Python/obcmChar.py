import serial
import sys
import time
import re
import pandas as pd
import matplotlib.pyplot as plt
from keithley2600 import Keithley2600
from BKPrecision import lib1785b as bk
from os import system, name
from datetime import datetime

# datetime object containing current date and time
#now = datetime.now()
 
#print("now =", now)

# dd/mm/YY H:M:S
dt_string = datetime.now().strftime("%Y_%m_%d-%I_%M_%S_%p")
#print("date and time =", dt_string)

#pico = serial.Serial('COM4', baudrate=115200)
smu = Keithley2600('TCPIP0::192.168.4.11::INSTR')               #set ip addr for smu
#smu._write(value='smua.source.autorangei = smua.AUTORANGE_ON')  #set auto range for smua
smu._write(value='smub.source.autorangev = smub.AUTORANGE_ON')  #set auto range for smua 

#smu.set_integration_time(smu.smua, 0.001)                       # sets integration time in sec
#smu._write(value= 'smua.source.limitv = 3.3')                   #set v liimit smua
smu._write(value= "smub.source.limitv = 3.3")                   #set v liimit smub
bkPS = serial.Serial('com6',9600)                               #set com port for BK power supply
bkdmm = serial.Serial('com7', 9600)  
                           #set com port for BK power supply
# def clear ():
#     if name == 'nt':
#         _ = system('cls')
#     else:
#         _ = system('clear')
# def write_cmd(x):
#     pico.write(bytes(x, 'utf-8'))
#     time.sleep(0.05)

dmmData = pd.DataFrame(data=[], index=[], columns=[])           #create dataframe
bk.remoteMode(True, bkPS) #set remote mode for power supply
bk.setMaxVoltage(10, bkPS)   #set max voltage for PS
bk.outputOn(True, bkPS)     #turn the powersupply on
bk.volt(0, bkPS)    #set voltage for power supply

bkdmm.write(b'func curr:dc\n')                                  #set dmm to volt
bkdmm.write(b'curr:dc:rang:auto 1\n')                           #set ddm to auto range
row = 0
counter = 0
voltIn = 0
currOut = 0
NMOS = 1
PMOS = 2
pwrInc = 8  #int(input('How many steps for current?'))
voltInc = 100      #int(input('How many steps for Voltage?'))

smu.apply_current(smu.smua, 0)
cOut = "CurrOut001"                                            #variable to store column names
vOut = "VoltOut001"
vIn = "VpwrIn000"
#bkPS.outputON(True, bkPS)
#commandTX = write_cmd(str(NMOS))  
time.sleep(1)
for vpwr in range (pwrInc):   #the voltage applied to opamp
    vpwr = vpwr + 3
    row = 0
    #smu.apply_current(smu.smua, currIn)  
    if counter > 0:
        cOut = re.sub(r'[0-9]+$',
                lambda x: f"{str(int(x.group())+1).zfill(len(x.group()))}",    # increments the number in the column name
                cOut)
        # vOut = re.sub(r'[0-9]+$',
        #         lambda x: f"{str(int(x.group())+1).zfill(len(x.group()))}",    # increments the number in the column name
        #         vOut)
        vIn = re.sub(r'[0-9]+$',
                lambda x: f"{str(int(x.group())+1).zfill(len(x.group()))}",    # increments the number in the column name
                vIn)
    counter = counter + 1
    bk.volt(vpwr, bkPS)    #set voltage for power supply
    time.sleep(1)
    for v in range(voltInc):
        voltIn = (1+v)/10                                   #the voltage applied to vout_byp
        smu.apply_voltage(smu.smub, voltIn)             # turns on and applies 10V to SMUA
        time.sleep(.1)
        bkdmm.write(b'fetch?\n')                        #requests the measurement from the bkdmm
        dmmCurr = bkdmm.readline()                      #reads the measurement from the bkdmm
        #currVOut = smu.smua.measure.v()                 #measure the voltage at ampBias
        voltIn = smu.smub.measure.v()                   #measure the voltage at vout_byp
        #if counter == 1:
        dmmData.at[row, 'VoltIn'] = float(voltIn)   #records the voltage applied to vout_byp
        dmmData.at[row, vIn] = (vpwr)
        #dmmData.at[row, str(cIn)] = float(currIn)       #records the current applied to the ampBias
        #dmmData.at[row, str(cOut)] = float(currVOut)    #records the voltage at ampBias
        dmmData.at[row, str(cOut)] = float(dmmCurr)*1000     #records the output voltage
        row = row + 1         
print(dmmData)
dmmData.to_csv('~/miniconda3/envs/testequ/RTSeval/Python/Data/obcmCharacterization/obcmCharData' + dt_string + '.csv')
#smu._write(value='smua.source.output = smua.OUTPUT_OFF')
smu._write(value='smub.source.output = smub.OUTPUT_OFF')
bk.outputOn(False, bkPS)     #turn the powersupply on

plt.plot(dmmData.VoltIn, dmmData.CurrOut001, label = "vgs=3")
plt.plot(dmmData.VoltIn, dmmData.CurrOut002, label = "vgs=4")
plt.plot(dmmData.VoltIn, dmmData.CurrOut003, label = "vgs=5")
plt.plot(dmmData.VoltIn, dmmData.CurrOut004, label = "vgs=6")
plt.plot(dmmData.VoltIn, dmmData.CurrOut005, label = "vgs=7")
plt.plot(dmmData.VoltIn, dmmData.CurrOut006, label = "vgs=8")
plt.plot(dmmData.VoltIn, dmmData.CurrOut007, label = "vgs=9")
plt.plot(dmmData.VoltIn, dmmData.CurrOut008, label = "vgs=10")
# plt.plot(dmmData.VoltIn, dmmData.CurrOut009, label = "vpwr=8")
# plt.plot(dmmData.VoltIn, dmmData.CurrOut010, label = "vpwr=9")
# plt.plot(dmmData.VoltIn, dmmData.CurrOut011, label = "vpwr=10")
plt.title("Vin vs Cout")
plt.xlabel("Vin (V)")
plt.ylabel("Cout (mA)")
plt.legend()
plt.savefig("C:\\Users\\jacob\\miniconda3\\envs\\testequ\\RTSeval\\Python\\Data\\obcmCharacterization\\lm393currRef.png")
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
# plt.plot(dmmData.CurrIn011, dmmData.CurrVOut011, label = "AmpBias V 11")
# plt.title("Voltage at AMPBIAS vs Current Into AMPBIAS")
# plt.xlabel("Current Into AMPBIAS")
# plt.ylabel("Voltage at AMPBIAS")
# plt.legend()
# plt.savefig("C:\\Users\\jacob\\miniconda3\\envs\\testequ\\RTSeval\\Python\\Data\\ampCharacterization\\amp0_ampVin_vs_ampCin.png")
# fig = plt.show()
# plt.pause(3)
# plt.close(fig)