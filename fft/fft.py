import numpy as np

def fft(V, verbose=False):
    if V.ndim == 0:
        return V.copy()
    elif V.ndim == 1:
        V = np.asarray(V, dtype=np.complex)
        return fft1d(V, verbose)
    elif V.ndim > 1:
        V = np.asarray(V, dtype=np.complex)
        Q = np.empty(V.shape, V.dtype)
        for i in xrange(Q.shape[0]):
            Q[i] = fft(V[i])
        return Q
    else:
        raise Exception('FFT for %d dimensions not implemented' % V.ndim)

def ifft(V, verbose=False):
    if V.ndim == 0:
        return V.copy()
    elif V.ndim == 1:
        V = np.asarray(V, dtype=np.complex)
        return ifft1d(V, verbose)
    elif V.ndim > 1:
        V = np.asarray(V, dtype=np.complex)
        Q = np.empty(V.shape, V.dtype)
        for i in xrange(Q.shape[0]):
            Q[i] = ifft(V[i])
        return Q
    else:
        raise Exception('Inverse FFT for %d dimensions not implemented' % \
                        V.ndim)

def fft1d_rec(V, mode=0):
    N = V.shape[0]
    if N > 1:
        V1 = V[::2]
        V2 = V[1::2]
        V1 = fft1d_rec(V1, mode)
        V2 = fft1d_rec(V2, mode)
        A = np.arange(N/2, dtype=np.complex)
        if mode == 0:
            W = np.exp(-2*np.pi*A*1j/N)
        else:
            W = np.exp(+2*np.pi*A*1j/N)
        #V1 = np.array([V1, V1]).ravel()
        #V2 = np.array([V2, V2]).ravel()
        #A = np.arange(N, dtype=np.complex)
        #if mode == 0:
        #    W = np.exp(-2*np.pi*A*1j/N)
        #else:
        #    W = np.exp(+2*np.pi*A*1j/N)
        Q1 = V1 + W*V2
        Q2 = V1 - W*V2
        Q = np.array([Q1, Q2]).ravel()
        return Q
    else:
        return V

def fft1d(V, verbose=False):
    return fft1d_rec(V) / np.sqrt(V.shape[0])

def ifft1d(V, verbose=False):
    return fft1d_rec(V, mode=1) / np.sqrt(V.shape[0])

