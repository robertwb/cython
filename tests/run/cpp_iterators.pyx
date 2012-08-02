# tag: cpp

from libcpp.vector cimport vector

cdef extern from "cpp_iterators_simple.h":
    cdef cppclass DoublePointerIter:
        DoublePointerIter(double* start, int len)
        double* begin()
        double* end()

def test_vector(py_v):
    """
    >>> test_vector([1, 2, 3])
    [1, 2, 3]
    """
    cdef vector[int] v = py_v
    cdef vector[int] result
    with nogil:
        for item in v:
            result.push_back(item)
    return result

def test_ptrs():
    """
    >>> test_ptrs()
    [1.0, 2.0, 3.0]
    """
    cdef double a = 1
    cdef double b = 2
    cdef double c = 3
    cdef vector[double*] v
    v.push_back(&a)
    v.push_back(&b)
    v.push_back(&c)
    return [item[0] for item in v]

def test_custom():
    """
    >>> test_custom()
    [1.0, 2.0, 3.0]
    """
    cdef double* values = [1, 2, 3]
    cdef DoublePointerIter* iter
    try:
        iter = new DoublePointerIter(values, 3)
        # TODO: It'd be nice to automatically dereference this in a way that
        # would not conflict with the pointer slicing iteration.
        return [x for x in iter[0]]
    finally:
        del iter
