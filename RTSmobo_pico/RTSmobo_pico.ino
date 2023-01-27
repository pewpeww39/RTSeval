#include <SPI.h>

#define debug           false
#define vgHVP           0   // point Vg input voltage to High Voltage Pmos transistors
#define vgLVP           1   // point Vg input voltage to Low Voltage Pmos transistors
#define HCLKin          2   // Shift Register Clock
#define Din             3   // Vertical Shift Register data pin
#define DHin            4   // Horizontal Shift Register data pin
#define resetBIN        5   // Reset shift registers
#define vddHV           6   // set Vdd input voltage to High Voltage transistors
#define vgLVN           7   // set VG input voltage to Low Voltage Nmos transistors
#define vgHVN           8   // set VG input voltaget to High Voltage Nmos Transistors
#define vddLV           9   // set VDD input voltage to Low Voltage Tansistors
#define ch1_vooff       10  // Select which amplifier output is on channel 1  vout0
#define ch1vo1          11  // Select which amplifier output is on channel 1  vout4
#define ch1vo2          12  // Select which amplifier output is on channel 2  vout1
#define ch1vo3          13  // Select which amplifier output is on channel 2  vout5
#define ch1vo4          14  // Select which amplifier output is on channel 3  vout2
#define ch1vo5          15  // Select which amplifier output is on channel 3  vout6
#define ch1vo6          16  // Select which amplifier output is on channel 4  vout3
#define ch1vo7          17  // Select which amplifier output is on channel 4  vout7
#define Csin            18  // Vout amplifier bypass
#define LED             25  // Pico LED

