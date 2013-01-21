#!/usr/bin/python

# this is stupid-simple code to loopback an alsa input into an alsa output
# other ways of doing this with different toolkits:
#
# arecord | aplay # alsa-utils
# rec -d | play - # sox
#
# the pure-python route gives known latency / phase delay and higher understandability than other routes
# data chunks can easily be shoved through an audio filter, keeping known delay

import numpy
import alsaaudio

_chunk = lambda l, x: [l[i:i+x] for i in xrange(0, len(l), x)]
_unTwos = lambda x, bitlen: x-(1<<bitlen) if (x&(1<<(bitlen-1))) else x

rate = 44.1e3
samplesPerPeriod = 160
frameDelay = 16

inp = alsaaudio.PCM(alsaaudio.PCM_CAPTURE, alsaaudio.PCM_NONBLOCK, 'default')
outp = alsaaudio.PCM(alsaaudio.PCM_PLAYBACK, alsaaudio.PCM_NONBLOCK, 'default')

inp.setchannels(1)
inp.setrate(int(rate))
inp.setformat(alsaaudio.PCM_FORMAT_S16_LE)

outp.setchannels(1)
outp.setrate(int(rate))
outp.setformat(alsaaudio.PCM_FORMAT_S16_LE)

inp.setperiodsize(samplesPerPeriod)
outp.setperiodsize(samplesPerPeriod)

print inp.pcmtype(), outp.pcmtype()

initbuffer = []

i = 0
while i < frameDelay:
	l, data = inp.read()
	if l == samplesPerPeriod:
		i += 1
		initbuffer.append(data)

print "lag of " + str(frameDelay*samplesPerPeriod/rate) + " seconds"

for data in initbuffer:
	outp.write(data)

while True:
	l, data = inp.read()
	outp.write(data)
