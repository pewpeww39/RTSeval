#include <SPI.h>

#define debug           false
#define vgHVP           0   // point Vg input voltage to High Voltage Pmos transistors
#define vgLVP           1   // point Vg input voltage to Low Voltage Pmos transistors
#define HCLKin          2   // Shift Register Clock
#define Din             3   // Vertical Shift Register data pin
#define DHin            4   // Horizontal Shift Register data pin
#define resetBIN        5   // Reset shift registers
#define vpwrHV          6   // set Vdd input voltage to High Voltage transistors
#define vpwrLV          7   // set VG input voltage to Low Voltage Nmos transistors
#define vgHVN           8   // set VG input voltaget to High Voltage Nmos Transistors
#define vddLV           9   // set VDD input voltage to Low Voltage Tansistors
#define ch1_vooff       10  // Select which amplifier output is on channel 1  vout0
#define ch1vo1          11  // Select which amplifier output is on channel 1  vout4
#define CRSTbin         12  // Select which amplifier output is on channel 2  vout1
#define ch1vo3          13  // Select which amplifier output is on channel 2  vout5
#define ch1vo4          14  // Select which amplifier output is on channel 3  vout2
#define ch1vo5          15  // Select which amplifier output is on channel 3  vout6
#define ch1vo6          16  // Select which amplifier output is on channel 4  vout3
#define ch1vo7          17  // Select which amplifier output is on channel 4  vout7
#define Csin            18  // Vout amplifier bypass
#define vPwr            20  // 3.3V and 1.2V power switch
#define LED             25  // Pico LED

int command = 0;
int colSelect = 1;
int rowSelect = 1;
int horSR = 0;
int verSR = 0;
int holdRow = 0;
int clkPulse = 0;

uint32_t timer = millis();
uint32_t timerB = millis();
void setup()
{
  Serial.begin(115200);
  while (!Serial & debug == true) {
    yield();
  }
  definePins();   // set Pinmode for pins
  turnOff();      // digital write pins low
  flashLED();
}

