import ext

def pycallback(a,b):
    print 'pycallback(%s,%s)' % (a,b)
    return ('abc',123)

ext.set_callback(pycallback)

ext.run()

