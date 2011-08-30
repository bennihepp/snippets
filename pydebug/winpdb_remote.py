import rpdb2
#rpdb2.start_embedded_debugger("abc")

import time

for i in xrange(1024):
    print i

rpdb2.settrace()

for j in xrange(5):
    time.sleep(1)
    print j