void loop()
{
  if (Serial.available()) {
    String recvString = Serial.readString();

    int i1 = recvString.indexOf(',');
    int i2 = recvString.indexOf(',', i1 + 1);
    command = recvString.substring(0, i1).toInt();
    rowSelect = recvString.substring(i1 + 1, i2).toInt();
    colSelect = recvString.substring(i2 + 1).toInt();

    Serial.println(String(command) + "," + String(rowSelect) + "," + String(colSelect));
  }


  switch (command) {
    case 0: {   // Default Case
        break;
      }
    case 1: {                                 // Opamp Characterization
        digitalWrite(CRSTbin, LOW);
        digitalWrite(resetBIN, LOW);          // by setting the SR inputs to low
        waitFor(50);
        digitalWrite(resetBIN, HIGH);
        waitFor(50);
        for (int j = 129; j >= 1; j--) {      // for loop for the number of columns

          horSR = 1;                          // if it does set SDA_ to high
          verSR = 1;                          // same as above for vertical SR

          waitFor(10);
          digitalWrite(DHin, horSR);          // set SDA_A pin to horSR value
          digitalWrite(Din, verSR);           // set SDA_B pin to verSR value
          waitFor(10);
          digitalWrite(HCLKin, HIGH);         // set the SR clock Low
          digitalWrite(LED, HIGH);
          waitFor(10);
          digitalWrite(HCLKin, LOW);          // set the SR clock Low
          digitalWrite(LED, LOW);
          waitFor(10);
        }
        digitalWrite(Csin, LOW);              // close PMOS amp bypass
        flashLED();
        Serial.println(command);
        command = 0;
        if (debug == true) {
          Serial.println("Ready for NMOS OpAmp characterization");
        }
        break;
      }
    case 2: {                                 // Nmos opamp characterization
        command = 0;
        break;
      }
    case 3: {                                 // iref current sweep Characterization
        digitalWrite(CRSTbin, LOW);
        digitalWrite(Csin, LOW);              // close vout bypass
        digitalWrite(LED, LOW);
        if (debug == true) {
          Serial.println("H V");
        }
        digitalWrite(resetBIN, LOW);          // Flush the SR
        waitFor(50);
        digitalWrite(resetBIN, HIGH);
        waitFor(50);
        for (int j = 129; j >= 1; j--) {      // for loop for the number of columns
          if (colSelect == j) {               // check if j = desired column i.e. 0000...0100
            horSR = 1;                        // if it does set SDA_ to high
          } else {
            horSR = 1;                        // if not set it to low (most cases)
          }
          if (rowSelect == j) {
            verSR = 0;                        // same as above for vertical SR
          } else {
            verSR = 1;
          }


          waitFor(10);
          digitalWrite(DHin, horSR);          // set SDA_A pin to horSR value
          digitalWrite(Din, verSR);           // set SDA_B pin to verSR value
          waitFor(10);
          digitalWrite(HCLKin, HIGH);         // set the SR clock Low
          digitalWrite(LED, HIGH);
          waitFor(10);
          digitalWrite(HCLKin, LOW);          // set the SR clock Low
          digitalWrite(LED, LOW);
          waitFor(10);
          digitalWrite(DHin, HIGH);           // set SDA_A pin to horSR value
          digitalWrite(Din, HIGH);

          if (debug == true) {
            Serial.print(horSR );
            Serial.print(' ');
            Serial.println(verSR);
          }
        }
        flashLED();
        int commandTX = 1;
        Serial.println(commandTX);
        commandTX = 0;
        command = 0;
        colSelect = 0; 
        rowSelect = 0;
        break;
      }

    case 4: {                                 // rts Characterization
        digitalWrite(CRSTbin, LOW);
        digitalWrite(Csin, LOW);              // close vout bypass
        digitalWrite(LED, LOW);
        if (debug == true) {
          Serial.println("H V");
        }
        digitalWrite(resetBIN, LOW);          // Flush the SR
        waitFor(50);
        digitalWrite(resetBIN, HIGH);
        waitFor(50);
        for (int j = 129; j >= 1; j--) {      // for loop for the number of columns
          if (colSelect == j) {               // check if j = desired column i.e. 0000...0100
            horSR = 0;                        // if it does set SDA_ to high
          } else {
            horSR = 1;                        // if not set it to low (most cases)
          }
          if (rowSelect == j) {
            verSR = 0;                        // same as above for vertical SR
          } else {
            verSR = 1;
          }


          waitFor(10);
          digitalWrite(DHin, horSR);          // set SDA_A pin to horSR value
          digitalWrite(Din, verSR);           // set SDA_B pin to verSR value
          waitFor(10);
          digitalWrite(HCLKin, HIGH);         // set the SR clock Low
          digitalWrite(LED, HIGH);
          waitFor(10);
          digitalWrite(HCLKin, LOW);          // set the SR clock Low
          digitalWrite(LED, LOW);
          waitFor(10);
          digitalWrite(DHin, HIGH);           // set SDA_A pin to horSR value
          digitalWrite(Din, HIGH);

          if (debug == true) {
            Serial.print(horSR );
            Serial.print(' ');
            Serial.println(verSR);
          }
        }
        flashLED();
        int commandTX = 1;
        Serial.println(commandTX);
        commandTX = 0;
        command = 0;
        colSelect = 0; 
        rowSelect = 0;
        break;
      }

    case 5: {                                 // idvg, rts NMOS Characterization on The bypass
        // command, rowSelect, colSelect
        // command, timetest, period
        double timeTest =  rowSelect;
        double period = colSelect;
        double dutyCycle = .5;

        float cycles = timeTest / period;
        float openTime = period * dutyCycle;
        float integrateTime = (1 - dutyCycle) * period;  // = period - highTime
        waitFor(100);
        for (int j = cycles; j >= 1; j--) {
          digitalWrite(CRSTbin, LOW);          // ctia reset short closed
          digitalWrite(LED, HIGH);
          waitFor(openTime * 1000);
          digitalWrite(CRSTbin, HIGH);         // ctia reset open, integrate mode
          digitalWrite(LED, LOW);
          waitFor(integrateTime * 1000);
        }
        digitalWrite(CRSTbin, LOW);
        command = 0;
        break;
      }

    case 6: {                                   // idvg, rts PMOS Characterization on the bypass

        command = 0;
        break;
      }

    case 7: {
        digitalWrite(vpwrHV, HIGH);
        digitalWrite(vpwrLV, HIGH);
        //        int commandTX = 1;
        //        Serial.println(commandTX);
        command = 0;
        break;
      }

    case 8: {                                   // SEU test for Shift Registers
        digitalWrite(Csin, LOW);                // open NMOS amp bypass
        digitalWrite(LED, LOW);
        if (debug == true) {
          Serial.println("H V");
        }
        digitalWrite(resetBIN, LOW);            // Flush the SR
        waitFor(50);
        digitalWrite(resetBIN, HIGH);
        waitFor(50);
        horSR = 0;
        verSR = 0;
        for (int j = 129; j >= 1; j--) {        // for loop for the number of columns
          //            if (colSelect == 1) {   // check if j = desired column i.e. 0000...0100
          horSR = 1;                            // if it does set SDA_ to high
          //          } else {
          //            horSR = 1;              // if not set it to low (most cases)
          //          }
          //          if (rowSelect == 1) {
          //            verSR = 1;              // same as above for vertical SR
          //          } else {
          //            verSR = 0;
          //          }

          waitFor(10);
          digitalWrite(DHin, horSR);            // set SDA_A pin to horSR value
          digitalWrite(Din, verSR);             // set SDA_B pin to verSR value
          waitFor(10);
          digitalWrite(HCLKin, HIGH);           // set the SR clock Low
          digitalWrite(LED, HIGH);
          waitFor(10);
          digitalWrite(HCLKin, LOW);            // set the SR clock Low
          digitalWrite(LED, LOW);
          waitFor(10);
          if (horSR == 0) {
            horSR = 1;
          }
          else if (horSR == 1) {
            horSR = 0;
          }

          if (verSR == 0) {
            verSR = 1;
          }
          else if (verSR == 1) {
            verSR = 0;
          }
        }
        if (debug == true) {
          Serial.print(horSR );
          Serial.print(' ');
          Serial.println(verSR);
        }

        //        flashLED();
        int commandTX = 1;
        Serial.println(commandTX);
        commandTX = 0;
        command = 0;
        break;
      }


    case 9:
      turnOff();
      flashLED();
      command = 0;
      digitalWrite(resetBIN, LOW);
      digitalWrite(CRSTbin, HIGH);


      break;

    case 10:
      for (int j = 129; j >= 1; j--) {      // for loop for the number of columns

        waitFor(10);
        digitalWrite(DHin, 0);              // set SDA_A pin to horSR value
        digitalWrite(Din, 0);               // set SDA_B pin to verSR value
        waitFor(10);
        digitalWrite(HCLKin, HIGH);         // set the SR clock Low
        digitalWrite(LED, HIGH);
        waitFor(10);
        digitalWrite(HCLKin, LOW);          // set the SR clock Low
        digitalWrite(LED, LOW);
        waitFor(10);
      }
      //        flashLED();
      int commandTX = 1;
      Serial.println(commandTX);
      commandTX = 0;
      command = 0;
      break;
  }
}

