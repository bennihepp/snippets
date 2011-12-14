import numpy as np

def dft(V, verbose=False):
    if V.ndim == 0:
        return V.copy()
    elif V.ndim == 1:
        return dft1d(V, verbose)
    elif V.ndim == 2:
        return dft2d(V, verbose)
    else:
        raise Exception('DFT for %d dimensions not implemented' % V.ndim)

def idft(V, verbose=False):
    if V.ndim == 0:
        return V.copy()
    elif V.ndim == 1:
        return idft1d(V, verbose)
    elif V.ndim == 2:
        return idft2d(V, verbose)
    else:
        raise Exception('Inverse DFT for %d dimensions not implemented' % \
                        V.ndim)

def dft1d(V, verbose=False):
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

def idft1d(V, verbose=False):
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

def dft2d(V, verbose=False):
    V = np.asarray(V, dtype=np.complex)
    N = V.shape[0]
    M = V.shape[1]
    A = np.mgrid[0:N,0:N]
    B = np.mgrid[0:M,0:M]
    A = A[0] * A[1]
    B = B[0] * B[1]
    A = np.asarray(A, dtype=np.complex) / N
    B = np.asarray(B, dtype=np.complex) / M
    kernelA = np.exp(-2*np.pi*A*1j)
    kernelB = np.exp(-2*np.pi*B*1j)
    Q = V
    Q = Q[:,np.newaxis,:] * kernelA[:,:,np.newaxis]
    Q = Q[:,:,:,np.newaxis] * kernelB[np.newaxis,np.newaxis,:,:]
    Q = np.sum(Q, axis=2) / np.sqrt(N*M)
    Q = np.sum(Q, axis=0)
    return Q

def idft2d(V, verbose=False):
    V = np.asarray(V, dtype=np.complex)
    N = V.shape[0]
    M = V.shape[1]
    A = np.mgrid[0:N,0:N]
    B = np.mgrid[0:M,0:M]
    A = A[0] * A[1]
    B = B[0] * B[1]
    A = np.asarray(A, dtype=np.complex) / N
    B = np.asarray(B, dtype=np.complex) / M
    kernelA = np.exp(+2*np.pi*A*1j)
    kernelB = np.exp(+2*np.pi*B*1j)
    Q = V
    Q = Q[:,np.newaxis,:] * kernelA[:,:,np.newaxis]
    Q = Q[:,:,:,np.newaxis] * kernelB[np.newaxis,np.newaxis,:,:]
    Q = np.sum(Q, axis=2) / np.sqrt(N*M)
    Q = np.sum(Q, axis=0)
    return Q

