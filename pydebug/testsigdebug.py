import time

import sigdebug, signal
sigdebug.listen(signal.SIGINT)

abc = 123

while True:
    print 'time:', time.time(), 'abc:', abc
    time.sleep(2)
    if abc == 0:
        break

