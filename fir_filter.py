import wave
import collections
import numpy
import fir_coef

import alsaaudio

def getWaveAsArray(file):
	wav = wave.open(file)
	samples = [wav.readframes(1) for i in range(wav.getnframes())]
	samples = [ord(sample[1]) << 8 | ord(sample[0]) for sample in samples]
	return numpy.array(samples, "int32"), wav.getframerate()
	
def fir824(samples, coeffs, ntaps):
	outSamples = numpy.array([], "int32")
	operationalBuffer = collections.deque([0]*ntaps, ntaps)
	for sample in samples:
		operationalBuffer.appendleft(sample)
		arrayFIFO = numpy.array(operationalBuffer, "int32")
		arrayFIFO *= coeffs
		numpy.append(outSamples, sum(arrayFIFO))
	return outSamples


def play32bArray(data):
	_chunk = lambda l, x: [l[i:i+x] for i in xrange(0, len(l), x)]
	device = alsaaudio.PCM()
	device.setformat(alsaaudio.PCM_FORMAT_S32_LE) 
	device.setchannels(1)
	device.setrate(frameRate)

	device.setperiodsize(320) 
	for dataGroup in _chunk(data, 320):
		device.write(dataGroup)

audioArray, frameRate = getWaveAsArray(open("noTree.wav"))

audioArray <<= 16

play32bArray(audioArray)

ntaps = 256

coeffs = fir_coef.filter('low', 500, 0, frameRate, 'hamming', ntaps)[0]

filtered = fir824(audioArray, coeffs, ntaps)

play32bArray(filtered)
