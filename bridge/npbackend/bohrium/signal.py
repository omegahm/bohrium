"""
Signal Processing
~~~~~~~~~~~~~~~~~

Common signal processing functions, which often handle multiple dimension

"""
import bohrium as np
import numpy_force as numpy
from numpy_force.lib.stride_tricks import as_strided
from . import array_create
from . import bhary
from . import ufuncs
from . import linalg

# 1d
#---------------------------------------------------------------------------------
def _correlate_and_convolve_body(vector, filter, d, mode):
    """ The body of correlate() and convolve() are identical"""

    # Anything to do?
    if vector.size <= 0:
        return vector.copy()

    # Complex correlate includes a conjugation
    if numpy.iscomplexobj(filter):
        filter = numpy.conj(filter)

    dtype = numpy.result_type(vector, filter)
    rows = int(ufuncs.ceil((vector.size + 2 * filter.size - 2) / float(filter.size)))
    padded = array_create.empty([rows * filter.size], dtype=dtype)
    padded[0:filter.size - 1] = 0
    padded[filter.size - 1:vector.size + filter.size - 1] = vector
    padded[vector.size + filter.size - 1:] = 0
    s = as_strided(padded, shape=(padded.shape[0] - filter.size + 1, filter.size),
                   strides=(padded.strides[0], padded.strides[0]))
    result = linalg.dot(s, filter)
    if mode == 'same':
        return result[d:vector.size + d]
    elif mode == 'full':
        return result[0:vector.size + filter.size - 1]
    elif mode == 'valid':
        return result[filter.size - 1:vector.size]
    else:
        raise ValueError("correlate1d: invalid mode '%s'" % mode)


def correlate1d(a, v, mode='valid'):
    assert a.ndim == 1
    assert v.ndim == 1

    # Let's make sure that we are working on Bohrium arrays
    if not bhary.check(a) and not bhary.check(v):
        return numpy.correlate(a, v, mode)
    else:
        a = array_create.array(a)
        v = array_create.array(v)

    # We might have to swap `a` and `v` such that `vector` is always largest
    if v.shape[0] > a.shape[0]:
        vector = v[::-1]
        filter = a[::-1]
        d = int(filter.size / 2)
    else:
        vector = a
        filter = v
        d = int((filter.size - 1) / 2)
    return _correlate_and_convolve_body(vector, filter, d, mode)


def convolve1d(a, v, mode='full'):
    assert a.ndim == 1
    assert v.ndim == 1

    # Let's make sure that we are working on Bohrium arrays
    if not bhary.check(a) and not bhary.check(v):
        return numpy.convolve(a, v, mode)
    else:
        a = array_create.array(a)
        v = array_create.array(v)

    # We might have to swap `a` and `v` such that `vector` is always largest
    if v.shape[0] > a.shape[0]:
        vector = v
        filter = a[::-1]
    else:
        vector = a
        filter = v[::-1]
    d = int((filter.size - 1) / 2)
    return _correlate_and_convolve_body(vector, filter, d, mode)
 
# Nd
#---------------------------------------------------------------------------------
def _findIndices(ArrSize,FilterSize):
    N=FilterSize.shape[0]
    n=int(FilterSize.prod())
    CumSizeArr=np.ones([N],dtype=np.int32)
    CumSizeArr[1:N]=ArrSize[0:N-1].cumprod()
    CumSize=np.ones([N],dtype=np.int32)
    CumSize[1:N]=FilterSize[0:N-1].cumprod()
    
    vals=np.empty((n,N),dtype=np.int32)
    for i in range(N):
        vals[:,i]=np.linspace(0,n-1,n)

    vals=ufuncs.floor(vals/CumSize)
    vals=vals%FilterSize
    CurrPos=np.sum(vals*CumSizeArr,axis=1)
    
    return CurrPos.astype(np.int32)

def _addZerosNd(Array,FilterSize,dtype):
    # Introduces zero padding for Column major flattening
    PaddedSize=np.asarray(Array.shape,dtype=np.int32)
    N=FilterSize.shape[0]
    PaddedSize[0:N]+=FilterSize-1
    cut='['
    for i in range(PaddedSize.shape[0]):
        if i<N:
            minpos=int(FilterSize[i]/2)
            maxpos=Array.shape[i]+int(FilterSize[i]/2)
        else:
            minpos=0
            maxpos=Array.shape[i]
        cut+=str(minpos)+':'+str(maxpos)+','
    cut=cut[:-1]+']'
    Padded=np.zeros(PaddedSize,dtype=dtype)
    exec('Padded'+cut+'=Array')
    return Padded

