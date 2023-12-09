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
rm = pyvisa.ResourceManager()
picoCom = 'COM3'
# smu = Keithley2600('TCPIP0::192.168.4.11::INSTR')               # set ip addr for smu
smu = rm.open_resource('TCPIP0::192.168.4.11::inst0::INSTR')
chan1 = "smua"
chan2 = "smub"
smu.write(f"loadscript CurrentSweep")
smu.write(f"function configNodeA()")
smu.write(f"reset()")
smu.write(chan1 + ".source.func = "+ chan1 + ".OUTPUT_DCVOLTS")
smu.write(chan2 + ".source.func = "+ chan2 + ".OUTPUT_DCAMPS")
smu.write(f"smua.measure.autozero = smua.AUTOZERO_AUTO")
smu.write(f"smub.measure.autozero = smub.AUTOZERO_OFF")
for ele in [chan1, chan2]:
    smu.write(ele + ".source.limitv = 3.3")
    smu.write(ele + ".source.range = 20")
    smu.write(ele + ".measure.range = 20") 
    smu.write(ele + ".nvbuffer1.clear()")
    smu.write(ele + ".nvbuffer2.clear()")
    smu.write(ele + ".nvbuffer1.clearcache()")
    smu.write(ele + ".nvbuffer2.clearcache()")
    
