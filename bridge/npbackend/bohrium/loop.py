"""
Bohrium Loop
============
"""

import sys
import numpy_force as numpy
from . import _bh
from . import bhary
from . import array_create


def do_while(func, niters, *args, **kwargs):
    """Repeatedly calls the `func` with the `*args` and `**kwargs` as argument.

    The `func` is called while `func` returns True or None and the maximum number
    of iterations, `niters`, hasn't been reached.

    Parameters
    ----------
    func : function
        The function to run in each iterations. `func` can take any argument and may return
        a boolean `bharray` with one element.
    niters: int or None
        Maximum number of iterations in the loop (number of times `func` is called). If None, there is no maximum.
    *args, **kwargs : list and dict
        The arguments to `func`

    Notes
    -----
    `func` can only use operations supported natively in Bohrium.

    Examples
    --------
    >>> def loop_body(a):
    ...     a += 1
    >>> a = bh.zeros(4)
    >>> bh.do_while(loop_body, 5, a)
    >>> a
    array([5, 5, 5, 5])

    >>> def loop_body(a):
    ...     a += 1
    ...     return bh.sum(a) < 10
    >>> a = bh.zeros(4)
    >>> bh.do_while(loop_body, None, a)
    >>> a
    array([3, 3, 3, 3])
    """

    _bh.flush()
    flush_count = _bh.flush_count()
    cond = func(*args, **kwargs)
    if flush_count != _bh.flush_count():
        raise TypeError("Invalid `func`: the looped function contains operations not support "
                        "by Bohrium, contain branches, or is simply too big!")
    if niters is None:
        niters = sys.maxsize-1
    if cond is None:
        _bh.flush_and_repeat(niters, None)
    else:
        if not bhary.check(cond):
            raise TypeError("Invalid `func`: `func` may only return Bohrium arrays or nothing at all")
        if cond.dtype.type is not numpy.bool_:
            raise TypeError("Invalid `func`: `func` returned array of wrong type `%s`. "
                            "It must be of type `bool`." % cond.dtype)
        if len(cond.shape) != 0 and len(cond) > 1:
            raise TypeError("Invalid `func`: `func` returned array of shape `%s`. "
                            "It must be a scalar or an array with one element." % cond.shape)
        if not bhary.is_base(cond):
            raise TypeError("Invalid `func`: `func` returns an array view. It must return a base array.")

        _bh.sync(cond)
        _bh.flush_and_repeat(niters, cond)

def for_loop(loop_body, niters, *args, **kwargs):
    """Calls the `loop_body` with the `*args` and `**kwargs` as argument.

    The `loop_body` is called `niters` times.

    Parameters
    ----------
    loop_body : function
        The function to run in each iterations. `func` can take any arguments.
    niters: int
        Number of iterations in the loop (number of times `loop_body` is called).
    *args, **kwargs : list and dict
        The arguments to `func`

    Notes
    -----
    `func` can only use operations supported natively in Bohrium.

    Examples
    --------
    """

    # The number of iterations must be positive
    if niters < 1: return

    # Clear the cache
    _bh.flush()

    flush_count = _bh.flush_count()
    loop_body(*args, **kwargs)
    if flush_count != _bh.flush_count():
        raise TypeError("Invalid `func`: the looped function contains operations not support "
                        "by Bohrium, contain branches, or is simply too big!")

    _bh.flush_and_repeat(niters, None)

def slide_view(a, dim_stride_tuples):
    """Creates a dynamic view within a loop, that updates the given dimensions by the given strides at the end of each iteration.

    Parameters
    ----------
    a : array view
        A view into an array
    dim_stride_tuples: (int, int)[]
        A list of (dimension, stride) pairs. For each of these pairs, the dimension is updated by the stride in each iteration of a loop.

    Notes
    -----
    No boundary checks are performed. If the view overflows the array, the behaviour is undefined.
    All dyn_views must be at the top of the loop body.
    All views are changed at the end of an iteration and cannot be performed in the middle of a loop body.

    Examples
    --------
    """

    # Allocate a new view
    b = a

    # Set the relevant update conditions for the new view
    for (dim, stride) in dim_stride_tuples:
        _bh.slide_view(b, dim, stride)
    return b

def iterator_loop(kernel, niters, *args):
    for_loop(kernel, niters, *args)

