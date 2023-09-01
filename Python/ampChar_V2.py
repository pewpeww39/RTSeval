import serial
import sys
import time
import re
import pandas as pd
import matplotlib.pyplot as plt
from keithley2600 import Keithley2600
# import RTSeval.Python.BKPrecision.lib1785b as bk
from os import system, name
from datetime import datetime

# datetime object containing current date and time
dt_string = datetime.now().strftime("%Y_%m_%d-%I_%M_%S_%p")

pico = serial.Serial('COM5', baudrate=115200)
smu = Keithley2600('TCPIP0::192.168.4.11::INSTR')               #set ip addr for smu

def clear ():
    if name == 'nt':
        _ = system('cls')
    else:
        _ = system('clear')
def write_cmd(x):
    pico.write(bytes(x, 'utf-8'))
    time.sleep(0.05)

data = pd.DataFrame(data=[], index=[], columns=["vIn", "vOut"])           #create dataframe

# int(input('How many steps for current?'))
# int(input('How many steps for Voltage?'))

def doe1_ampCharacterization(select):
    smu.smua.OUTPUT_DCVOLTS          # SMU 1 is set to apply voltage
    smu.smub.OUTPUT_DCAMPS           # SUM 2 is set to measure voltage
    smu._write(value='smua.source.output = smua.OUTPUT_ON')
    smu._write(value='smub.source.output = smub.OUTPUT_ON')
    #bkPS.outputON(True, bkPS)
    write_cmd(f"{select}")  
    time.sleep(1)
    commandRX = int(pico.read_until().strip().decode())                             # confirms amp characterization is selected
    if commandRX == 1 or commandRX == 2:
        print('pico selected amp characterization procedure.')
        vList = (0, 1.8, 100)
        delay = 0
        t_int = 0
        data.vIn, data.vOut = smu.doe1AmpChar(smu.smua, smu.smub, vList, delay, t_int)
        plt.plot(data.vIn, data.vOut, label = '0.5 mA')
        plt.title("Vin vs Vout")
        plt.xlabel("Vin")
        plt.ylabel("Vout")
        plt.legend()
        plt.savefig("C:\\Users\\UTChattsat\\miniconda3\\envs\\testequ\\RTSeval\\Python\\Data\\ampCharacterization\\amp0_VoVsVin.png")
        fig = plt.show()
        plt.pause(3)
        plt.close(fig)
        commandTX = write_cmd(f"{9}")          
        # print(data)
        data.to_csv('~/miniconda3/envs/testequ/RTSeval/Python/Data/ampCharacterization/ampcharData' + dt_string + '.csv')
        smu._write(value='smua.source.output = smua.OUTPUT_OFF')
        smu._write(value='smub.source.output = smub.OUTPUT_OFF')


NMOS = 1
PMOS = 2
doe1_ampCharacterization(NMOS)