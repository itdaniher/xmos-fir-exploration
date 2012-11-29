// Copyright (c) 2011, XMOS Ltd, All rights reserved
// This software is freely distributable under a derivative of the
// University of Illinois/NCSA Open Source License posted in
// LICENSE.txt and at <http://github.xcore.com/>

#include <xs1.h>
#include "pwm_singlebit_port.h"

// use XTAG2 pins 3 and 5 and 7 as 1b wide outputs with a 32b buffer
out buffered port:32 rgPorts[] = {XS1_PORT_1L, XS1_PORT_1A, XS1_PORT_1C}; 

clock clk = XS1_CLKBLK_1;

#define RESOLUTION 1024
#define PERIOD RESOLUTION*2*TIMESTEP
#define PERIOD_NS PERIOD*10
#define NUM_PORTS 3
#define TIMESTEP 100

void updateValues(unsigned int values[]) {
	for (unsigned int i = 0; i < NUM_PORTS; ++i) {
		// increment values[0] by 1, values[1] by 2, modulo the resolution
		values[i] = (values[i]+i+1) % RESOLUTION;
	}
}

void client(chanend c) {
    timer t;
    int time;

    unsigned int values[NUM_PORTS] = {0, 0};

    t :> time;
    time += PERIOD;

    while (1) {
        t when timerafter (time) :> void;
        updateValues(values);
        pwmSingleBitPortSetDutyCycle(c, values, NUM_PORTS);
        time += PERIOD;
    }
}

int main() {
    chan c;

    par {
        client(c);
        pwmSingleBitPort(c, clk, rgPorts, NUM_PORTS, RESOLUTION, TIMESTEP, 1);
    }
    return 0;
}

