from keithleyDriver import Keithley2600
import numpy as np
import math
import time
import pandas as pd
from datetime import datetime
from os import system, name
import serial
import matplotlib.pyplot as plt
import re
from scipy.signal import find_peaks, savgol_filter, peak_widths
from scipy.signal import argrelmax, welch
import pyvisa
from pathlib import Path

# rm = pyvisa.ResourceManager()
# smu = rm.open_resource('TCPIP0::192.168.4.11::inst0::INSTR')
# smu = Keithley2600('TCPIP0::192.168.4.11::inst0::INSTR')
# smu.write("node[1].execute(CurrentSweep)")
# smu.write("CurrentSweep())")
# smu.tsplink.reset()
# smu._write(value="CurrentSweep()")
p = Path.home()
p = str(p) + "\\Documents\\SkywaterData\\DOE2\\rtsData\\Bank 0\\"
vOut = pd.DataFrame(pd.read_csv(p + "rtsData_Loop0.csv")) 
sig = savgol_filter(vOut["V_C Out"], window_length=51, polyorder=3)
sig2 = savgol_filter(vOut["Vsg"], window_length=51, polyorder=3)
plt.figure(figsize=(8,11))
plt.subplot(2,1,1)
plt.plot(vOut['Ticks'], vOut['V_C Out'], label = "$V_{C}$ Out")
plt.plot(vOut.Ticks, sig, label = "Filterd Signal")
plt.xlabel("Time (sec)")
plt.title("RTS Data: Col: " + str(1) + " Row: " + str(1)) # spec[0]) + " " + str(spec[1]))
plt.ylabel("$V_{C}$ Out [V]")
plt.legend()

plt.subplot(2,1,2)
plt.plot(vOut['Ticks'], vOut['Vsg'], label = "$V_{sg}$")
plt.plot(vOut.Ticks, sig2, label = "Filterd Signal")
plt.xlabel("Time (sec)")
# plt.title("RTS Data: Col: " + str(1) + " Row: " + str(1)) # spec[0]) + " " + str(spec[1]))
plt.ylabel("$V_{sg}$ [V]")
plt.legend()
plt.figtext(.5, .95, "$V_{g}$ = " + str(3.3) +" V, $V_{dd}$ = "+ str(3.3) + " V, Samp Rate = " + str(2) + " kHz, $I_{d}$ = " + str(1) +
                            ' uA', horizontalalignment='center', fontsize = 10)
plt.savefig(p + "_C" + str(1) + "R" + str(1) + "Id=1uA.png")
plt.tight_layout()
plt.show(block=False)
plt.pause(3)
print(vOut["V_C Out"])