void waitFor(int msec) {                      // delay command
  timerB = millis();
  while (int hold = true) {
    if (millis() - timerB >= msec) {
      hold == false;
      return;
    } else {}
  }
}

void flashLED() {                             // Flash Led command
  timer = millis();
  for (timer; millis() - timer <= 1500;) {
    if (millis() - timer <= 500) {
      digitalWrite(LED, HIGH);
    }
    if (millis() - timer > 500 & millis() - timer <= 1000) {
      digitalWrite(LED, LOW);
    }
    if (millis() - timer > 1000 & millis() - timer < 1500) {
      digitalWrite(LED, HIGH);
    }
    if (millis() - timer >= 1500) {
      digitalWrite(LED, LOW);
    }
  }
}
void turnOff()                                // Command to set the pins to default condition
{
  digitalWrite(vgHVP, LOW);
  digitalWrite(vgLVP, LOW);
  digitalWrite(HCLKin, LOW);
  digitalWrite(Din, LOW);
  digitalWrite(DHin, LOW);
  digitalWrite(resetBIN, LOW);
  digitalWrite(vpwrHV, LOW);
  digitalWrite(vpwrLV, HIGH);
  digitalWrite(vgHVN, LOW);
  digitalWrite(vddLV, LOW);
  digitalWrite(ch1_vooff, LOW);
  digitalWrite(ch1vo1, LOW);
  digitalWrite(CRSTbin, HIGH);
  digitalWrite(ch1vo3, LOW);
  digitalWrite(ch1vo4, LOW);
  digitalWrite(ch1vo5, LOW);
  digitalWrite(ch1vo6, LOW);
  digitalWrite(ch1vo7, LOW);
  digitalWrite(Csin, LOW);
  digitalWrite(LED, LOW);
  digitalWrite(vPwr, LOW);
}

void definePins()
{
  pinMode(vgHVP, OUTPUT);
  pinMode(vgLVP, OUTPUT);
  pinMode(HCLKin, OUTPUT);
  pinMode(Din, OUTPUT);
  pinMode(DHin, OUTPUT);
  pinMode(resetBIN, OUTPUT);
  pinMode(vpwrHV, OUTPUT);
  pinMode(vpwrLV, OUTPUT);
  pinMode(vgHVN, OUTPUT);
  pinMode(vddLV, OUTPUT);
  pinMode(ch1_vooff, OUTPUT);
  pinMode(ch1vo1, OUTPUT);
  pinMode(CRSTbin, OUTPUT);
  pinMode(ch1vo3, OUTPUT);
  pinMode(ch1vo4, OUTPUT);
  pinMode(ch1vo5, OUTPUT);
  pinMode(ch1vo6, OUTPUT);
  pinMode(ch1vo7, OUTPUT);
  pinMode(Csin, OUTPUT);
  pinMode(LED, OUTPUT);
  pinMode(vPwr, OUTPUT);
}
