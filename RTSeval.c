#include <stdio.h>
#include "pico/stdlib.h"
#include "hardware/gpio.h"
#include "pico/binary_info.h"

#define SR1_PIN		16
#define SR2_PIN		17
#define SRCLK_PIN 	18
#define SR1_LATCH	19
#define SR2_LATCH	20

const uint LED_PIN = 25;
int counter = 0;
int 0;

int HardwareSerial::available(void)			// Serial.available function
{
  return (unsigned int)(SERIAL_BUFFER_SIZE + _rx_buffer->head - _rx_buffer->tail) % SERIAL_BUFFER_SIZE;
}

int main() {
							//Binary info for picotool
	bi_decl(bi_program_description("This script loads instruction sets into shift registers for RTS Noise evaluation."));   
	bi_decl(bi_1pin_with_name(LED_PIN, "On-board LED"));

	uart_init(uart0, 115200);			// initialize the pico UART ports
	uart_init(uart1, 115200);

	gpio_set_function(0, GPIO_FUNC_UART);		// set gpio function to UART
	gpio_set_function(1, GPIO_FUNC_UART);

	uart_puts(uart0, "Hello World");		// print 

	stdio_init(LED_PIN);				// initialize LED pin
	gpio_set_dir(LED_PIN, GPIO_OUT);		// Set LED pin direction

	 
	gpio_put(LED_PIN, 1);				// Set LED to high
	
	/////algorithm code
	
	//store SR instructions to array(s)
	uint8_t sr1Data[8] = [1,1,1,1,1,1,1,1]	
	uint8_t sr2Data[8] = [1,1,1,1,1,1,1,1]
	
	////  Load the Shift register with instruction ////
//	for(int byte=0; byte <8, byte++) {
//		gpio_put(SRCLK_PIN, 1);			//set clock pin high
//		gpio_put(SR1_PIN, sr1Data[byte]);	//load SR1 bit into data pin
//		gpio_put(SR2_PIN, sr2Data[byte]);	//load SR2 bit into data pin
//		gpio_put(SRCLK_PIN, 0);	// clock pin low
//	}
	puts("transistor xx is on");  			//send transistor number to CPU
	gpio_put(LED_PIN, 0);				//
}
