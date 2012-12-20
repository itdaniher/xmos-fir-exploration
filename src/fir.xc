// Copyright (c) 2011, XMOS Ltd, All rights reserved
// This software is freely distributable under a derivative of the
// University of Illinois/NCSA Open Source License posted in
// LICENSE.txt and at <http://github.xcore.com/>

#include <print.h>
#include <xs1.h>
#include "fir.h"

int fir_SingleThread(streaming chanend c,int h[],int x[], unsigned ntaps){
	for(int i=0;i<ntaps;i++){
		c:>h[i];
		x[i]=0;
		x[i+ntaps]=0;
	}
	schkct(c,9); // Check that all filter taps was sent
    firASM_DoubleData_singleThread(c, h, x, ntaps);
return 0;
}

void disconnect(streaming chanend c[], unsigned size) {
    for (unsigned i = 0; i < size; i++) {
    //printf("\nKilling channel cd %d",i);
        soutct(c[i], XS1_CT_END);
        schkct(c[i], XS1_CT_END);
    }
}


int test_performance(streaming chanend c,int ELEMENTS){
	timer t;
	int ans,time;
	int i = 1;
	unsigned crc=0;
	for(int i=0;i<ELEMENTS;i++)
		c<: (i + 1) << 24; // sends the filtertaps to the fir filter
    soutct(c,9);
    printstrln("Testing performance, Running FIR-filter for 1 sec");
	printint(ELEMENTS);
	printstrln(" filter taps");
	t:> time;
	c<:i; //Send first sample directly after the timing started
	i++;
	c<:i; //Send second sample directly to fill channel buffers
	time+=XS1_TIMER_HZ;
	while(1) {
		select {
			case c:>ans:
			crc32(crc, ans, POLY);
			i++;
			c<:i;
			break;
			case t when timerafter (time) :> void:
			soutct(c,10); //end FIR thread
			c:>ans; // Fetch second last sample in channel buffer
			crc32(crc, ans, POLY);
			c:>ans; // Fetch last sample in channel buffer
			crc32(crc, ans, POLY);
			printstr("Filtered ");
			printint(i);
			printstrln(" samples during 1 second");
			printint(i*3);
			printstrln(" kTaps per sec.");
			printstr("CRC32 checksum for all filtered samples was: 0x");
			printhexln(crc);
			return i;
			break;
		}
	}
	return -1;
}


