import wave
import collections
import numpy
import fir_coef

import alsaaudio

def getWaveAsArray(file):
	wav = wave.open(file)
	samples = [wav.readframes(wav.getsampwidth()) for i in range(wav.getnframes())]
	samples = map(ord, samples)
	return numpy.array(samples, "int32"), wav.getframerate()
	
audioArray, frameRate = getWaveAsArray(open("noTree.wav"))

audioArray <<= 24

def fir824(samples, coeffs, ntaps):
	outSamples = numpy.array([], "int32")
	operationalBuffer = collections.deque([0]*ntaps, ntaps)
	for sample in samples:
		operationalBuffer.appendleft(sample)
		arrayFIFO = numpy.array(operationalBuffer, "int32")
		arrayFIFO *= coeffs
		numpy.append(outSamples, sum(arrayFIFO))
	return outSamples

ntaps = 256

coeffs = fir_coef.filter('low', 500, 0, frameRate, 'hamming', ntaps)[0]

filtered = fir824(audioArray, coeffs, ntaps)

device = alsaaudio.PCM()
device.setformat(alsaaudio.PCM_FORMAT_S32_LE) 
device.setchannels(1)
device.setrate(frameRate)

device.setperiodsize(320) 

_chunk = lambda l, x: [l[i:i+x] for i in xrange(0, len(l), x)]

for data in _chunk(filtered, 320):
	device.write(data)