def _findSame(Array,FilterSize):
    # Numpy convention. Returns view of the same size as the largest input
    N=FilterSize.shape[0]
    cut='['
    for i in range(len(Array.shape)):
        if i<N:
            minpos=(FilterSize[i]-1)//2
            maxpos=Array.shape[i]-(FilterSize[i])//2
        else:
            minpos=0
            maxpos=Array.shape[i]
        cut+=str(minpos)+':'+str(maxpos)+','
    cut=cut[:-1]+']'
    res=eval('Array'+cut)
    return res

def _findValid(Array,FilterSize):
    # Cuts the result down to only totally overlapping views
    N=FilterSize.shape[0]
    cut='['
    for i in range(len(Array.shape)):
        if i<N:
            minpos=FilterSize[i]-1
            maxpos=Array.shape[i]-FilterSize[i]+1
        else:
            minpos=0
            maxpos=Array.shape[i]
        cut+=str(minpos)+':'+str(maxpos)+','
    cut=cut[:-1]+']'
    res=eval('Array'+cut)
    return res

def _invertArr(Array):
    # Returns a view of array with all dimensions reversed
    for i in range(len(Array.shape)):
        Array=np.flip(Array,axis=i)
    return Array

def _correlate_kernel(Array,Filter,mode):
    # Anything to do?
    if Array.size <= 0:
        return Array.copy()

    # Complex correlate includes a conjugation
    if numpy.iscomplexobj(Filter):
        Filter = numpy.conj(Filter)
    
    # Get sizes as arrays for easier manipulation
    ArrSize=np.asarray(Array.shape,dtype=np.int32)
    FilterSize=np.asarray(Filter.shape,dtype=np.int32)

    # Check that mode='valid' is allowed given the array sizes
    if mode=='valid':
        diffSize=ArrSize[:FilterSize.size]-FilterSize
        nSmaller=np.sum(diffSize<0)
        if nSmaller>0:
            raise ValueError("correlateNd: For 'valid' mode, one must be at least as large as the other in every dimension")

    # Use numpy convention for result dype
    dtype = numpy.result_type(Array, Filter) 
    
    # Add zeros along relevant dimensions
    Padded=_addZerosNd(Array,FilterSize,dtype)
    PaddedSize=np.asarray(Padded.shape,dtype=np.int32)
    
    # Get positions of first view
    IndiVec=_findIndices(PaddedSize,FilterSize)
    CenterPos=tuple((FilterSize-1)//2)
    IndiMat=IndiVec.reshape(FilterSize,order='F')
    nPre=IndiMat[CenterPos] # Required zeros before Array for correct alignment
    nPost=IndiVec[Filter.size-1]-nPre 
    n=Padded.size
    nTot=n+nPre+nPost # Total size after pre/post padding
    V=np.empty([nTot],dtype=dtype)
    V[nPre:n+nPre]=Padded.flatten(order='F')
    V[:nPre]=0
    V[n+nPre:]=0
    A=Filter.flatten(order='F')
    
    # Actual correlation calculation
    Correlated=np.empty([n],dtype=dtype)
    Correlated=V[IndiVec[0]:n+IndiVec[0]]*A[0]
    for i in range(1,Filter.size):
        Correlated+=V[IndiVec[i]:n+IndiVec[i]]*A[i]
    
    Full=Correlated.reshape(PaddedSize,order='F')
    if mode=='full':
        return Full
    elif mode=='same':
        return _findSame(Full,FilterSize)
    elif mode=='valid':
        return _findValid(Full,FilterSize)
    else:
        raise ValueError("correlateNd: invalid mode '%s'" % mode)

def convolveNd(a,v,mode='full'):
    # Let's make sure that we are working on Bohrium arrays
    if not bhary.check(a) and not bhary.check(v):
        raise TypeError("convolveNd: Expects Bohrium arrays")
        
    if a.size>v.size:
        Array=a
        Filter=_invertArr(v)
    else:
        Array=v
        Filter=_invertArr(a)
    return _correlate_kernel(Array,Filter,mode)

def correlateNd(a,v,mode='valid'):
    # Let's make sure that we are working on Bohrium arrays
    if not bhary.check(a) and not bhary.check(v):
        raise TypeError("correlateNd: Expects Bohrium arrays")
    
    if a.size>v.size:
        Array=a
        Filter=v
    else:
        Array=_invertArr(v)
        Filter=_invertArr(a)
    return _correlate_kernel(Array,Filter,mode)
