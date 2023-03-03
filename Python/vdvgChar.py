from os import system, name
import serial
import sys
import time
import re
import pandas as pd
import matplotlib.pyplot as plt
from keithleyDriver import Keithley2600
#from keithley2600 import Keithley2600
# from BKPrecision import lib1785b as bk
from datetime import datetime
import numpy as np

dt_string = datetime.now().strftime("%Y_%m_%d-%I_%M_%S_%p")

pico = serial.Serial('COM5', baudrate=115200)
smu = Keithley2600('TCPIP0::192.168.4.11::INSTR')               #set ip addr for smu
smu._write(value='smua.source.autorangei = smua.AUTORANGE_ON')  #set auto range for smua 
smu._write(value='smub.source.autorangev = smub.AUTORANGE_OFF')  #set auto range for smua 
smu._write(value= 'smua.source.limitv = 3.3')                   #set v liimit smua
smu._write(value= "smub.source.limitv = 3.3")                   #set v liimit smub

def clear ():
    if name == 'nt':
        _ = system('cls')
    else:
        _ = system('clear')
def write_cmd(x):
    pico.write(bytes(x, 'utf-8'))
    time.sleep(0.05)

currOut = []
measVd = []
measVg = []
spec = []
vdvgData = pd.DataFrame(data=[], index=[], columns=[])  
pltData = pd.DataFrame(data=[], index=[], columns=['Site', 'Type'])         #create dataframe
specData = pd.DataFrame(pd.read_csv('~\miniconda3\envs\\testequ\RTSeval\Files\RTS_Array_Cells.csv',
                     index_col=[0] , header=0), columns = ['W/L', 'Type'])
debug = False
counter = 0
voltIn = 0
currOut = 0
commandTX = 0
# colSelect = 1
# rowSelect = 1
rowNum = 96
colNum = 32      #int(input('How many colums do you want to test?'))
dieX = '6p'
dieY = '3'

