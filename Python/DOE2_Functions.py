import serial
import sys
import time
import re
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from keithleyDriver import Keithley2600
from os import system, name
from datetime import datetime
from pathlib import Path
from scipy.signal import find_peaks, savgol_filter, peak_widths, welch
import os
import pyvisa
rm = pyvisa.ResourceManager()

# datetime object containing current date and time
dt_string = datetime.now().strftime("%Y_%m_%d-%I_%M_%S_%p")
# oscope = OScope("TCPIP0::192.168.4.2::inst0::11
# INSTR")
pico = serial.Serial('COM3', baudrate=115200)
smu = Keithley2600('TCPIP0::192.168.4.11::INSTR')               #set ip addr for smu
smu2 = Keithley2600('TCPIP0::192.168.4.12::INSTR')
powerSupply = rm.open_resource('TCPIP0::192.168.4.3::INSTR') 
p = Path.home()
# print(p)
def powerSupply_Set(channel, voltage, current):
    powerSupply.write("INST " + channel) # Select +6V output ch 1
    powerSupply.write("VOLT " + voltage) # Set output voltage to 3.0 V
    powerSupply.write("CURR " + current) # Set output current to 1.0 A

def powerSupply_On():
    powerSupply.write("OUTP ON")

def powerSupply_Off():
    powerSupply.write("INST P6V")
    powerSupply.write("OUTP OFF")
    powerSupply.write("INST P25V")
    powerSupply.write("OUTP OFF")
    powerSupply.write("INST N25V")
    powerSupply.write("OUTP OFF")

def clearSMU():
    smu.errorqueue.clear()
    smu.eventlog.clear()
    smu.smua.reset()
    smu.smub.reset()

def clear ():
    if name == 'nt':
        _ = system('cls')
    else:
        _ = system('clear')

def write_cmd(x):
    pico.write(bytes(x, 'utf-8'))
    time.sleep(0.05)

def bankNum(bank, bypass, folder):
    
    # if bypass is True and bank in [0,1,2,3]:
    #     select = 3
    # elif bypass is False and bank in [0,1,2,3]:
    #     select = 3
    # elif bypass is True and bank in [4,5,6,7]:
    #     select = 3
    # elif bypass is False and bank in [4,5,6,7]:
    #     select = 3
    # else:
    #     print('Bypass not selected')
    #     select = 0
    select = 3
    if bank == 0:        
        colStart = 0 + 1
        colEnd = colStart + 16 #17
        csIn = select                       # selects the switch case command for pi pico                                    
                
    elif bank == 1:
        colStart = 16 + 1
        colEnd = colStart + 16
        csIn = select

    elif bank == 2:
        colStart = 32 + 1
        colEnd = colStart + 16
        csIn = select

    elif bank == 3:
        colStart = 48 + 1
        colEnd = colStart + 16
        csIn = select

    elif bank == 4:
        colStart = 64 + 1
        colEnd = colStart + 16
        csIn = select

    elif bank == 5:
        colStart = 80 + 1
        colEnd = colStart + 16
        csIn = select

    elif bank == 6:
        colStart = 96 + 1
        colEnd = colStart + 16
        csIn = select

    elif bank == 7:
        colStart = 112 + 1
        colEnd = colStart + 16
        csIn = select

    fileLoc = str(p) + "\\Documents\\SkywaterData\\DOE2\\" + str(folder) + "\\Bank " + str(bank) + "\\idvsgcharData"
    rowStart = 0 + 1
    rowEnd = rowStart + 1 
    vg = 3.3
    
    if folder == 'currentSweep':                     
        measDelay = -1                      # measurement timer delay 
        nplc = 16/60                        # integration time. has to be faster than measDelay
        sweepList = (-1e-8, -1e-4, 50, 0)   # sweep parameters for currentSweep logarithmic sweep   
                                            # Low number, High number, number of points, asymptote
        send = rowStart, rowEnd, colStart, colEnd, sweepList, csIn, fileLoc,
        fileLoc, measDelay, nplc, vg
        return send
    elif folder == 'rtsEval':        
        timeTest = 20                       
        holdTime = 20  
        limitv = 3.3                        # voltage source limit of SMU
        rangev = 20                         # voltage measurement range of SMU
        period = timeTest / 2               # period of duty cycle for CTIA reset pin
        measDelay = 0.0005                  # measurement timer delay     # 2 kHz
        nplc = 0.027 / 60                   # integration time. has to be faster than measDelay
        Iref = -1e-5                        # Value applied to Iref. Id is Iref/10 
        sampRate = 1 / (measDelay * 1000)   # sample rate of the SMU

        send = rowStart, rowEnd, colStart, colEnd, csIn, fileLoc, measDelay,
        nplc, vg, Iref, timeTest, holdTime, sampRate, limitv, rangev, period    
        return send

