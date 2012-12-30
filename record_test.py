#!/usr/bin/env python

import alsaaudio
import wave

_chunk = lambda l, x: [l[i:i+x] for i in xrange(0, len(l), x)]
_unTwos = lambda x, bitlen: x-(1<<bitlen) if (x&(1<<(bitlen-1))) else x


def recordAudio(wav = wave.open(open("out.wav", "wb")), rate = 44100, totalTime = 60):

	# capture, blocking, default device
	inp = alsaaudio.PCM(alsaaudio.PCM_CAPTURE, 0, 'default')

	# Set attributes: Mono, 44100 Hz, 16 bit little endian samples
	inp.setchannels(1)
	inp.setrate(rate)
	inp.setformat(alsaaudio.PCM_FORMAT_S16_LE)

	# get 160 sample chunks in 320 bytes
	samplesPerPeriod = 160

	inp.setperiodsize(samplesPerPeriod)

	# config wave file header
	wav.setnchannels(1)
	wav.setsampwidth(2)
	wav.setframerate(rate)

	for i in range(rate*totalTime/samplesPerPeriod):
		# Read data from device
		l, data = inp.read()
		# build list of properly signed numbers from data buffer 
		#samples = [ _unTwos(ord(y) << 8 | ord(x), 16) for x, y in _chunk(data, 2) ]
		# write raw data buffer
		wav.writeframes(data)

if __name__ == "__main__":
	recordAudio()
