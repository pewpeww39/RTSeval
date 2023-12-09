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
p = str(p) + "\\Documents\\SkywaterData\\DOE2\\currentSweep\\Bank 0\\idvgscharData"
        
print(p)