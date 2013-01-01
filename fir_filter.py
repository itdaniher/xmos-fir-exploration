#!/usr/bin/python

import wave
import numpy
import fir_coef

import alsaaudio

_chunk = lambda l, x: [l[i:i+x] for i in xrange(0, len(l), x)]
_unTwos = lambda x, bitlen: x-(1<<bitlen) if (x&(1<<(bitlen-1))) else x

def recordAudio(rate = 44100, totalTime = 60):

	# capture, blocking, default device
	inp = alsaaudio.PCM(alsaaudio.PCM_CAPTURE, 0, 'default')

	inp.setchannels(1)
	inp.setrate(int(rate))
	inp.setformat(alsaaudio.PCM_FORMAT_S16_LE)

	# get 160 sample chunks in 320 bytes
	samplesPerPeriod = 160

	inp.setperiodsize(samplesPerPeriod)

	samples = []
	for i in range(int(rate*totalTime/samplesPerPeriod)):
		# Read data from device
		l, data = inp.read()
		# build list of properly signed numbers from data buffer 
		samples += [ _unTwos(ord(y) << 8 | ord(x), 16) for x, y in _chunk(data, 2) ]

	return samples

# play an array of 32b integers via ALSA
def play32bArray(data):
	data = numpy.array(data, "int32")
	device = alsaaudio.PCM()
	device.setformat(alsaaudio.PCM_FORMAT_S32_LE) 
	device.setchannels(1)
	device.setrate(int(frameRate))

	device.setperiodsize(320) 
	for dataGroup in _chunk(data, 320):
		device.write(dataGroup)

if __name__ == "__main__":

	frameRate = 44.1e3
	print "recording audio sample"
	audioArray = recordAudio(frameRate, 10)
	audioArray = numpy.array(audioArray, "int32")
	
	# shift 16b audio to play nicely with 32b out
	audioArray <<= 16
	
	print "playing unmodified audio"
	
	# play the unmessedup array
	play32bArray(audioArray)
	
	# reasonable number of taps
	ntaps = 255
	
	print "generating coefficients"
	# generate coefficients using fir_coef code by Diana
	coeffs = fir_coef.filter('low', 2000, 0, frameRate, 'hamming', ntaps)
	
	# uncomment below line for convolving-with-impulse
	# 1 << 25 is the 8.24 representation of '1'
	#coeffs = [1<<25]+[0]*(ntaps-1)
	
	print "filtering"
	# process audioArray, store it as 'filtered'
	filtered = numpy.convolve(numpy.array(audioArray, "int64"), coeffs)[0:-ntaps+1]
	filtered >>= 25
	print "playing filtered audio"
	# play filtered audio
	play32bArray(filtered)
