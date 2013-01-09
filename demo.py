#!/usr/bin/python

from helpers import *
import numpy
import fir_coef

from matplotlib import pyplot
fig, (ax, bx) = pyplot.subplots(2, 1, sharex=True, sharey=True)
pyplot.xlabel("frequency")
pyplot.ylabel("amplitude")

frameRate = 44.1e3

print "recording audio sample"
audioArray = recordAudio(frameRate, 10)
audioArray = numpy.array(audioArray, "int32")
# shift 16b audio to play nicely with 32b out
audioArray <<= 16

print "calculating fft of unfiltered audio"
fftUnfiltered = numpy.abs(numpy.fft.fft(audioArray))
freqs = numpy.fft.fftfreq(audioArray.shape[-1], d=1/frameRate)
ax.semilogy(freqs[0:freqs.shape[-1]/2], fftUnfiltered[0:fftUnfiltered.shape[-1]/2])

print "playing unmodified audio"

# play the unmessedup array
play32bArray(audioArray, frameRate)

# reasonable number of taps
ntaps = 255

print "generating coefficients"
# generate coefficients using fir_coef code by Diana
coeffs = fir_coef.filter('low', 2000, 0, frameRate, 'blackman', ntaps)

# uncomment below line for convolving-with-impulse
# 1 << 25 is the 8.24 representation of '1'
#coeffs = [1<<25]+[0]*(ntaps-1)

print "filtering"
# process audioArray, store it as 'filtered'
filtered = numpy.convolve(numpy.array(audioArray, "int64"), coeffs)[0:-ntaps+1]
filtered >>= 25

print "calculating fft of filtered audio"
freqs = numpy.fft.fftfreq(filtered.shape[-1], d=1/frameRate)
fftFiltered = numpy.abs(numpy.fft.fft(filtered))
bx.semilogy(freqs[0:freqs.shape[-1]/2], fftFiltered[0:fftFiltered.shape[-1]/2]) 

print "playing filtered audio"
# play filtered audio
play32bArray(filtered, frameRate)
pyplot.show()