def powerPico():                                                                    # Turns on the vPwr pins for pi pico
    write_cmd(str(7))                                                               # selects the switch case on the pico
    pico.read_until().strip().decode()                                              # confirms mode selected
    print('pico turned on the power') 
    time.sleep(2)

def doe1_ampCharacterization(amp, test):
    clearSMU()
    if amp in range(0,4):
        select = 1                                                            # NMOS Op-Amp
    elif amp in range(4,8):
        select = 2                                                            # PMOS Op-Amp

    data = pd.DataFrame(data=[], index=[], columns=["vIn", "vOut"])           #create dataframe

    
    powerSupply_Set("P25V", "5.2", "1.0")
    powerSupply_On()
    write_cmd(f"{7}")
    commandRX, rowRX, columnRX = tuple(pico.read_until().strip().decode().split(','))                            # confirms pico is on
    time.sleep(1)
    print("Power is turned on.")
    # powerSupply_Set("P6V", "3.3", "1.0")
    # powerSupply_On()
    # powerSupply_Set("N25V", "1.2", "1.0")
    # powerSupply_On()

    smu.smua.OUTPUT_DCVOLTS          # SMU 1 is set to apply voltage
    smu.smub.OUTPUT_DCAMPS           # SUM 2 is set to measure voltage
    # smu._write(value='smua.source.output = smua.OUTPUT_OFF')
    # smu._write(value='smub.source.output = smub.OUTPUT_OFF')
    time.sleep(1)
    write_cmd(f"{select}")  
    time.sleep(0.5)
    commandRX, rowRX, columnRX = tuple(pico.read_until().strip().decode().split(','))                            # confirms amp characterization is selected
    # if commandRX == 1 or commandRX == 2:
    print('pico selected amp characterization procedure.')
    vList = (0, 3.3, 50)
    # vList = (0, .3, 30)
    delay = 0
    t_int = 0.005
    smu._write(value = "smub.measure.autozero = smub.AUTOZERO_AUTO")
    smu._write(value='smua.source.output = smua.OUTPUT_ON')
    smu._write(value='smub.source.output = smub.OUTPUT_ON')
    time.sleep(1)
    # smu.apply_voltage(smu.smua, 1.8)
    smu.smub.measure.v()
    # print(test)
    time.sleep(5)
    # start_time, end_time, transients = oscope.save_measurements_timed(3)
    data.vIn, data.vOut = smu.doe1AmpChar(smu.smub, smu.smua, vList, delay, t_int)
    print(data)
    plt.plot(data.vIn, data.vOut, label = '0.5 mA')
    plt.title("Vin vs Vout")
    plt.xlabel("Vin")
    plt.ylabel("Vout")
    plt.legend()
    plt.savefig(str(p) + "\\Documents\\SkywaterData\\DOE2\\ampCharacterization\\amp" + str(amp) + "_Vo_vs_Vin_testNumber_" + str(test) + ".png")
    fig = plt.show(block=False)
    plt.pause(3)
    plt.close(fig)
    commandTX = write_cmd(f"{9}")          
    # print(data)
    data.to_csv("~/Documents/SkywaterData/DOE2/ampCharacterization/amp" + str(amp) + '.csv')
    smu._write(value='smua.source.output = smua.OUTPUT_OFF')
    smu._write(value='smub.source.output = smub.OUTPUT_OFF')
    powerSupply_Off()
    return

