import sys
import struct
import numpy as np

output_filename = sys.argv[1]
length = int(sys.argv[2])

data = np.random.randint(0, 2**31-1, length)

with open(output_filename, 'w') as f:
    s = struct.pack('>i', length)
    f.write(s)
    s = struct.pack('>%di' % length, *data)
    f.write(s)

