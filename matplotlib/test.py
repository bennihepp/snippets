import matplotlib
matplotlib.use('TkAgg')
import numpy
from matplotlib import pyplot
import time

bins = 5
data = [ 1, 2, 3, 4, 5, 1, 1, 1, 3, 4, 5, 5, 2, 3, 5, 5, 5, 5, 5, 5, 5, 5, 4, 4 ]


tmp = numpy.zeros( ( bins, ), int )
for d in data:
	tmp[ d - 1 ] += 1

left = numpy.arange(bins)
f = pyplot.figure()
f.add_subplot(111)

pyplot.bar( left, tmp, facecolor='yellow', alpha=0.75, align='center' )
pyplot.grid( True )

xaxis = f.axes[0].get_xaxis()
print xaxis.get_ticklocs(False)
print xaxis.get_ticklocs(True)
axes = f.axes[0]
axes.set_xticks( left )
axes.set_xticklabels( ['a','b','c','d','e'])

pyplot.show()

