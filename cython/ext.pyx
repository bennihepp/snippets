def func(int a, int b):
    cdef int c, d, i
    c = 0
    d = 5
    for i in xrange(20,1,-1):
        c = d + i
    print c
    return c

