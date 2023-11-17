import serial
import sys
import traceback
import time
import re
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from keithleyDriver import Keithley2600
from os import system, name
from datetime import datetime
from pathlib import Path
from Oscope import OScope
import os
import pyvisa
rm = pyvisa.ResourceManager()

# datetime object containing current date and time


smu = Keithley2600('TCPIP0::192.168.4.11::INSTR') 
smu.write(QRY)              #set ip addr for smu