def idvgsCharacterization(bank, dieX, dieY, bypass):
    currIn = []
    measVs = []
    measVI = []
    vGS = []
    spec = []
    idvgsData = pd.DataFrame(data=[], index=[], columns=[])  
    pltData = pd.DataFrame(data=[], index=[], 
                        columns=['Site', 'V_C Out', 'Vsg', 'Iref', 'Id', "V_iref",  'Temp(K)', 'Die X', 'Die Y',
                                    'Row', 'Column', 'Test Time (Sec)'])  
    # specData = pd.DataFrame(pd.read_csv('~\miniconda3\envs\\skywater\RTSeval\Files\RTS_Array_Cells.csv',
    #                     index_col=[0] , header=0), columns = ['W/L', 'Type'])
    debug = False
    row = 0
    folder = 'currentSweep'
    rowStart, rowEnd, colStart, colEnd, sweepList, csIn, fileLoc, fileLoc, measDelay, nplc, vg = bankNum(bank, bypass, folder)

    smu.apply_current(smu.smua, 0.0)
    smu.apply_current(smu.smub, 0.0)
    smu2.apply_current(smu2.smua, 0.0)
    powerSupply_Set("P25V", "5.333", "1.0")
    powerSupply_On()
    powerPico()
    start_total_time = time.time()
    plt.figure(figsize=(12,14))
    for row in range(rowStart, rowEnd):
        for col in range(colStart, colEnd):
            write_cmd(f"{csIn},{row},{col}")                                                   # selects the switch case on the pico
            commandRX = tuple(pico.read_until().strip().decode().split(','))
            if debug is True:
                print(commandRX)
            commandRX, rowRX, columnRX = commandRX
            rowRX = re.sub(r'[0-9]+$',
                    lambda x: f"{str(int(x.group())-1).zfill(len(x.group()))}",    # decrements the number in the row number
                    rowRX)  
            columnRX = re.sub(r'[0-9]+$',
                    lambda x: f"{str(int(x.group())-1).zfill(len(x.group()))}",    # decrements the number in the colimn number
                    columnRX)    
            print('pico confirmed: ' + str(commandRX))
            print('pico selected row: ' + str(rowRX))
            print('pico selected column: ' + str(columnRX))
            commandRX = int(pico.read_until().strip().decode())                             # confirms shift registers are loaded
            print(f'pico loaded shift register.')                           # confirms shift registers are loaded
            # spec = list(specData.iloc[col-1])
            currIn, measVI, measVs = smu.idvgsChar(smu.smub, smu.smua, sweepList, measDelay, nplc)
            currIn = [abs(ele) for ele in currIn]
            pltData["V_C Out"] = measVs
            pltData['Site'] = 'IU'
            # pltData['Type'] = spec[1]
            vSG = np.full_like(measVs, vg) - measVs 
            pltData["V_iref"] = measVI
            pltData["Vsg"] = vSG # [1.2 - measVs for i in range(len(measVs))]
            pltData["Iref"] = currIn
            pltData["Id"] = pltData["Iref"]/10
            # pltData["W/L"] = spec[0]
            pltData["Temp(K)"] = 295
            pltData["Die X"] = dieX
            pltData["Die Y"] = dieY
            # pltData["Gm"] = np.gradient(currIn, vGS)
            # grouped = pltData.groupby(pltData.Gm)
            # maxGm = max(np.gradient(pltData['Id'], pltData['Vgs'], edge_order=2))
            # vthData = grouped.get_group(max(pltData['Gm']))
            # pltData["Vth"] = (vthData.Vgs*maxGm - np.sqrt(abs(vthData.Id)))/maxGm
            pltData["Row"] = rowRX
            pltData['Column'] = columnRX
            print(pltData)
            if debug is True:
                print(len(measVs))
                print(vGS)

            # if ((col % 2 == 1) and (row <= 97)):
               
            plt.subplot(2,1,1)
            plt.title("$I_{d}$ [A] vs $V_{C}$ Out")
            plt.plot(pltData["Id"], pltData["V_C Out"], label = "Id" + str(col))
            plt.xscale('log')
            plt.ylabel("$V_{C}$ [V]")
            plt.legend()
            plt.xlabel("$I_{d}$ [A]")

            plt.subplot(2,1,2)
            plt.title("$I_{d}$ [A] vs $V_{sg}$ Out")
            plt.plot(pltData["Id"], pltData["Vsg"], label = "Id" + str(col))
            plt.xscale('log')
            plt.ylabel("$V_{sg}$ [V]")
            plt.legend()
            plt.xlabel("$I_{d}$ [A]")


        plt.figtext(.35, .95, "$I_{Ref}$ = " + str(sweepList[0]) 
                    + " A to " + str(sweepList[1]) + " A", fontsize = 15)
        plt.figtext(.4, .92, "Current Sweep", fontsize = 15)
        plt.savefig(fileLoc + "R" + rowRX + 'C' + columnRX + "currentSweep.png")
        plt.tight_layout()
        plt.show(block = False)
        plt.close()

        currIn = []
        measVs = []
        measVI = []
        vGS = []
        commandRX=0
        idvgsData = pd.concat([idvgsData, pltData], axis = 0, ignore_index=True)
        idvgsData.to_csv(fileLoc + 'BAK.csv')
    
    
    write_cmd(str(9))                                                   # selects the switch case on the pico
    commandRX = pico.read_until().strip().decode()                                  # confirms mode selected
    print('pico confirmed: ' + str(commandRX) + ' and reset the shift registers')   

    end_total_time = time.time()
    test_time = end_total_time - start_total_time
    idvgsData.at[0, 'Test Time (Sec)'] = test_time
    idvgsData.to_csv(fileLoc + dt_string + '.csv')
    # print(idvgsData)
    smu._write(value='smua.source.output = smua.OUTPUT_OFF')
    smu._write(value='smub.source.output = smub.OUTPUT_OFF')
    smu2._write(value='smua.source.output = smua.OUTPUT_OFF')
    powerSupply_Off()
    return

