import sys

import numpy as np

from matplotlib import pyplot as plt

import fft

N = 8 * 2

X = np.arange(N)

V = np.cos(2*np.pi*X/N+0.5) + np.sin(2*np.pi*0.5*X/N) - 0.3*np.cos(2*np.pi*X/N) + 5.0*np.sin(2*np.pi*0.3*X/N)
print 'V:', V
Q1 = fft.fft(V)
P1 = fft.ifft(Q1)

plt.plot(X, V, '-b', X, np.real(Q1), '-g', X, np.real(P1), '-r')
plt.show()
print 'Q1:', Q1
print 'P1:', np.real(P1)

Q2 = np.fft.fft(V)
P2 = np.fft.ifft(Q2)

plt.plot(X, V, '-b', X, np.real(Q2/np.sqrt(N)), '-g', X, np.real(P2), '-r')
plt.show()
print 'Q2:', Q2
print 'P2:', P2

max_dev = np.max(np.abs(P1-P2))
print 'maximum deviation:', max_dev


