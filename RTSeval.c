#include <stdio.h>
#include "pico/stdlib.h"
#include "hardware/gpio.h"
#include "pico/binary_info.h"

const uint LED_PIN = 25;
int counter = 0;
int inputSequence = 00000000;

int main() {
	bi_decl(bi_program_description("This is a test binary."));
	bi_decl(bi_1pin_with_name(LED_PIN, "On-board LED"));

	stdio_init(LED_PIN);
	gpio_set_dir(LED_PIN, GPIO_OUT);

	while(1) {
		gpio_put(LED_PIN, 1);
		for(int byte=0; byte <256, byte++) {
			//alogrithm code
			//increment shiftR1 256 bit number
			//increment shiftR2 256 bit number
			//clock goes high
			//shift in first bit for sr1 & sr2 
			//clock goes low
}
	puts("transistor xx is on");
}
