import pyvisa
rm = pyvisa.ResourceManager()
# from PowerSupplyDriver import KeysightPS  
# rm.list_resources()  
powerSupply = rm.open_resource('TCPIP0::192.168.4.3::INSTR')  
# powerSupply = KeysightPS("TCPIP0::192.168.4.3::INSTR")  
    
def powerSupply_Set(channel, voltage, current):
    powerSupply.write("INST "+channel) # Select +6V output ch 1
    powerSupply.write("VOLT "+voltage) # Set output voltage to 3.0 V
    powerSupply.write("CURR "+current) # Set output current to 1.0 A

def powerSupply_On():
    powerSupply.write("OUTP ON")

def powerSupply_Off():
    powerSupply.write("INST P6V")
    powerSupply.write("OUTP OFF")
    powerSupply.write("INST N25V")
    powerSupply.write("OUTP OFF")


powerSupply_Set("P6V", "3.3", "1.0")
powerSupply_On()
# powerSupply_Off()

powerSupply_Set("N25V", "1.2", "1.0")
powerSupply_On()
# powerSupply_Off()
# print("Power is turned on.")
print("Power is turned off.")