class iterator(int):
    def __new__(cls, value, *args, **kwargs):
        return super(iterator, cls).__new__(cls, value)

    def __add__(self, other):
        res = super(iterator, self).__add__(other)
        return self.__class__(res)

    def __minus__(self, other):
        res = super(iterator, self).__minus__(other)
        return self.__class__(res)

def get_iterator(val = 0):
    return iterator(val)

def has_iterator(s):
    return isinstance(s.start, iterator) or \
           isinstance(s.stop, iterator)

# class it_array(_bh.ndarray):
#     def __getitem__(self, sliced):
#         if isinstance(sliced, tuple):
#             new_slices = ()
#             slides = []
#             for i, s in enumerate(sliced):
#                 if isinstance(s, slice) and has_iterator(s):
#                     new_slices += (slice(s.start, s.stop),)
#                     slides.append((i, int(s.step)))
#             return slide_view(self[new_slices], slides)
#         elif isinstance(sliced, slice) and has_iterator(sliced):
#             return slide_view(
#                 self[sliced.start:sliced.stop],
#                 [(0, int(sliced.step))])
#         else:
#             return self[sliced]

class Wrapper(object):
    """Wrapper class that provides proxy access to an instance of some
       internal instance."""

    __wraps__  = None
    __ignore__ = "class mro new init setattr getattr getattribute"

    def __init__(self, obj):
        if self.__wraps__ is None:
            raise TypeError("base class Wrapper may not be instantiated")
        elif isinstance(obj, self.__wraps__):
            self._obj = obj
        else:
            raise ValueError("wrapped object must be of %s" % self.__wraps__)

    # provide proxy access to regular attributes of wrapped object
    def __getattr__(self, name):
        return getattr(self._obj, name)

    # create proxies for wrapped object's double-underscore attributes
    class __metaclass__(type):
        def __init__(cls, name, bases, dct):

            def make_proxy(name):
                def proxy(self, *args):
                    return getattr(self._obj, name)
                return proxy

            type.__init__(cls, name, bases, dct)
            if cls.__wraps__:
                ignore = set("__%s__" % n for n in cls.__ignore__.split())
                for name in dir(cls.__wraps__):
                    if name.startswith("__"):
                        if name not in ignore and name not in dct:
                            setattr(cls, name, property(make_proxy(name)))

class it_array(Wrapper):
    __wraps__ = _bh.ndarray

    def __getslice__(self, a, b):
        return slide_view(self._obj[a:b], [(0,1)])

    def __getitem__(self, sliced):
        if isinstance(sliced, tuple):
            new_slices = ()
            slides = []
            for i, s in enumerate(sliced):
                if isinstance(s, slice) and has_iterator(s):
                    new_slices += (slice(s.start, s.stop),)
                    slides.append((i, int(s.step)))
            return slide_view(self._obj[new_slices], slides)
        elif isinstance(sliced, slice) and has_iterator(sliced):
            if sliced.step:
                return slide_view(
                    self._obj[sliced.start:sliced.stop],
                    [(0, int(sliced.step))])
            else:
                return slide_view(
                    self._obj[sliced.start:sliced.stop],
                    [(0, 1)])
        else:
            return self._obj[sliced]



# class it_array(object):
#     def __init__(self, a):
#         self.array = a

#     def __getitem__(self, sliced):
#         print("WHAAATTZZ")
#         if isinstance(sliced, tuple):
#             new_slices = ()
#             slides = []
#             for i, s in enumerate(sliced):
#                 if isinstance(s, slice) and has_iterator(s):
#                     new_slices += (slice(s.start, s.stop),)
#                     slides.append((i, int(s.step)))
#             return slide_view(self.array[new_slices], slides)
#         elif isinstance(sliced, slice) and has_iterator(sliced):
#             if sliced.step:
#                 return slide_view(
#                     self.array[sliced.start:sliced.stop],
#                     [(0, int(sliced.step))])
#             else:
#                 return slide_view(
#                     self.array[sliced.start:sliced.stop],
#                     [(0, 1)])

#         else:
#             return self.array

#    def __setitem__(self, *args):
#        self.array.__setitem__(*args)

#    def __getattr__(*args):

#        self.array.__getattribute__(*args)
