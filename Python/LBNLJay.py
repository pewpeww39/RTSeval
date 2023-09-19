from keithleyDriver import Keithley2600
import time

def clearSMU():
    smu.errorqueue.clear()
    smu.eventlog.clear()
    smu.smua.reset()
    smu.smub.reset()

# Initialize the Keithley SMU
smu = Keithley2600('TCPIP0::192.168.4.11::INSTR')
clearSMU()

smu.smua.source.output = smu.smua.OUTPUT_ON  # turn on SMUA
smu.smub.source.output = smu.smub.OUTPUT_ON

try:
    total_latchup_counts = 0
    current_threshold = -1.049e-10
    threshold_hold_delay = 1  # the delay between measurements after one has triggered a threshold
    required_threshold_measurements = 4  # the amount of measurements that need to be above the threshold
    current_threshold_measurements = 0  # the current amount of measurements that read above the threshold

    smu.smua.source.levelv = 1  # sets SMUA source level to 1V

    latchup_currents = []  # Create a list to store measured currents during latch-ups

    while True:
        current_values = []  # Create a list to store the four current measurements

        for i in range(required_threshold_measurements):
            current = smu.smub.measure.i()  # Measure current at smub
            current_values.append(current)  # Append the current measurement to the list
            time.sleep(threshold_hold_delay)  # Delay between measurements

            # Check if current is above threshold
            if current > current_threshold:
                print(f"Above Threshold: {current} - {current_threshold_measurements} out of {required_threshold_measurements}")
                current_threshold_measurements += 1

        # Check if the required number of measurements are above the threshold
        if current_threshold_measurements == required_threshold_measurements:
            # Increment counter because latch-up occurred
            total_latchup_counts += 1
            latchup_label = f"Latchup {total_latchup_counts}"
            print(f"{latchup_label} occurred. {total_latchup_counts} total")

            # Save the current measurements during latch-up
            latchup_currents.append((latchup_label, current_values))

            # Shut off device
            smu.smua.source.levelv = 0

            # Wait to cool off
            time.sleep(1)

            # Restart device
            smu.smua.source.levelv = 1

            # Reset measurement count
            current_threshold_measurements = 0
        else:
            print(f"Below Threshold: {current}")

except KeyboardInterrupt:
    # Save the measured current data during latch-ups to a file before exiting
    if latchup_currents:
        with open("latchup_currents.txt", "w") as file:
            for label, values in latchup_currents:
                file.write(f"{label}:\n")
                for current in values:
                    file.write(f"{current}\n")
    print(f"There were {total_latchup_counts} latch-ups")
