import numpy as np

def dft(V, verbose=False):
    V = np.asarray(V, dtype=np.complex)
    N = V.shape[0]
    A = np.mgrid[0:N,0:N]
    if verbose:
        print 'A:', A
    A = A[0] * A[1]
    if verbose:
        print 'A:', A
    A = np.asarray(A, dtype=np.complex) / N
    if verbose:
        print 'A:', A
    kernel = np.exp(-2*np.pi*A*1j)
    if verbose:
        print 'kernel:', kernel
    Q = V[np.newaxis,:] * kernel
    if verbose:
        print 'Q:', Q
    Q = np.sum(Q, axis=1) / np.sqrt(N)
    if verbose:
        print 'Q:', Q
    return Q

def idft(V, verbose=False):
    V = np.asarray(V, dtype=np.complex)
    N = V.shape[0]
    A = np.mgrid[0:N,0:N]
    if verbose:
        print 'A:', A
    A = A[0] * A[1]
    if verbose:
        print 'A:', A
    A = np.asarray(A, dtype=np.complex) / N
    if verbose:
        print 'A:', A
    kernel = np.exp(+2*np.pi*A*1j)
    if verbose:
        print 'kernel:', kernel
    Q = V[np.newaxis,:] * kernel
    if verbose:
        print 'Q:', Q
    Q = np.sum(Q, axis=1) / np.sqrt(N)
    if verbose:
        print 'Q:', Q
    return Q

