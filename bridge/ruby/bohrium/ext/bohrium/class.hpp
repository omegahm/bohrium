#pragma once

using namespace std;

/**
    Creates an array of the given size and value using Bohriums identity method.

    @param result The data object to add the result to.
    @param width The width of the array.
    @param height The height of the array.
    @param value The value each element should have.
    @param type The Ruby type of this value.
*/
template <typename T>
inline void _identity(VALUE res, unsigned long width, unsigned long height, T value, ruby_value_type type) {
    bhDataObj<T> *result;
    Data_Get_Struct(res, bhDataObj<T>, result);
    bhxx::BhArray<T> bhary = *(new bhxx::BhArray<T>({width, height}));
    bhxx::identity(bhary, value);
    result->type = type;
    result->bhary = bhary;
}

/**
    Create an array and fill it with ones (or value given).

    @param argc Number of elements in argv.
    @param argv The arguments given the method from Ruby.
    @param klass The class we are defining on.
    @return The created array.
*/
VALUE bh_array_s_ones(int argc, VALUE *argv, VALUE klass) {
    unsigned long x = 1, y = 1;

    VALUE res = bh_array_alloc(klass);

    if(argc >= 1) { x = NUM2INT(argv[0]); }
    if(argc >= 2) { y = NUM2INT(argv[1]); }
    if(argc >= 3) {
        switch (TYPE(argv[2])) {
            case T_FIXNUM:
                _identity(res, x, y, (int64_t) NUM2INT(argv[2]), T_FIXNUM);
                break;
            case T_FLOAT:
                _identity(res, x, y, (float) NUM2DBL(argv[2]), T_FLOAT);
                break;
            case T_TRUE:
                _identity(res, x, y, true, T_TRUE);
                break;
            case T_FALSE:
                _identity(res, x, y, false, T_FALSE);
                break;
            default:
                rb_raise(rb_eRuntimeError, "Wrong type for array given.");
        }
    } else {
        _identity(res, x, y, (int64_t) 1, T_FIXNUM);
    }

    return res;
}

/**
    Create an array and fill it with zeros.

    @param argc Number of elements in argv.
    @param argv The arguments given the method from Ruby.
    @param klass The class we are defining on.
    @return The created array.
*/
VALUE bh_array_s_zeros(int argc, VALUE *argv, VALUE klass) {
                     argv[2] = INT2NUM(0);   // Force 'value' to 0
    if (argc <= 1) { argv[1] = INT2NUM(1); } // Force 'y' to 1, if not given
    if (argc <= 0) { argv[0] = INT2NUM(1); } // Force 'x' to 1, if not given
    return bh_array_s_ones(3, argv, klass);
}

/**
    Helper function to create a sequence array.

    @param res The resulting array.
    @param nelems The number of elements in the sequence.
    @param type The type of the resulting array.
*/
inline void _range(VALUE res, unsigned long nelems, ruby_value_type type) {
    bhDataObj<uint64_t> *result;
    Data_Get_Struct(res, bhDataObj<uint64_t>, result);
    bhxx::BhArray<uint64_t> bhary = *(new bhxx::BhArray<uint64_t>({nelems, 1}));
    bhxx::range(bhary);
    result->type = type;
    result->bhary = bhary;
}

/**
    Create an array and fill it with a sequence.

    @param klass The class we are defining on.
    @param limit The number of elements in the resulting array.
    @return The created array.
*/
VALUE bh_array_s_arange(VALUE klass, VALUE limit) {
    VALUE res = bh_array_alloc(klass);

    if (NUM2INT(limit) <= 0) {
        rb_raise(rb_eRuntimeError, "Argument for 'arange' cannot be negative or zero.");
    }

    switch (TYPE(limit)) {
        case T_FIXNUM:
            _range(res, NUM2INT(limit), T_FIXNUM);
            break;
        default:
            rb_raise(rb_eRuntimeError, "Wrong type for array given.");
    }

    return res;
}
