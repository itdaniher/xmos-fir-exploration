// Copyright (c) 2011, Mikael Bohman, All rights reserved
// This software is freely distributable under a derivative of the
// University of Illinois/NCSA Open Source License posted in
// LICENSE.txt and at <http://github.xcore.com/>

//FIR filtering using a channel as Input and Output running on one thread.
//Uses the double data method and Q8.24

#include <platform.h>
#include <xs1.h>
#include "fir.h"

#define ntaps 300

int main() {
	streaming chan c;
	unsigned samples;
	int h[ntaps];
	int x[2*ntaps];
	par{
		fir_SingleThread(c, h, x, ntaps);
		samples = test_performance(c, ntaps);
	}
return 0;
}
