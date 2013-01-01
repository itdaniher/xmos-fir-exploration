#!/usr/bin/env python

import wave
import alsaaudio

_chunk = lambda l, x: [l[i:i+x] for i in xrange(0, len(l), x)]
_unTwos = lambda x, bitlen: x-(1<<bitlen) if (x&(1<<(bitlen-1))) else x

def recordAudio(wav = "", rate = 44100, totalTime = 60):

	if wav is not None:
		wav = wave.open(open("out.wav", "wb"))

	# capture, blocking, default device
	inp = alsaaudio.PCM(alsaaudio.PCM_CAPTURE, 0, 'default')

	inp.setchannels(1)
	inp.setrate(int(rate))
	inp.setformat(alsaaudio.PCM_FORMAT_S16_LE)

	# get 160 sample chunks in 320 bytes
	samplesPerPeriod = 160

	inp.setperiodsize(samplesPerPeriod)
	if wav is not None:
		# config wave file header
		wav.setnchannels(1)
		wav.setsampwidth(2)
		wav.setframerate(int(rate))

	samples = []
	for i in range(int(rate*totalTime/samplesPerPeriod)):
		# Read data from device
		l, data = inp.read()
		# build list of properly signed numbers from data buffer 
		samples += [ _unTwos(ord(y) << 8 | ord(x), 16) for x, y in _chunk(data, 2) ]
		if wav is not None:
			# write raw data buffer
			wav.writeframes(data)
	return samples

if __name__ == "__main__":
	print recordAudio(wav = "", rate = 8000, totalTime = .1)
