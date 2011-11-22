#!/usr/bin/env python
from pprint import pprint as pp
import numpy as np
import time
import sys

CPHVB   = True
size    = 3

try:
    CPHVB   = int(sys.argv[1])
    size    = int(sys.argv[2])
except:
    pass

def main():

    y = 3
    x = np.array([[range(1,size+1)]*size]*size, dtype=np.float32, dist=CPHVB)
    print "x: \n", x
    print "y: ", y
    print np.add( x, y )

if __name__ == "__main__":
    main()
