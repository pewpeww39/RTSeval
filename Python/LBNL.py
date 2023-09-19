from keithleyDriver import Keithley2600
import time
import pandas as pd

def clearSMU():
    smu.errorqueue.clear()
    smu.eventlog.clear()
    smu.smua.reset()
    smu.smub.reset()

# Initialize the Keithley SMU
smu = Keithley2600('TCPIP0::192.168.4.11::INSTR')
clearSMU()

smu.smua.source.output = smu.smua.OUTPUT_ON # turn on SMUA
smu.smub.source.output = smu.smub.OUTPUT_ON

data = []
times = []

def save_data():
    global data
    global times
    df = pd.DataFrame({"data": data, "time": times})
    df.to_csv(f'{time.time()}.csv', index=False)
    data = []
    times = []

try:
    total_latchup_counts = 0

    current_threshold = -1.049e-10

    #threshold_hold_delay = 1 # the delay between measurements after one has triggered a threshold
    required_threshold_measurements = 8 # the amount of measurements that needs to be above the threshold
    current_threshold_measurements = 0 # the current amount of measurements that read above the threshold

    latchup_currents = [] # create an array to append latchup current values.

    smu.smua.source.levelv = 1 # sets SMUA source level to 1V

    while(True):
        # Your command goes here
        current = smu.smub.measure.i() # measures current at smub
        data.append(current)
        times.append(time.time())

        # current above threshold
        if(current > current_threshold):

            print(f"Above Threshold: {current} - {current_threshold_measurements} out of {required_threshold_measurements}")

            current_threshold_measurements += 1

            # wait to make sure current is latched or just a random spike
            #time.sleep(threshold_hold_delay)

            # check again to see if current held above threshold 
            if(current_threshold_measurements == required_threshold_measurements):

                # increment counter because latchup occured
                total_latchup_counts += 1

                print(f"Latch up occured. {total_latchup_counts} total")

                latchup_currents.append(current)

                # shut off device
                smu.smua.source.levelv = 0

                # wait to cool off
                time.sleep(1)

                # restart device
                smu.smua.source.levelv = 1

                # reset measurement count
                current_threshold_measurements = 0

                save_data()
        else:
            print(f"Below Threshold: {current}")
            current_threshold_measurements = 0
        

except KeyboardInterrupt:
    save_data()

print(f"There were {total_latchup_counts} latchups")