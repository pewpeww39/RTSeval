from driverTest import Keithley2600
import numpy as np

smu = Keithley2600('TCPIP0::192.168.4.11::INSTR')               #set ip addr for smu
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

vlist = frange(1, 5, .5)

smu.voltage_sweep_single_smu(smu.smua, vlist, 0.001, 1, False)