int command = 0;
int colSelect = 0;
int rowSelect = 0;
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
    command = Serial.readString().toInt();
    Serial.println(command);

    while (command == 3) {                  // hold amp characterization command for column select
      colSelect = Serial.readString().toInt();
      if (colSelect > 0) {
        break;
      }
    }
  }


  switch (command) {
    case 0: {   // set all pins low
        break;
      }
    case 1: {                               // nmos opamp characterization
        turnOff();
        digitalWrite(resetBIN, LOW);        // by setting the SR inputs to low
        digitalWrite(Csin, HIGH);           // close NMOS amp bypass
        flashLED();
        command = 0;
        if (debug == true) {
          Serial.println("Ready for NMOS OpAmp characterization");
        }
        break;
      }
    case 2: {                               // pmos opamp characterization
        turnOff();
        digitalWrite(resetBIN, LOW);
        digitalWrite(Csin, LOW);              // close PMOS amp bypass
        flashLED();
        command = 0;
        if (debug == true) {
          Serial.println("Ready for PMOS OpAmp characterization");
        }
        break;
      }
    case 3: {                               // Current Source Characterization
        digitalWrite(Csin, HIGH);             // close NMOS amp bypass
        Serial.println(colSelect);          // tell CPU what column was selected
        digitalWrite(LED, LOW);
        if (debug == true) {
          Serial.println("H V");
        }          
        digitalWrite(resetBIN, LOW);        // Flush the SR
        waitFor(10);
        digitalWrite(resetBIN, HIGH);
        waitFor(10);
        for (int j = 256; j > 0; j--) {     // for loop for the number of columns
          if (colSelect == j) {             // check if j = desired column i.e. 0000...0100
            horSR = 1;                      // if it does set SDA_ to high
          } else {
            horSR = 0;                      // if not set it to low (most cases)
          }
          if (rowSelect == j) {
            verSR = 1;                      // same as above for vertical SR
          } else {
            verSR = 0;
          }


          digitalWrite(HCLKin, HIGH);          // set the SR clock high
          digitalWrite(LED, HIGH);
          waitFor(10);
          digitalWrite(DHin, horSR);       // set SDA_A pin to horSR value
          digitalWrite(Din, verSR);       // set SDA_B pin to verSR value
          waitFor(10);
          digitalWrite(HCLKin, LOW);           // set the SR clock Low
          digitalWrite(LED, LOW);
          waitFor(10);

          if (debug == true) {
            Serial.print(horSR );
            Serial.print(' ');
            Serial.println(verSR);
          }
        }
        flashLED();
        command = 0;
        int commandTX = 1;
        Serial.println(commandTX);
        commandTX = 0; 
        colSelect = 0; // colSelect + 1;
        break;
      }
      case 4: {                               // Clock, Shift Register Characterization
        digitalWrite(Csin, HIGH);             // close NMOS amp bypass
        Serial.println(colSelect);          // tell CPU what column was selected
        digitalWrite(LED, LOW);
        if (debug == true) {
          Serial.println("H V");
        }
        digitalWrite(resetBIN, LOW);        // Flush the SR
        waitFor(1);
        digitalWrite(resetBIN, HIGH);
        
        waitFor(1);

        
        for (int j = 257; j >= 1; j--) {     // for loop for the number of columns
          if ( colSelect == j) {             // check if j = desired column i.e. 0000...0100
            horSR = HIGH;                      // if it does set SDA_ to high
          } else {
            horSR = LOW;                      // if not set it to low (most cases)
          }
          if (rowSelect == j) {
            verSR = HIGH;                      // same as above for vertical SR
          } else {
            verSR = LOW;
          }

          digitalWrite(HCLKin, LOW);           // set the SR clock Low
          digitalWrite(LED, LOW);
          waitFor(1);
          digitalWrite(DHin, horSR);       // set SDA_A pin to horSR value
          digitalWrite(Din, verSR);       // set SDA_B pin to verSR value
          waitFor(1);
          digitalWrite(HCLKin, HIGH);           // set the SR clock Low
          digitalWrite(LED, HIGH);
          waitFor(1);
          digitalWrite(DHin, LOW);       // set SDA_A pin to horSR value
          digitalWrite(Din, LOW);          


          
          if (debug == true) {
            Serial.print(horSR );
            Serial.print(' ');
            Serial.println(verSR);
          }
        }
        flashLED();
        command = 0;
        int commandTX = 1;
        Serial.println(commandTX);
        commandTX = 0;
        //colSelect = 1; // colSelect + 1;
        break;
      }

      case 5: {
        digitalWrite(Csin, HIGH);
        digitalWrite(resetBIN, LOW);
        break;
      }

    //    case 3: {
    //        colSelect++;
    //        command = 0;
    //        break;
    //      }
    //    case 4: {                             // increment through rows and hold columns
    //        digitalWrite(LED, LOW);
    //        timerB = millis();
    //        if (debug == true) {
    //          Serial.println("H V");
    //        }
    //        for (int j = 256; j > 0; j--) {    // for loop for the number of columns
    //          if (colSelect == j) {     // check if 2^j = desired column i.e. 0000...0100
    //            horSR = 1;                      // if it does set SDA_ to high
    //          } else {
    //            horSR = 0;                      // if not set it to low (most cases)
    //          }
    //          if (rowSelect == j) {
    //            verSR = 1;                      // same as above for vertical SR
    //          } else {
    //            verSR = 0;
    //          }
    //
    //          digitalWrite(resetBIN, LOW);        // Flush the SR
    //          waitFor(10);
    //          digitalWrite(resetBIN, HIGH);
    //          waitFor(10);
    //          digitalWrite(HCLKin, HIGH);          // set the SR clock high
    //          digitalWrite(LED, HIGH);
    //          waitFor(10);
    //          digitalWrite(Din, horSR);       // set SDA_A pin to horSR value
    //          digitalWrite(DHin, verSR);       // set SDA_B pin to verSR value
    //          waitFor(10);
    //          digitalWrite(HCLKin, LOW);           // set the SR clock Low
    //          digitalWrite(LED, LOW);
    //          waitFor(10);
    //
    //          if (debug == true) {
    //            Serial.print(horSR );
    //            Serial.print(' ');
    //            Serial.println(verSR);
    //          }
    //        }
    //        colSelect++;
    //        flashLED();
    //        command = 0;
    //        break;
    //      }
    //    case 5: {
    //        rowSelect++;
    //        command = 0;
    //        Serial.println(rowSelect);
    //        break;
    //      }
    //    case 6: {                               // increment rows and hold columns
    //        digitalWrite(LED, LOW);
    //        if (debug == true) {
    //          Serial.println("H V");
    //        }
    //        for (int j = 256; j > 0; j--) {    // for loop for the number of columns
    //          if (colSelect == j) {     // check if j = desired column i.e. 0000..0100
    //            // if (pow(2, colSelect) == j) {     // check if 2^j = desired column i.e. 0000..0100
    //
    //            horSR = 1;                      // if it does set SDA_ to high
    //          } else {
    //            horSR = 0;                      // if not set it to low (most cases)
    //          }
    //          if (rowSelect == j) {
    //            verSR = 1;                      // same as above for vertical SR
    //          } else {
    //            verSR = 0;
    //          }
    //          digitalWrite(resetBIN, LOW);        // Flush the SR
    //          waitFor(10);
    //          digitalWrite(resetBIN, HIGH);
    //          waitFor(10);
    //          digitalWrite(HCLKin, HIGH);          // set the SR clock high
    //          digitalWrite(LED, HIGH);
    //          waitFor(10);
    //          digitalWrite(Din, horSR);       // set SDA_A pin to horSR value
    //          digitalWrite(DHin, verSR);       // set SDA_B pin to verSR value
    //          waitFor(10);
    //          digitalWrite(HCLKin, LOW);           // set the SR clock Low
    //          digitalWrite(LED, LOW);
    //
    //          if (debug == true) {
    //            Serial.print(horSR );
    //            Serial.print(' ');
    //            Serial.println(verSR);
    //          }
    //          rowSelect++;
    //          if (rowSelect >= 96) {
    //            rowSelect = 0;
    //          }
    //        }
    //        flashLED();
    //        command = 0;
    //        break;
    //
    //      }
    case 9:
      turnOff();
      flashLED();
      command = 0;
      break;
  }
}

