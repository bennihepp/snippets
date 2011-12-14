import sys

import numpy as np

from matplotlib import pyplot as plt

import fft

N = 256
M = N

X,Y = np.mgrid[-N/2:N/2,-M/2:M/2]

V = np.cos(2*np.pi*X/N) + np.sin(2*np.pi*Y/M)
Q1 = fft.fft(V)
P1 = fft.ifft(Q1)

ax = plt.subplot(2, 2, 1)
ax.imshow(V, interpolation='nearest')
ax = plt.subplot(2, 2, 2)
ax.imshow(np.real(P1), interpolation='nearest')
ax = plt.subplot(2, 2, 3)
ax.imshow(np.real(Q1), interpolation='nearest')
ax = plt.subplot(2, 2, 4)
ax.imshow(np.imag(Q1), interpolation='nearest')
plt.show()

Q2 = np.fft.fft(V)
P2 = np.fft.ifft(Q2)

plt.plot(X, V, '-b', X, np.real(Q2/np.sqrt(N)), '-g', X, np.real(P2), '-r')
#plt.show()
#print 'Q2:', Q2
#print 'P2:', P2

max_dev = np.max(np.abs(P1-P2))
#print 'maximum deviation:', max_dev


