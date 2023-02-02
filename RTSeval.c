#include <stdio.h>
#include "pico/stdlib.h"
#include "hardware/gpio.h"
#include "pico/binary_info.h"

#define SR1_DATA	16	// Horizontal Shift Register
#define SR2_DATA	17	// Vertical Shift Register
#define SRCLK	 	18	// Clock for both shift registers
#define CSIN		19	// Chip Select?
#define RESET		20	// Reset for SR?

const uint LED_PIN = 25;
int counter = 0;
int SRbyte = 0;

int HardwareSerial::available(void)			// Serial.available function
{
  return (unsigned int)(SERIAL_BUFFER_SIZE + _rx_buffer->head - _rx_buffer->tail) % SERIAL_BUFFER_SIZE;
}

int main() {
							//Binary info for picotool
	bi_decl(bi_program_description("This script loads instruction sets into shift registers for RTS Noise evaluation."));   
	bi_decl(bi_1pin_with_name(LED_PIN, "On-board LED"));

	uart_init(uart0, 115200);			// initialize the pico UART ports
//	uart_init(uart1, 115200);

	gpio_set_function(0, GPIO_FUNC_UART);		// set gpio function to UART
	gpio_set_function(1, GPIO_FUNC_UART);

	uart_puts(uart0, "Hello World");		// print 

	stdio_init(LED_PIN);				// initialize LED pin
	gpio_set_dir(LED_PIN, GPIO_OUT);		// Set LED pin direction
	gpio_set_dir(SR1_LATCH, GPIO_OUT);		// Set SR1 Latch pin to output
	 
	gpio_put(LED_PIN, 1);				// Set LED to high
	
	/////algorithm code
	
	//store SR instructions to array(s)
	uint8_t sr1Data[8] = [0,0,0,0,0,0,0,1];		// Horizontal Shift register instruction set
	uint8_t sr2Data[8] = [0,0,0,0,0,0,0,1];		// Vertical Shift register instruction set
	
	////  Load the Shift register with instruction ////
	
	for(SRbyte = 0; SRbyte < 8, SRbyte++) {
		gpio_put(SRCLK, 1);			//set clock pin high
		gpio_put(SR1_DATA, sr1Data[SRbyte]);	//load SR1 bit into data pin
		gpio_put(SR2_DATA, sr2Data[SRbyte]);	//load SR2 bit into data pin
		gpio_put(SRCLK, 0);			// clock pin low
	}
	gpio_put(RESET, 0);
	SRbyte = 0;
	
	puts("transistor xx is on");  			//send transistor number to CPU
	gpio_put(LED_PIN, 0);				//
}