void waitFor(int msec) {
  timerB = millis();
  while (int hold = true) {
    if (millis() - timerB >= msec) {
      hold == false;
      return;
    } else {}
  }
}

void flashLED() {
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
void turnOff()
{
  digitalWrite(vgHVP, LOW);
  digitalWrite(vgLVP, LOW);
  digitalWrite(HCLKin, LOW);
  digitalWrite(Din, LOW);
  digitalWrite(DHin, LOW);
  digitalWrite(resetBIN, LOW);
  digitalWrite(vddHV, LOW);
  digitalWrite(vgLVN, LOW);
  digitalWrite(vgHVN, LOW);
  digitalWrite(vddLV, LOW);
  digitalWrite(ch1_vooff, LOW);
  digitalWrite(ch1vo1, LOW);
  digitalWrite(ch1vo2, LOW);
  digitalWrite(ch1vo3, LOW);
  digitalWrite(ch1vo4, LOW);
  digitalWrite(ch1vo5, LOW);
  digitalWrite(ch1vo6, LOW);
  digitalWrite(ch1vo7, LOW);
  digitalWrite(Csin, LOW);
  digitalWrite(LED, LOW);
}

void definePins()
{
  pinMode(vgHVP, OUTPUT);
  pinMode(vgLVP, OUTPUT);
  pinMode(HCLKin, OUTPUT);
  pinMode(Din, OUTPUT);
  pinMode(DHin, OUTPUT);
  pinMode(resetBIN, OUTPUT);
  pinMode(vddHV, OUTPUT);
  pinMode(vgLVN, OUTPUT);
  pinMode(vgHVN, OUTPUT);
  pinMode(vddLV, OUTPUT);
  pinMode(ch1_vooff, OUTPUT);
  pinMode(ch1vo1, OUTPUT);
  pinMode(ch1vo2, OUTPUT);
  pinMode(ch1vo3, OUTPUT);
  pinMode(ch1vo4, OUTPUT);
  pinMode(ch1vo5, OUTPUT);
  pinMode(ch1vo6, OUTPUT);
  pinMode(ch1vo7, OUTPUT);
  pinMode(Csin, OUTPUT);
  pinMode(LED, OUTPUT);
}
