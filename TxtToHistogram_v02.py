# TxtToHistogram_v02.py
# Created: 07/28/2017
# By: Allison Davis, Wildlife Technician
# University of Kentucky, Department of Forestry and Natural Resources
# For: Jonathan Matthews, Graduate student
# Creates histogram from textfile
# Last Updated: 07/28/2017 11:30 AM

import os
import numpy as np
import random
from matplotlib import pyplot as plt

txtfile = arcpy.GetParameterAsText(0) # v02
outputimage = arcpy.GetParameterAsText(1)
# txtfile = str( input( "Input textfile: ") ) # v01

arcpy.AddMessage("Grabbing data from textfile...")
opentxtfile = open(txtfile, 'r')
counts = [line.split(',') for line in opentxtfile.readlines()]
counts = [ int(i) for i in counts[0][1:] ]

arcpy.AddMessage("Plotting histogram...")
bins = np.arange( min( counts ) - 2 , max( counts ) + 2, 1 )
plt.xlim( [ min( counts ) - 2, max( counts ) + 2 ] )
plt.hist( counts, bins = bins, alpha = 0.5)
plt.hist(counts, bins = bins, alpha = 0.5)
plt.title( os.path.basename(txtfile) )
plt.xlabel('Number of transects')
plt.ylabel('Number of iterations')
plt.savefig( outputimage )
