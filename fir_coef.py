#!/usr/bin/python
# written by Diana Vermilya on Dec17
# modified by Ian Daniher sometime thereafter
# based on code by XMOS Ltd.
# released under beerware license

# classic windowed sinc filter coefficient generator

import math
import numpy

def windowValue(window, n, N):
	if window == 'hann':
		return 0.5 * (1 - math.cos (2 * n * math.pi / (N-1.0)))
	elif window == 'hamming':
		return 0.54 - 0.46 * math.cos (2 * n * math.pi / (N-1.0))
	elif window == 'gaussian':
		sigma = 0.4
		return exp(-0.5*math.sqrt( (n-(N-1.0)/2.0) / (sigma * (N-1.0)/2.0) ))
	elif window == 'blackman':
		alpha = 0.16
		a0 = (1-alpha)/2
		a1 = 0.5
		a2 = alpha/2
		return a0 - a1*math.cos(2*math.pi*n/(N-1.0))+a2*math.cos(4*math.pi*n/(N-1.0))
	else:
		return 1.0

def sinc(x, fc):
	if x == 0:
		return 2*fc
	else:
		return math.sin(2*fc*math.pi*x)/(math.pi*x)

def lp(fc, w, n, N):
	s = sinc(n-(N>>1), fc)
	wi = windowValue(w, n, N)
	return s*wi

def hp(fc, w, n, N):
	l = lp(fc, w, n, N)
	if n != (N>>1):
		return -l
	else:
		return 1-l

def bs(fcl, fch, w, n, N):
	l = lp(fcl, w, n, N)
	h = hp(fch, w, n, N)
	return l+h


def bp(fcl, fch, w, n, N):
	b = bs(fcl, fch, w, n, N)
	if n != (N>>1):
		return -b
	else:
		return 1-b;
	
"""
type can be: low, high, BP, BS
freq1 and freq2 are ints
if one freq is required, it is freq1 and freq2 = 0
if two freqs are required, freq1 is low and freq2 is high
win can be gaussian, hamming, hann, blackman
N is an odd int for number of taps.  If not needed, equals 0
# Sourcefile is an xc file.  If not needed, = 'none'
# resposeCurve is a csv file.  If not needed, = 'none'
fs is the sample frequency

"""

def filter(filterType, freq1, freq2, fs, win, N):
	c = []

	freq1 = freq1/float(fs)
	freq2 = freq2/float(fs)

	for i in range(N):
		if filterType == 'high':
			c.append(hp(freq1, win, i, N))
		elif filterType == 'low':
			c.append(lp(freq1, win, i, N))
		elif filterType == 'BP':
			c.append(bp(freq1, freq2, win, i, N))
		elif filterType == 'BS':
			c.append(bs(freq1, freq2, win, i, N))
		else:
			return 'invalid filter type!'

	sum0 = 0
	tsum = 0
	for i in range(-80, 80+N):

		if (i == (N>>1)):
			pass
		else:
			if filterType == 'high':
				x = hp(freq1, 'nowindow', i, N)
			elif filterType == 'low':
				x = lp(freq1, 'nowindow', i, N)
			elif filterType == 'BP':
				x = bp(freq1, freq2, 'nowindow', i, N)
			elif filterType == 'BS':
				x = bs(freq1, freq2, 'nowindow', i, N)
			else:
				return 'invalid filter type!'
			if i >= N or i < 0:
				sum0 += x**2
			else:
				sum0 += (x - c[i])**2
			tsum += x**2
	sum0 = math.sqrt(sum0)/math.sqrt(tsum)
	print "error: " + str(sum0*100)+'%'
	if sum0 > 0.2:
		print "more taps?"
	
	fixed = []

	floating = numpy.array(c, "float64")
	
	for i in range(N):
		fixed.append(int(math.floor(c[i]*(1<<24) + 0.5)))
	fixed = numpy.array(fixed, "int32")

	factor = 2**(1./2**5)
	omega = 50
	frequency = []
	magnitude = []
	dB = []

	while omega < fs/2:
		sumr = 0
		sumi = 0
		for i in range(N):
			o = omega/float(fs)*2*math.pi
			sumr += c[i] * math.cos(i*o)
			sumi += c[i] * math.sin(i*o)
		mag = math.sqrt(sumi*sumi + sumr*sumr)
		frequency.append(omega) #accurate to 0 places
		magnitude.append(mag) #accurate to 8 places
		dB.append(20*math.log10(mag)) #accurate to 3 places

		omega = omega*factor
	return fixed #[fixed, floating, frequency, magnitude, dB]
