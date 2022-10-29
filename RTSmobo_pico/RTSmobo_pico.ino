#include <SPI.h>

#define debug true
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
#define ch7v6   22  // Select which amplifier output is on channel 7  vout6
#define LED     25  // Pico LED
#define ch6v5   26  // Select which amplifier output is on channel 6  vout5
#define ch5v4   27  // Select which amplifier output is on channel 5  vout4

int command = 0;
int increment = 0;
int horSR = 0;

uint32_t timer = millis();
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
  if (Serial.available() > 0) {
    command = Serial.readString().toInt();
    Serial.println(command);
  }

  switch (command) {
    case 0: {   // set all pins low
        turnOff();
        flashLED();
        break;
      }
    case 1: {                     // set channel 1 for amp characterization
        turnOff();                  // by setting the SR inputs to low
        digitalWrite(Csin, HIGH);   // close amp bypass
        digitalWrite(ch1v0, HIGH);  // chanel 1 has vout0
        // apply a voltage to vout1BYP jumper
        // adjust gain to provide a 1:1 input/output
        break;
      }
    case 2: {
        int num = 1234;

        uint8_t bitsCount = sizeof( num ) * 8;
        if (debug == true) {
          Serial.println(bitsCount);
          Serial.println(sizeof(num));
        }
        char str[ bitsCount + 1 ];


        uint8_t i = 0;
        while ( bitsCount-- ) {
          str[ i++ ] = bitRead( num, bitsCount ) + '0';
        }
        str[ i ] = '\0';

        Serial.println( str );
        break;
      }
    case 3: {
        for (int j = 0; j < 32; j = j + 1) {
          int64_t horInput = pow(2, j);
          Serial.println(horInput);

          horizBinary(horInput);
          delay(500);
        }
        break;
      }
    case 4: {
      
        timer == millis();
        for (int j = 2048; j > 0; j--) {
          if (pow(2, increment) == j){
            
            horSR = 1;
        } else {
          horSR = 0;
        }
     //   if (millis() - timer == 10)
        digitalWrite(SCL, HIGH);
        delay(10);
        digitalWrite(SDA_A, horSR);
        delay(10);
        digitalWrite(SCL, LOW);
        delay(10);
                
        if (debug == true){
        Serial.print(horSR);
        }
    }
    
        increment++;
        if (debug == true){
        Serial.println();
        }

        

        break;
}
}
}

void horizBinary(int horizDecim)
{
  for (int bit = 32; bit >= 0; bit--) {
    int horizBin = bitRead(horizDecim, bit);
    if (debug == true) {
      Serial.print(horizBin);
    }
  }
  Serial.println();
}
void printFullBin(int number)
{
  for (int bit = 7; bit >= 0; bit--)
  {
    Serial.print(bitRead(number, bit));
  }
  Serial.println();
}
void flashLED() {
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
  digitalWrite(smuSel, LOW);
  digitalWrite(naSel, LOW);
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
  pinMode(smuSel, OUTPUT);
  pinMode(naSel, OUTPUT);
  pinMode(ch8v7, OUTPUT);
  pinMode(ch7v6, OUTPUT);
  pinMode(LED, OUTPUT);
  pinMode(ch6v5, OUTPUT);
  pinMode(ch5v4, OUTPUT);
}
