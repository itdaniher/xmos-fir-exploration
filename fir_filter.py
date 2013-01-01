#!/usr/bin/python

import wave
import numpy
import fir_coef

import record_test

import alsaaudio

# return a numpy array of 32b integers from a wavefile
def getWaveAsArray(file):
	wav = wave.open(file)
	samples = [wav.readframes(1) for i in range(wav.getnframes())]
	samples = [ord(sample[1]) << 8 | ord(sample[0]) for sample in samples]
	return numpy.array(samples, "int32"), wav.getframerate()

# execute a FIR filter with ntaps	
def simpleConvolve(samples, coeffs, ntaps):
	outSamples = []
	operationalBuffer = numpy.zeros(ntaps, "int32")
	for sample in samples:
		operationalBuffer = numpy.insert(operationalBuffer, 0, sample)
		operationalBuffer = numpy.delete(operationalBuffer, -1)
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
	device.setrate(int(frameRate))

	device.setperiodsize(320) 
	for dataGroup in _chunk(data, 320):
		device.write(dataGroup)

if __name__ == "__main__":
	# load sample wav file
	# audioArray, frameRate = getWaveAsArray(open("out.wav"))

	frameRate = 44.1e3
	print "recording audio sample"
	audioArray = record_test.recordAudio(None, frameRate, 10)
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
	#filtered = fir824(audioArray, coeffs, ntaps)
	filtered = numpy.convolve(numpy.array(audioArray, "int64"), coeffs)[0:-ntaps+1]
	filtered >>= 25
	print "playing filtered audio"
	# play filtered audio
	play32bArray(filtered)
