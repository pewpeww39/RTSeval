import pyvisa
import time
from enum import Enum
import os
import glob

class MultipurposeAction(Enum):
    QuickWaveform = "qSaveWavMode"
    QuickScreen = "qSaveScrnMode"
class SweepMode(Enum):
    Normal = "trigNormal"
    Auto = "trigAuto"
class OScope:
    MAX_NUMBER_ACTIONS = 1000000

    def __init__(self, device="TCPIP0::localhost::inst0::INSTR"):
        
        rm = pyvisa.ResourceManager()
        self.device = rm.open_resource(device)#"TCPIP0::*****::inst0::INSTR")
        self.device.timeout = 2000
        self.device.clear()

        self.auto_mode = False
        self.set_sweep_mode(SweepMode.Normal)

        self.transient_folder = "\\\\K-EXR104A-10192\\Waveforms"
        
        # connect
        os.system(f"net use {self.transient_folder} /user:user pass")

    def set_screen_scale(self, amount):
        '''
        val: The the upper and (-val) lower bounds for the screen
        '''
        val /= 4
        self.device.write(f'SYSTem:CONTrol "Chan1Scale -1 {val}"')

    def set_offset(self, offset):
        '''
        offset: The the upper and (-val) lower bounds for the screen
        '''
        self.device.write(f'SYSTem:CONTrol "Chan1Offset -1 {offset}"')

    def set_thresholds(self, lower, upper, channel_number=1):
        '''
        offset: The the upper and (-val) lower bounds for the screen
        '''
        self.device.write(f'SYSTem:CONTrol "SupplTrig{channel_number}Level -1 {lower}"')
        self.device.write(f'SYSTem:CONTrol "Trig{channel_number}Level -1 {upper}"')

    def set_max_actions(self, number):
        self.device.write(f'SYSTem:CONTrol "EMailMax -1 {number}"')

    def save_measurements_counted(self, count):
        self.set_max_actions(count)
        self.start_quicktrigger()
        self.device.write(f'SYSTem:CONTrol "Interpolate -1 interpAuto"')

    def set_savefile_suffix(self, suffix):
        self.device.write(f'SYSTem:CONTrol "QuickSaveWaveIncrement -1 {suffix}"')

    def start_quicktrigger(self):
        self.device.write(f'SYSTem:CONTrol "QuickOnTrigger -1 on"')

    def stop_quicktrigger(self):
        self.device.write(f'SYSTem:CONTrol "QuickOnTrigger -1 off"')

    def save_measurements_timed(self, seconds):
        start_time = time.time()
        start_transients = self.get_trainsient_count()
        self.set_max_actions(OScope.MAX_NUMBER_ACTIONS)
        self.start_quicktrigger()
        try:
            time.sleep(seconds)
            self.stop_quicktrigger()
        except:
            self.stop_quicktrigger()
        end_time = time.time()
        end_transients = self.get_trainsient_count()

        transient_count = end_transients - start_transients
        
        print(f"Time: {end_time - start_time}")
        print(f"Transients Recorded: {transient_count}")

        return (start_time, end_time, transient_count)

    def set_sweep_mode(self, mode):
        self.device.write(f'SYSTem:CONTrol "SweepMode -1 {mode.value}"')

    def swap_sweep_mode(self):
        self.auto_mode = not self.auto_mode
        if self.auto_mode:
            self.set_sweep_mode(SweepMode.Normal)
        else:
            self.set_sweep_mode(SweepMode.Auto)

    def do_multipurpose(self):
        self.device.write(f'SYSTem:CONTrol "HkMultipurpose -1 "')

    def load_setup(self, filename, path=r"C:\\Users\\Public\\Documents\\Infiniium\\Setups\\"):
        self.device.write(f'SYSTem:CONTrol "OpenSetup -1 {path}{filename}"')

    def set_multipurpose_action(self, action):
        self.device.write(f'SYSTem:CONTrol "QuickMode -1 {action.value}"')

    def capture_screen(self):
        self.set_sweep_mode(SweepMode.Auto)
        self.set_multipurpose_action(MultipurposeAction.QuickScreen)
        self.do_multipurpose()
        self.set_multipurpose_action(MultipurposeAction.QuickWaveform)
        self.set_sweep_mode(SweepMode.Normal)
    
    def get_action_suffix(self):
        pass

    def get_trainsient_count(self):
        return len(glob.glob1(self.transient_folder,"*.h5"))
        
        
# oscope = OScope("TCPIP0::192.168.4.2::inst0::INSTR")

# print(oscope.device.query(f'COUNter3:CURRent?'))