# smu.write(f"smub.source.func = smub.OUTPUT_DCAMPS")
# smu.write(f"smua.source.limitv = 3.3")
# smu.write(f"smub.source.limitv = 3.3")
# smu.write(f"smua.source.range = 20")
# smu.write(f"smua.measure.range = 20")
# smu.write(f"smub.source.range = 20")
# smu.write(f"smub.measure.range = 20")
# smu.write(f"smua.measure.autozero = smua.AUTOZERO_AUTO")
# smu.write(f"smub.measure.autozero = smub.AUTOZERO_OFF")
smu.write(f"end")
smu.write(f"endscript")
smu.write(f"configNodeA()")
smu.write(chan1 + ".source.output = " + chan1 + ".OUTPUT_ON")
smu.write(f"CurrentSweep.save()")
smu.write(f"node[1].execute(CurrentSweep())")

    # def doe2AmpCharScript(self,                            # DOE 2 amp characterization evaluation
    #                 smu1: KeithleyClass,
    #                 smu2: KeithleyClass,
    #                 vList: Sequence[float],
    #                 delay: float,
    #                 t_int: float):
        
    #     # self.tsplink.reset()
    #     # masterNode = self.tsplink.master

    #     # smu3 = self.node[2].smua
    #     # smu4 = self.node[2].smub

    #     smu._write("loadscript CurrentSweep")
    #     smu._write("function configNode2()")
    #     smu._write("reset()")
        
    #     smu1.source.func = smu1.OUTPUT_DCVOLTS  
    #     smu2.source.func = smu2.OUTPUT_DCAMPS      # SUM 2 is set to measure voltage
    #     # self.node[2].smua.source.func = smu3.OUTPUT_DCAMPS          # SMU 1 is set to apply voltage
    #     # self.node[2].smub.source.func = smu4.OUTPUT_DCAMPS           # SUM 2 is set to measure voltage
    #     # self.node[2].smub.source.func = smu1.OUTPUT_DCVOLTS
    #     # self.node[2].smua.source.func = smu1.OUTPUT_DCAMPS
        
    #     # self.node[2].smua.source.output = smu1.OUTPUT_ON
    #     # self.node[2].smub.source.output = smu1.OUTPUT_ON 

    #     with self._measurement_lock:
    #         timestamp = []


    #         # for smu in [smu1, smu2]:
    #         #     # smu.source.rangei = pow(10, -6)
    #         #     self.set_integration_time(smu, t_int)
    #         #     # self.set_integration_time(smu, t_int)
    #         #     smu.source.limitv = 3.3
    #         #     smu.nvbuffer1.clear()
    #         #     smu.nvbuffer2.clear()
    #         #     smu.nvbuffer1.clearcache()
    #         #     smu.nvbuffer2.clearcache()
    #             # smu.nvbuffer2.appendmode = 1
    #         # self.node[2].set_integration_time(smu1, t_int)
    #         # self.node[2].smua.source.limitv = 3.3
    #         # self.node[2].smua.nvbuffer1.clear()
    #         # self.node[2].smua.nvbuffer2.clearcache()

    #         # self.node[2].set_integration_time(smu2, t_int)
    #         # self.node[2].smub.source.limitv = 3.3
    #         # self.node[2].smub.nvbuffer1.clear()
    #         # self.node[2].smub.nvbuffer2.clearcache()

    #         smu1.measure.autozero = smu1.AUTOZERO_AUTO
    #         smu2.measure.autozero = smu2.AUTOZERO_OFF
    #         smu2.nvbuffer2.collecttimestamps = 0
    #         smu1.measure.rangev = 20
    #         smu2.measure.rangev = 20
    #         smu._write("end")
    #         smu.write("CurrentSweep.save()")

    #         # self.node[2].smua.measure.autozero = smu1.AUTOZERO_AUTO
    #         # self.node[2].smub.measure.autozero = smu2.AUTOZERO_OFF
    #         # self.node[2].smub.nvbuffer2.collecttimestamps = 0
    #         # self.node[2].smua.measure.rangev = 2
    #         # self.node[2].smub.measure.rangev = 20

            
    #         self.trigger.blender[1].orenable = True                                 # triggers when either stimuli are true (True = or statement)
    #         self.trigger.blender[1].stimulus[1] = smu1.trigger.PULSE_COMPLETE_EVENT_ID
    #         self.trigger.blender[1].stimulus[2] = smu1.trigger.ARMED_EVENT_ID

    #         self.trigger.blender[2].orenable = True                                 # triggers when either stimuli are true (True = or statement)
    #         self.trigger.blender[2].stimulus[1] = smu1.trigger.SOURCE_COMPLETE_EVENT_ID
    #         self.trigger.blender[2].stimulus[2] = self.trigger.EVENT_ID
            
    #         # self.trigger.blender[3].ornable = True
    #         # self.trigger.blender[3].stimulus[1] = self.tsplink.trigger[1].EVENT_ID

    #         start, stop, step =  vList
    #         smu1.trigger.source.linearv(start, stop, step)
    #         smu1.trigger.source.action = smu1.ENABLE
    #         smu1.trigger.source.stimulus = self.trigger.blender[1].EVENT_ID# self.trigger.blender[1].EVENT_ID
    #         smu1.trigger.measure.action = smu1.ENABLE # ASYNC                      # enable synchronous measurements
    #         smu1.trigger.measure.v(smu1.nvbuffer2)                                # measure current and voltage on trigger, store in buffer of smu
    #         smu1.trigger.measure.stimulus = smu1.trigger.SOURCE_COMPLETE_EVENT_ID
    #         smu2.trigger.source.action = smu2.DISABLE                               # disable channel b source
    #         smu2.trigger.measure.action = smu2.ASYNC                                # enable smu
    #         smu2.trigger.measure.v(smu2.nvbuffer2)                                  # measure current and voltage on trigger, store in buffer of smu
    #         smu2.trigger.measure.stimulus = smu1.trigger.SOURCE_COMPLETE_EVENT_ID

    #         # self.tsplink.trigger[1].stimulus = smu1.trigger.SOURCE_COMPLETE_EVENT_ID
    #         # self.tsplink.trigger[1].mode = self.tsplink.TRIG_BYPASS

    #         # self.node[2].smua.trigger.source.action = smu1.DISABLE                               # disable channel b source
    #         # self.node[2].smua.trigger.measure.action = smu1.ASYNC                                # enable smu
    #         # self.node[2].smua.trigger.measure.v(smu1.nvbuffer1)                                  # measure current and voltage on trigger, store in buffer of smu
    #         # self.node[2].smua.trigger.measure.stimulus = self.tsplink.trigger[1].EVENT_ID
      
    #         smu1.measure.delay = 0.001
    #         smu2.measure.delay = 0.001
    #         # self.node[2].smua.measure.delay = 0.001
          
    #         smu1.trigger.count = step                                               # number of triggers for pulse
    #         smu1.trigger.arm.stimulus = self.trigger.EVENT_ID                    # sweep start trigger
    #         smu1.trigger.arm.count = 1    
    #         smu1.trigger.endpulse.action = smu1.SOURCE_HOLD                       # pulse action
    #         smu1.trigger.endpulse.stimulus = smu1.trigger.MEASURE_COMPLETE_EVENT_ID # initiate pulse
    #         smu1.trigger.endsweep.action = smu1.SOURCE_IDLE                       # turn off source after sweep 
    #         # self.node[1].smub.trigger.count = step                                                # number of triggers for pulse
    #         # self.node[1].smub.trigger.arm.stimulus = self.trigger.EVENT_ID                    # sweep start trigger
    #         # self.node[1].smub.trigger.arm.count = 1 
    #         # self.node[1].smub.trigger.endpulse.action = smu2.SOURCE_HOLD                       # pulse action
    #         # self.node[1].smub.trigger.endpulse.stimulus = smu2.trigger.MEASURE_COMPLETE_EVENT_ID # initiate pulse
    #         # self.node[1].smub.trigger.endsweep.action = smu2.SOURCE_IDLE                       # turn off source after sweep 
    #         smu2.trigger.count = step                                                # number of triggers for pulse
    #         smu2.trigger.arm.stimulus = self.trigger.EVENT_ID                    # sweep start trigger
    #         smu2.trigger.arm.count = 1 
    #         smu2.trigger.endpulse.action = smu2.SOURCE_HOLD                       # pulse action
    #         smu2.trigger.endpulse.stimulus = smu2.trigger.MEASURE_COMPLETE_EVENT_ID # initiate pulse
    #         smu2.trigger.endsweep.action = smu2.SOURCE_IDLE   
    #         # self.node[2].smua.trigger.count = step                                               # number of triggers for pulse
    #         # self.node[2].smua.trigger.arm.stimulus = self.trigger.EVENT_ID                    # sweep start trigger
    #         # self.node[2].smua.trigger.arm.count = 1    
    #         # self.node[2].smua.trigger.endpulse.action = smu1.SOURCE_HOLD                       # pulse action
    #         # self.node[2].smua.trigger.endpulse.stimulus = smu1.trigger.MEASURE_COMPLETE_EVENT_ID # initiate pulse
    #         # self.node[2].smua.trigger.endsweep.action = smu1.SOURCE_IDLE                       # turn off source after sweep 
            
    #         for smu in [smu1, smu2]:
    #             smu.source.output = smu.OUTPUT_ON 
    #         smu1.trigger.initiate()                                                 # move into the armed layer
    #         smu2.trigger.initiate()
    #         # self.node[1].smua._write(value='smua.trigger.initiate()')
    #         self.send_trigger()                                                     # start the sweep
    #         # self.node[1]._write("*trg")
    #         # self.node[2]._write("*trg")
    #         # print('Configured')
    #         while self.status.operation.sweeping.condition == 0:                    # check if sweep has started 
    #             # print('waiting')
    #             self.trigger.wait(.001)
    #         while self.status.operation.sweeping.condition > 0:                     # check if sweep has ended
    #             # print('running')
    #             # self.waitcomplete()
    #             self.trigger.wait(0.001)
    #             # time.sleep(0.001)
    #             # self.display.trigger.clear()
    #         print('reading buffers')
    #         v_smu1 = self.read_buffer(smu1.nvbuffer2)
    #         v_smu2 = self.read_buffer(smu2.nvbuffer2)
    #         # v_smu3 = self.read_buffer(self.node[2].smua.nvbuffer1)
    #         for smu in [smu1, smu2]:
    #             smu.nvbuffer1.clear()
    #             smu.nvbuffer2.clear()
    #             smu.nvbuffer1.clearcache()
    #             smu.nvbuffer2.clearcache()
    #         print('returning data')
    #         # print(v_smu3)
    #         return v_smu1, v_smu2 #, v_smu3
    #     # return()
