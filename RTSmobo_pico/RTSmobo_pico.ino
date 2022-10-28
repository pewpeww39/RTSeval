#include <SPI.h>

#define debug false
#define vgHVP   0   // point Vg input voltage to High Voltage Pmos transistors
#define vgLVP   1   // point Vg input voltage to Low Voltage Pmos transistors
#define SCL     2   // Shift Register Clock
#define SDA_A   3   // Vertical Shift Register data pin
#define SDA_B   4   // Horizontal Shift Register data pin
#define RESET   5   // Reset shift registers
#define vddHV   6   // set Vdd input voltage to High Voltage transistors
#define vgLVN   7   // set VG input voltage to Low Voltage Nmos transistors
#define vgHVN   8   // set VG input voltaget to High Voltage Nmos Transistors
#define vddLV   9   // set VDD input voltage to Low Voltage Tansistors
#define ch1v0   10  // Select which amplifier output is on channel 1  vout0
#define ch1v4   11  // Select which amplifier output is on channel 1  vout4
#define ch2v1   12  // Select which amplifier output is on channel 2  vout1
#define ch2v5   13  // Select which amplifier output is on channel 2  vout5
#define ch3v2   14  // Select which amplifier output is on channel 3  vout2
#define ch3v6   15  // Select which amplifier output is on channel 3  vout6
#define ch4v3   16  // Select which amplifier output is on channel 4  vout3
#define ch4v7   17  // Select which amplifier output is on channel 4  vout7
#define Csin    18  // Vout amplifier bypass
#define smuSel  19  // Select SMU as precision nanoAmp Current Source
#define naSel   20  // Select on board nA Current Source
#define ch8v7   21  // Select which amplifier output is on channel 8  vout7
#define ch8v6   22  // Select which amplifier output is on channel 7  vout6
#define LED     25  // Pico LED
#define ch6v5   26  // Select which amplifier output is on channel 6  vout5
#define ch5v4   27  // Select which amplifier output is on channel 5  vout4


void setup()
{
  Serial.begin(115200);
  while (!Serial & debug == true) {
    yield();
  }
  
  definePins();   // set Pinmode for pins
  turnOff();      // digital write pins low
  
}


void loop()
{
  if (Serial.avialable() > 0){
    command = Serial.readString().toInt();
    Serial.println(command);
  }

  switch (command) {
    case 0: {   // set all pins low
      turnOff();
      flashLED();      
    }
    case 1: {                     // set channel 1 for amp characterization
      turnoff();                  // by setting the SR inputs to low
      digitalWrite(Csin, HIGH);   // close amp bypass
      digitalWrite(ch1v0, HIGH);  // chanel 1 has vout0
                                  // apply a voltage to vout1BYP jumper 
                                  // adjust gain to provide a 1:1 input/output
    }
  }
}

void flashLED(){
  digitalWrite(LED, HIGH);
  delay(500);
  digitalWrite(LED, LOW);
  delay(500);
  digitalWrite(LED, HIGH);
  delay(500);
  digitalWrite(LED, LOW);
}
void turnOff()
{
  digitalWrite(vgHVP, LOW);
  digitalWrite(vgLVP, LOW);
  digitalWrite(SCL, LOW);
  digitalWrite(SDA_A, LOW);
  digitalWrite(SDA_B, LOW);
  digitalWrite(RESET, LOW);
  digitalWrite(vddHV, LOW);
  digitalWrite(vgLVN, LOW);
  digitalWrite(vgHVN, LOW);
  digitalWrite(vddLV, LOW);
  digitalWrite(ch1v0, LOW);
  digitalWrite(ch1v4, LOW);
  digitalWrite(ch2v1, LOW);
  digitalWrite(ch2v5, LOW);
  digitalWrite(ch3v2, LOW);
  digitalWrite(ch3v6, LOW);
  digitalWrite(ch4v3, LOW);
  digitalWrite(ch4v7, LOW);
  digitalWrite(Csin, LOW);
  digitalWrite(smuSelect, LOW);
  digitalWrite(naSelect, LOW);
  digitalWrite(ch8v7, LOW);
  digitalWrite(ch7v6, LOW);
  digitalWrite(LED, LOW);
  digitalWrite(ch6v5, LOW);
  digitalWrite(ch5v4, LOW); 
}

void definePins()
{
  pinMode(vgHVP, OUTPUT);
  pinMode(vgLVP, OUTPUT);
  pinMode(SCL, OUTPUT);
  pinMode(SDA_A, OUTPUT);
  pinMode(SDA_B, OUTPUT);
  pinMode(RESET, OUTPUT);
  pinMode(vddHV, OUTPUT);
  pinMode(vgLVN, OUTPUT);
  pinMode(vgHVN, OUTPUT);
  pinMode(vddLV, OUTPUT);
  pinMode(ch1v0, OUTPUT);
  pinMode(ch1v4, OUTPUT);
  pinMode(ch2v1, OUTPUT);
  pinMode(ch2v5, OUTPUT);
  pinMode(ch3v2, OUTPUT);
  pinMode(ch3v6, OUTPUT);
  pinMode(ch4v3, OUTPUT);
  pinMode(ch4v7, OUTPUT);
  pinMode(Csin, OUTPUT);
  pinMode(smuSelect, OUTPUT);
  pinMode(naSelect, OUTPUT);
  pinMode(ch8v7, OUTPUT);
  pinMode(ch7v6, OUTPUT);
  pinMode(LED, OUTPUT);
  pinMode(ch6v5, OUTPUT);
  pinMode(ch5v4, OUTPUT);
}
