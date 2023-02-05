from keithley2600 import Keithley2600
from BKPrecision import lib1785b as bk
import pandas as pd
import matplotlib.pyplot as plt
from os import system, name
from datetime import datetime
import serial
import sys
import time
import re
import numpy as np

def frange(start: int, end: int, step: float):
    """
    Generate a list of floating numbers within a specified range.

    :param start: range start
    :param end: range end
    :param step: range step
    :return:
    """
    numbers = np.linspace(start, end,(end-start)*int(1/step)+1).tolist()
    return [round(num, 2) for num in numbers]


dt_string = datetime.now().strftime("%Y_%m_%d-%I_%M_%S_%p")
smu = Keithley2600('TCPIP0::192.168.4.11::INSTR')               #set ip addr for smu

smuaV = frange(0, 10, 1)

output = smu.output_measurment(smu.smua, smu.smub, 0, 10, .01, smuaV, 0.001, -1, False)
#output = smu.voltage_sweep_dual_smu(smu.smua, smu.smub, smuaV,smuaV,0.001, 0.1, False)
print(smuaV)