def rtsEval(bank, dieX, dieY, bypass):
    clearSMU()
    rtsData = pd.DataFrame(data=[], index=[], columns=[]) 
    # specData = pd.DataFrame(pd.read_csv('~\miniconda3\envs\\testequ\RTSeval\Files\RTS_Array_Cells.csv',
    #                  index_col=[0] , header=0), columns = ['W/L', 'Type'])
    rowStart, rowEnd, colStart, colEnd, csIn, fileLoc, measDelay, nplc, vg, Iref, timeTest, holdTime, sampRate, limitv, rangev, period = bankNum(bank, bypass)


    powerSupply_Set("P25V", "5.333", "1.0")
    powerSupply_On()
    powerPico()  

    RTSCounter = 0                                                                # Counter variable for RTS detection(Jay Kim 06/06/23 9:04PM)
    SlowTrapCounter = 0                                                           # Counter variable for SlowTrapRTS detection(Jay Kim 06/06/23 9:04PM)
    DeviceCounter = 0                                                             # Counter variable for Device Counter(Jay Kim 06/06/23 9:04PM)
    for row in range(rowStart, rowEnd):
        for col in range(colStart, colEnd):
            DeviceCounter += 1                                                    #Device Counter
            print('Device Count:', DeviceCounter)
            vOut = pd.DataFrame(data=[], index=[], columns=[])
            # start_total_time = time.time()
            write_cmd(f"{csIn},{row},{col}")                                                   # selects the switch case on the pico
            commandRX, rowRX, columnRX = tuple(pico.read_until().strip().decode().split(','))
            # end_command_time = time.time()
            rowRX = re.sub(r'[0-9]+$',
                    lambda x: f"{str(int(x.group())-1).zfill(len(x.group()))}",    # decrements the number in the row number
                    rowRX)  
            columnRX = re.sub(r'[0-9]+$',
                    lambda x: f"{str(int(x.group())-1).zfill(len(x.group()))}",    # decrements the number in the colimn number
                    columnRX)    
            print('pico confirmed: ' + str(commandRX))
            print('pico selected row: ' + str(rowRX))
            print('pico selected column: ' + str(columnRX))
            # start_response_time = time.time()
            commandRX = int(pico.read_until().strip().decode())                             # confirms shift registers are loaded
            print(f'pico loaded the shift registers')                           # confirms shift registers are loaded
            # end_response_time = time.time()
            # start_voltage_sweep = time.time()
            # spec = list(specData.iloc[col - 1])
            smu._write(value = "smua.measure.autozero = smua.AUTOZERO_AUTO")
            smu._write(value = "smua.source.output = smub.OUTPUT_ON")
            smu.smua.measure.v()
            smu.apply_current(smu.smub, Iref)
            smu._write(value="node[2].smua.source.func = smua.OUTPUT_DCAMPS")
            smu._write(value="node[2].smua.source.output = smua.OUTPUT_ON")
            # smu2.apply_current(smu2.smua, 0.0)
            time.sleep(holdTime)
            print("Starting Test")
            write_cmd(f"{5},{timeTest}, {period}")  
            vOut['V_C Out'] = smu.sourceA_measAB(smu.smub, smu.smua, Iref, timeTest, holdTime, measDelay, nplc, rangev, limitv)     # run the script on smu
            vOut['Vsg'] = np.full_like(vOut['V_C Out'], vg) - vOut['V_C Out']
            vOut['Id'] = -Iref/10
            vOut['Sample_Rate(kHz)'] = sampRate
            vOut['Ticks'] = np.linspace(0, timeTest, len(vOut['V_C Out'])) 
            vOut['Column'] = columnRX
            vOut['Row'] = rowRX
            # vOut['W_L'] = spec[0] 
            # vOut['Type'] = spec[1] 
            vOut['DieX'] = dieX
            vOut['DieY'] = dieY
            print(len(vOut))
            rtsData = pd.concat([rtsData, vOut], axis = 0, ignore_index=True)           # save the new data with old data
            sig = savgol_filter(vOut["V_C Out"], window_length=51, polyorder=3)
            y1, x1 = np.histogram(sig, bins=50)
            peak = find_peaks(y1, width=1, height=100, distance=5)
            YMAX = y1[peak[0]]
            XMAX = x1[peak[0]]
            if len(peak[0]) >= 2:
                SlowTrapCounter += 1                                 
                for k in range(0, len(peak[0])):
                    if y1[peak[0][k]] == max(YMAX):
                        steadystate = k
                rtsAmplitude = x1[peak[0]] - x1[peak[0][steadystate]]
                rtsAmplitude = rtsAmplitude[rtsAmplitude != 0.]
                peaks, _ = find_peaks(sig, width=5, prominence=np.abs(min(rtsAmplitude)),      # find peaks of the filtered signal
                                   rel_height=0.5)
                peaks2, _ = find_peaks(-sig, width=5, prominence=np.abs(min(rtsAmplitude)))    # find peaks of the negative filtered signal

                results_W, results_WH, results_ips, results_rps= peak_widths(sig,           # find the peak widths (capture time)
                                                                            peaks, rel_height=0.5)
                results_NW, results_NWH, results_Nips, results_Nrps = peak_widths(-sig,     # find the valley widths (emission time)
                                                                                peaks2, rel_height=0.5)
                
                                                                                            # capture and emission maybe flipped depending on signal
            else: 
                peaks = []

            if len(peaks) >= 2:
                # print(xMax, ' ', yMax)
                # rtsAmplitude = np.round(xMax[1]-xMax[0], 6)
                RTSCounter += 1                                                             #RTS Counter
                plt.figure(figsize=(12,14))
                plt.subplot(3, 1, 1)
                debug = False
                if debug is False:
                    plt.plot(vOut['Ticks'], vOut['V_C Out'], label = "$V_{C}$ Out")
                    plt.plot(vOut.Ticks, sig, label = "Filterd Signal")
                    plt.xlabel("Time (sec)")
                else:
                    plt.plot(vOut['Vsg'], lbel='Vsg')
                    plt.plot(sig, label='Filtered Signal')
                    plt.plot(peaks, sig[peaks], 'x', color='red')
                    plt.plot(peaks2, sig[peaks2], 'x', color='green')
                    plt.hlines(results_WH, results_ips, results_rps, color="C2")
                    plt.xlabel('Data Points')
                plt.title("RTS Data: Col: " + str(col) + " Row: " + str(row)) # spec[0]) + " " + str(spec[1]))
                plt.ylabel("$V_{sg}$ [V]")
                plt.legend()

                plt.subplot(3,2,3)

                frq, P1d = welch(vOut.Vsg, fs=2000, window='hann', nperseg=20000,               #  Compute PSD using welch method
                                noverlap=None, nfft=20000)
                p1dSmooth = savgol_filter(P1d, window_length=5, polyorder=1)

                plt.yscale('log')
                plt.title('1/f Noise')
                plt.ylabel('$S_{id}$' + '($V^2$/Hz)')
                plt.xlabel("Frequency (Hz)")
                plt.xscale('log')
                plt.plot(frq[5:], P1d[5:])
                plt.plot(frq[5:], p1dSmooth[5:])

                # plt.subplot(2,1,2)
                plt.subplot(3, 2, 4)    
                plt.hist(vOut['Vsg'], label = "$V_{sg}$", histtype="stepfilled", bins=50)
                plt.hist(sig, label = 'Filtered Signal', histtype="stepfilled", bins=50)
                # plt.plot(xMax, yMax, 'x')
                plt.plot(XMAX, YMAX, 'o')
                plt.ylabel("Frequency")
                plt.xlabel("$V_{sg}$ [V]")
                plt.title('RTS Amplitude = ' + str(rtsAmplitude) + ' (V)')
                plt.legend()

                plt.subplot(3, 2, 5)
                plt.hist(results_W/2000, bins=50)
                meanTauE = np.mean(results_W)/2000
                plt.xlabel('Time (Sec)')
                plt.ylabel('Frequency')
                plt.title('Mean emission time: ' + str(meanTauE))

                plt.subplot(3, 2, 6)
                plt.hist((results_NW)/2000, bins=50)
                meanTauC = np.mean(results_NW)/2000
                plt.xlabel('Time (Sec)')
                plt.ylabel('Frequency')
                plt.title('Mean capture time: ' + str(meanTauC))
                
                plt.figtext(.5, .95, "$V_{g}$ = " + str(vg) +" V, $V_{dd}$ = "+ str(vg) + " V, Samp Rate = " + str(sampRate) + " kHz, $I_{d}$ = " + str(Iref) +
                            ' A', horizontalalignment='center', fontsize = 10)
                plt.savefig(fileLoc + "_C" + columnRX + "R" + rowRX + " " + dt_string + ".png")
                plt.tight_layout()
                fig1 = plt.show(block = False)
                # plt.pause(.5)
                plt.close(fig1)
            # else:
            #     rtsAmplitude = "???"
            
            vOut = vOut.reset_index(drop = True, inplace=True)
            smu._write(value='smua.source.output = smua.OUTPUT_OFF')
            smu._write(value='smub.source.output = smub.OUTPUT_OFF')
            smu._write(value="node[2].smua.source.output = smua.OUTPUT_OFF")
        rtsData.to_csv(fileLoc + '_Loop'+ rowRX + '.csv')                                   # save after row completes
        # rtsData.to_feather(fileLoc + '_Row'+ rowRX + '.feather')   
        rtsData = rtsData.reset_index(drop=True, inplace=True)                              # delete data frame after row completes
    write_cmd(str(9))                                                   # selects the switch case on the pico
    commandRX = pico.read_until().strip().decode()                                  # confirms mode selected
    print('pico reset the shift registers')
    # rtsData.to_csv(fileLoc + dt_string + '.csv')
    print('Slow Trap Count:', SlowTrapCounter)
    print('RTS Count:', RTSCounter)
    totalRTS = SlowTrapCounter/DeviceCounter *100
    refinedRTS = RTSCounter/DeviceCounter *100
    print('totalRTS: ', totalRTS)
    print('refinedRTS: ', refinedRTS)
    rtsData.at[0, 'totalRTS'] = totalRTS
    rtsData.at[0, 'refinedRTS'] = refinedRTS
    return rtsData