smu.apply_voltage(smu.smua, 0.0)
smu.apply_voltage(smu.smub, 0.0)
colS = "Col000"   
rowS = "Row00"
picLoc = "C:\\Users\\UTChattsat\\miniconda3\\envs\\testequ\\RTSeval\\Python\\Data\\vdvgCharacterization\\Bank 1\\vdvgcharData"
time.sleep(1)
sweepList = np.linspace(0, 1.2)
# measVg = sweepList
vdList = [0.1, 0.8]
# print(decadeList)
for row in range(1, rowNum+1):
    for col in range(1, colNum+1):
        # start_total_time = time.time()
        commandTX = write_cmd(f"5,{row},{col}")                                                   # selects the switch case on the pico
        commandRX = tuple(pico.read_until().strip().decode().split(','))
        if debug is True:
            print(commandRX)
        commandRX, rowRX, columnRX = commandRX
        # end_command_time = time.time()
        print('pico confirmed: ' + str(commandRX))
        print('pico selected row: ' + str(rowRX))
        print('pico selected column: ' + str(columnRX))
        # start_response_time = time.time()
        commandRX = int(pico.read_until().strip().decode())                             # confirms shift registers are loaded
        print(f'pico loaded shift register - response {commandRX}')                           # confirms shift registers are loaded
        # end_response_time = time.time()
        # start_voltage_sweep = time.time()
        spec = list(specData.iloc[col-1])
        smu._write(value = "smua.measure.autozero = smua.AUTOZERO_AUTO")
        smu.smub.measure.v()
        currOut, measVd, measVg= smu.vdvgChar(smu.smua, smu.smub, sweepList, vdList, .001, .01)
        # vGS = measVs 
        # for i in range(len(measVs)):
        #     vGS[i] = 1.2 - vGS[i]
        # print(vGS)
        # pltData["Vgs"] = vGS # [1.2 - measVs for i in range(len(measVs))]
        pltData["Vd"] = measVd
        pltData["Vg"] = measVg
        pltData["Id"] = currOut
        pltData1Id = pltData.loc[:49, 'Id']
        pltData2Id = pltData.loc[50:99, 'Id']
        pltData1Vg = pltData.loc[:49, 'Vg']
        pltData2Vg = pltData.loc[50:99, 'Vg']
        pltGm1 = np.gradient(pltData.loc[:49, 'Id'], pltData.loc[:49, 'Vg'])
        pltGm2 = np.gradient(pltData.loc[50:99, 'Id'], pltData.loc[50:99, 'Vg'])
        pltVth1 = np.full_like(pltData1Id, max(np.gradient(pltData.loc[2:49, 'Id'], pltData.loc[2:49, 'Vg'], edge_order=2)))
        pltVth2 = np.full_like(pltData2Id, max(np.gradient(pltData.loc[52:99, 'Id'], pltData.loc[52:99, 'Vg'], edge_order=2)))
        pltData['Site'] = 'UTC'
        pltData['Type'] = spec[1]
        pltData["W/L"] = spec[0]
        pltData["Temp(K)"] = 295
        pltData["Die X"] = dieX
        pltData["Die Y"] = dieY
        pltData["Vth"] = np.append(pltVth1, pltVth2)
        pltData["Gm"] = np.append(pltGm1, pltGm2)
        pltData["Row"] = row
        pltData['Column'] = col
        # print(pltData)
        if debug is True:
            print(len(measVg))
            # print(vGS)
        if col % 2 == 0:
            vth1 = pltData.at[1, "Vth"]
            vth2 = pltData.at[51, "Vth"]
            grouped = pltData.groupby(pltData.Vth) 
            pltData1 = grouped.get_group(vth1)
            pltData2 = grouped.get_group(vth2)
            plt.plot(pltData1["Vg"], pltData1["Id"], label = "vD = 0.1")
            plt.plot(pltData2["Vg"], pltData2["Id"], label = "Vd = 0.8")
            # plt.figtext(.4, .15, "Vg = 1.2 V, Vdd = 1.2 V", fontsize = 10)
            # plt.figtext(.4, .2, "Ibias = 20 uA to .1 nA, AmpBias = .5 mA", fontsize = 10)
            # plt.figtext(.4, .25, "column = " + str(colS) + ", row = " + str(rowS), fontsize = 10)
            plt.yscale('log')
            plt.title(rowS + '' + colS + '' + str(spec) +" Id vs Vgs")
            plt.xlabel("Vg [V]")
            plt.ylabel("Id [A]")
            plt.legend()
            plt.savefig(picLoc + rowS + colS + "idvg.png")
            fig1 = plt.show(block = False)
            # plt.pause(3)
            plt.close(fig1)
            # pltData1.plot(x="Vg", y="Id", xlabel="Ids [A]", ylabel="Vg [V]", sharey=True, title=(rowS + '' + colS + '' + 
            #                 str(spec) + " Drain Current [Id] vs. Gate Voltage [Vs]"), legend=True,
            #             subplots=False, logx= True)
            # # plt.figtext(.2, .15, "Vg = 1.2 V, Vdd = 1.2 V", fontsize = 10)
            # # plt.figtext(.2, .2, "Ibias = 1 nA, AmpBias = .5 mA", fontsize = 10)
            # # plt.figtext(.2, .25, "column = " + str(colS) + ", row = " + str(rowS), fontsize = 10)
            # plt.savefig(picLoc + rowS + colS + "vdvg.png")
            # fig2 = plt.show(block = False)
            # # plt.pause(3)
            # plt.close(fig2)
            # pltData1.plot(x="Vg", y="Gm", xlabel="Vg [V]", ylabel="Gm ", sharey=True, title=(rowS + '' + colS + '' + 
            #                 str(spec) + " Transconductance vs. Vg [V]"), legend=True,
            #             subplots=False, logx= True)
            # # plt.figtext(.2, .15, "Vg = 1.2 V, Vdd = 1.2 V", fontsize = 10)
            # # plt.figtext(.2, .2, "Ibias = 1 nA, AmpBias = .5 mA", fontsize = 10)
            # plt.figtext(.2, .2, "column = " + str(colS) + ", row = " + str(rowS), fontsize = 10)
            # plt.savefig(picLoc + rowS + colS + "gm.png")
            # fig3 = plt.show(block = False)
            # # plt.pause(3)
            # plt.close(fig3)
        colS = re.sub(r'[0-9]+$',
            lambda x: f"{str(int(x.group())+1).zfill(len(x.group()))}",    # increments the number in the column name
            colS)
        currIn = []
        measVg = []
        measVd = []
        commandRX=0
        # colSelect = colSelect + 1
        vdvgData = pd.concat([vdvgData, pltData], axis = 0, ignore_index=True)
    colS = "Col000"
    rowS = re.sub(r'[0-9]+$',
                lambda x: f"{str(int(x.group())+1).zfill(len(x.group()))}",    # increments the number in the row name
                rowS)   
    # colSelect = 1
    # rowSelect = rowSelect + 1    
    # csData = pd.concat([csData, pltData], axis = 0, ignore_index=False)
    vdvgData.to_csv('~/miniconda3/envs/testequ/RTSeval/Python/Data/vdvgCharacterization/Bank 1/vdvgcharDataBAK.csv')
    
vdvgData.to_csv('~/miniconda3/envs/testequ/RTSeval/Python/Data/vdvgCharacterization/Bank 1/vdvgcharData' + dt_string + '.csv')
print(vdvgData)
smu._write(value='smua.source.output = smua.OUTPUT_OFF')
smu._write(value='smub.source.output = smub.OUTPUT_OFF')
