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
		arrayFIFO = numpy.array(operationalBuffer, "int32")
		arrayFIFO *= coeffs
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

# play the unmessedup array
play32bArray(audioArray)

ntaps = 255

# generate coefficients using fir_coef code by Diana
coeffs = fir_coef.filter('low', 500, 0, frameRate, 'hamming', ntaps)[1]

# uncomment below line for convolving-with-impulse
#coeffs = [1]+[0]*(ntaps-1)

# process audioArray, store it as 'filtered'
filtered = fir824(audioArray, coeffs, ntaps)

# play filtered audio
play32bArray(filtered)