def doe1_ShiftRegister(seconds):
    # oscope.set_thresholds(3.1, 3.5, 1)          # tells oscope the clock is set to HIGH
    # oscope.set_thresholds(3.5, 4, 2)            # watches vertical SR for upsets
    # oscope.set_thresholds(3.5, 4, 3)            # watches horizontal SR for upets
    # oscope.load_setup("SR_SEU.setup?")              # loads the setup for this tets

    powerSupply_Set("P25V", "5.2", "1.0")
    powerSupply_On()
    write_cmd(f"{7}")
    commandRX, rowRX, columnRX = tuple(pico.read_until().strip().decode().split(','))                            # confirms pico is on
    time.sleep(1)
    print("Power is turned on.")
    write_cmd(f"{8}")  
    time.sleep(0.5)
    commandRX = tuple(pico.read_until().strip().decode())  
    print('pico selected SEU Shift Register procedure.')
    # h_upsets, v_upsets = oscope.report_transients(seconds)    # Script that tells oscope to count triggers over test period
    time.sleep(5)
    # time.sleep(seconds)
    write_cmd(f"{8}")
    time.sleep(0.5)
    commandRX = tuple(pico.read_until().strip().decode()) 
    powerSupply_Off()


# Test selection script
test = int(input("Which test are you running? "))

