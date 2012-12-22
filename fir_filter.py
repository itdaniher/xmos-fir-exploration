#!/usr/bin/python

import wave
import collections
import numpy
import fir_coef

import alsaaudio

# return a numpy array of 32b integers from a wavefile
def getWaveAsArray(file):
	wav = wave.open(file)
	samples = [wav.readframes(1) for i in range(wav.getnframes())]
	samples = [ord(sample[1]) << 8 | ord(sample[0]) for sample in samples]
	return numpy.array(samples, "int32"), wav.getframerate()

# execute a FIR filter with ntaps	
def fir824(samples, coeffs, ntaps):
	outSamples = []
	operationalBuffer = collections.deque([0]*ntaps, ntaps)
	for sample in samples:
		operationalBuffer.appendleft(sample)
		# create an array of 64b numbers from our operational queue for storage of the results of a 32*32 multiplication
		arrayFIFO = numpy.array(operationalBuffer, "int64")
		# multiply by our 8.24 coefficients
		arrayFIFO *= coeffs
		# shift by 25 to normalize back to 32b integers
		arrayFIFO >>= 25
		outSamples.append(sum(arrayFIFO))
	return outSamples

# play an array of 32b integers via ALSA
def play32bArray(data):
	data = numpy.array(data, "int32")
	_chunk = lambda l, x: [l[i:i+x] for i in xrange(0, len(l), x)]
	device = alsaaudio.PCM()
	device.setformat(alsaaudio.PCM_FORMAT_S32_LE) 
	device.setchannels(1)
	device.setrate(frameRate)

	device.setperiodsize(320) 
	for dataGroup in _chunk(data, 320):
		device.write(dataGroup)

# load sample wav file
audioArray, frameRate = getWaveAsArray(open("noTree.wav"))

# shift 16b audio to play nicely with 32b out
audioArray <<= 16

print "playing unmodified audio"

# play the unmessedup array
play32bArray(audioArray)

# reasonable number of taps
ntaps = 255

print "generating coefficients"
# generate coefficients using fir_coef code by Diana
coeffs = fir_coef.filter('high', 2000, 0, frameRate, 'hamming', ntaps)

# uncomment below line for convolving-with-impulse
# 1 << 25 is the 8.24 representation of '1'
#coeffs = [1<<25]+[0]*(ntaps-1)

print "filtering"
# process audioArray, store it as 'filtered'
filtered = fir824(audioArray, coeffs, ntaps)

print "playing filtered audio"
# play filtered audio
play32bArray(filtered)
