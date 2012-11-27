// Copyright (c) 2011, XMOS Ltd, All rights reserved
// This software is freely distributable under a derivative of the
// University of Illinois/NCSA Open Source License posted in
// LICENSE.txt and at <http://github.xcore.com/>

#include <xs1.h>
#include "pwm_singlebit_port.h"

out buffered port:32 rgPorts[] = {XS1_PORT_1L, XS1_PORT_1A}; 
clock clk = XS1_CLKBLK_1;

#define RESOLUTION 256
#define PERIOD (RESOLUTION*200)
#define NUM_PORTS 2
#define TIMESTEP 100

enum { COUNTUP, COUNTDOWN };

void updateValues(unsigned int values[], unsigned int direction[]) {
	for (unsigned int i = 0; i < NUM_PORTS; ++i) {
		switch (direction[i]) {
		case COUNTUP:
			if (values[i] == RESOLUTION) {
				direction[i] = COUNTDOWN;
				--values[i];
			} else {
				++values[i];
			}
			break;

		case COUNTDOWN:
			if (values[i] == 0) {
				direction[i] = COUNTUP;
				++values[i];
			} else {
				--values[i];
			}
			break;
		}
	}
}

void client(chanend c) {
    timer t;
    int time;

    unsigned int values[NUM_PORTS] = {0, RESOLUTION};
    unsigned int direction[NUM_PORTS] = {COUNTUP, COUNTDOWN};

    t :> time;
    time += PERIOD;

    while (1) {
        t when timerafter (time) :> void;
        updateValues(values, direction);
        pwmSingleBitPortSetDutyCycle(c, values, NUM_PORTS);
        time += PERIOD;
    }
}

int main() {
    chan c;

    par {
        client(c);
        pwmSingleBitPort(c, clk, rgPorts, NUM_PORTS, RESOLUTION, TIMESTEP,1);
    }
    return 0;
}