try:
    if test == 1:
        print("Amp Characterization is selected.")
        bank = int(input("Which amp are you testing? "))
        doe1_ampCharacterization(bank, 1)               # (amp, test)

    elif test == 2:
        print("Current sweep test is selected.")
        bank = int(input("Which bank are you testing? "))
        idvgsCharacterization(bank, '2E', '6', True)   # (bank, DieX, DieY, Bypass)
        
    elif test == 3:        
        print("RTS Evaluation test is selected.")
        bank = int(input("Which bank are you testing? "))
        rtsEval(bank, '2E', '6', True)                  # (bank, DieX, DieY, Bypass)
        
    elif test == 4:
        print("Selected Shift Register SEU Test")
        fileLoc = str(p) + "/Documents/LBNL2023/ShiftRegisterSEU/runlog.csv"
        path = Path(fileLoc)
        if path.exists():
            seuData = pd.read_csv(fileLoc) 
            testNumber = seuData.loc[len(seuData.Test)-1, "Test"] + 1 
        else:
            seuData = pd.DataFrame(data=[], index=[], columns=["Beam Energy", "Ion", "LET", "Fluence", "Ion Energy", 
                                                                "Flux", "Time", "HorizontalSR_Upsets", 
                                                                "VerticalSR_Upsets", "Test", "H_DataState",
                                                                "V_DataState", "H_XS", "V_XS"])
            testNumber = 0
        MeV = int(input("Beam MeV: "))
        ion = str(input("Beam Ion: "))
        test_time = int(input("Total Test time input: "))
        flux = int(input("Flux Input: "))
        h_dataS = str(input("Horizontal steady state condition: "))
        v_dataS = str(input("Vertical steady state condition: "))
        start_time = time.time()
        time.sleep(1)
        braggCurve = (pd.read_csv("~/Documents/LBNL2023/Bragg Curves/In-Vacuum_" + str(MeV) + "MeV_" + ion + ".csv",
                                        header=None, names=['Depth(um)', 'depth', 'LET', 'MEV'],
                                        index_col=False, skipfooter=1, engine='python'))
        print(braggCurve)
        let = braggCurve.LET.loc[braggCurve.depth ==  23.5]
        energy = braggCurve.MEV.loc[braggCurve.depth ==  23.5]
        print("LET: " + str(energy.values))
        
        # h_upsets, v_upsets = doe1_ShiftRegister_SEU(test_time)
        h_upsets, v_upsets = [4,5]

        fluence = flux * test_time
        seuData.at[testNumber, "Test"] = testNumber
        seuData.at[testNumber, "Beam Energy"] = MeV
        seuData.at[testNumber, "Ion"] = ion
        seuData.at[testNumber, "LET"] = let.values
        seuData.at[testNumber, "Ion Energy"] = energy.values
        seuData.at[testNumber, "HorizontalSR_Upsets"] = h_upsets
        seuData.at[testNumber, "VerticalSR_Upsets"] = v_upsets
        seuData.at[testNumber, "H_DataState"] = h_dataS
        seuData.at[testNumber, "V_DataState"] = v_dataS
        seuData.at[testNumber, "Time"] = test_time
        seuData.at[testNumber, "Flux"] = flux
        seuData.at[testNumber, "Fluence"] = fluence
        seuData.at[testNumber, "H_XS"] = h_upsets / fluence
        seuData.at[testNumber, "V_XS"] = v_upsets / fluence

        seuData.to_csv(fileLoc, index=False)
except:
    print("Abort")