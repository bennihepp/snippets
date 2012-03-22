import sys
import struct
import numpy as np

input_filename = sys.argv[1]
output_filename = sys.argv[2]

with open(input_filename, 'r') as f:
    length = struct.unpack('@i', f.read(4))[0]
    s = f.read(length * 4)
    data = struct.unpack('@%di' % length, s)

with open(output_filename, 'w') as f:
    s = struct.pack('>i', length)
    f.write(s)
    s = struct.pack('>%di' % length, *data)
    f.write(s)

