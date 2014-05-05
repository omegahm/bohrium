/*
This file is part of Bohrium and copyright (c) 2012 the Bohrium team:
http://bohrium.bitbucket.org

Bohrium is free software: you can redistribute it and/or modify
it under the terms of the GNU Lesser General Public License as 
published by the Free Software Foundation, either version 3 
of the License, or (at your option) any later version.

Bohrium is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the 
GNU Lesser General Public License along with Bohrium. 

If not, see <http://www.gnu.org/licenses/>.
*/
#ifndef __BOHRIUM_BRIDGE_CPP_REDUCTION
#define __BOHRIUM_BRIDGE_CPP_REDUCTION

namespace bxx {

template <typename T>
multi_array<T>& reduce(multi_array<T>& op, reducible opcode, int64_t axis)
{
    if (axis<0) {
        axis = op.getRank()+axis;
    }
    if (axis >= (int64_t)op.getRank()) {
        throw std::runtime_error("Error: Axis out of bounds in reduction.\n");
    }
    multi_array<T>* result = &Runtime::instance().temp<T>();

    result->meta.start = 0;                 // Update meta-data
    if (op.meta.ndim == 1) {                // Pseudo-scalar; one element
        result->meta.ndim      = 1;
        result->meta.shape[0]  = 1;
        result->meta.stride[0] = op.meta.stride[0];
    } else {                                // Remove axis
        result->meta.ndim  = op.meta.ndim -1;
        int64_t stride = 1; 
        for(int64_t i=op.meta.ndim-1, j=result->meta.ndim-1; i>=0; --i) {
            if (i!=(int64_t)axis) {
                result->meta.shape[j]  = op.meta.shape[i];
                result->meta.stride[j] = stride;
                stride *= result->meta.shape[j];
                --j;
            }
        }
    }
    result->link();                         // Bind the base

    switch(opcode) {
        case ADD:
            bh_add_reduce(*result, op, (bh_int64)axis);
            break;

        case MULTIPLY:
            bh_multiply_reduce(*result, op, (bh_int64)axis);
            break;
        case MIN:
            bh_minimum_reduce(*result, op, (bh_int64)axis);
            break;
        case MAX:
            bh_maximum_reduce(*result, op, (bh_int64)axis);
            break;
        case LOGICAL_AND:
            bh_logical_and_reduce(*result, op, (bh_int64)axis);
            break;
        case LOGICAL_OR:
            bh_logical_or_reduce(*result, op, (bh_int64)axis);
            break;
        case LOGICAL_XOR:
            bh_logical_xor_reduce(*result, op, (bh_int64)axis);
            break;
        case BITWISE_AND:
            bh_bitwise_and_reduce(*result, op, (bh_int64)axis);
            break;
        case BITWISE_OR:
            bh_bitwise_or_reduce(*result, op, (bh_int64)axis);
            break;
        case BITWISE_XOR:
            bh_bitwise_xor_reduce(*result, op, (bh_int64)axis);
            break;

        default:
            throw std::runtime_error("Error: Unsupported opcode for reduction.\n");
    }

    return *result;
}

template <typename T>
multi_array<T>& sum(multi_array<T>& op)
{
    size_t dims = op.meta.ndim;

    multi_array<T>* result = &reduce(op, ADD, 0);
    for(size_t i=1; i<dims; i++) {
        result = &reduce(*result, ADD, 0);
    }
    return *result;
}

template <typename T>
multi_array<T>& product(multi_array<T>& op)
{
    size_t dims = op.meta.ndim;

    multi_array<T>* result = &reduce(op, MULTIPLY, 0);
    for(size_t i=1; i<dims; i++) {
        result = &reduce(*result, MULTIPLY, 0);
    }

    return *result;
}

template <typename T>
multi_array<T>& min(multi_array<T>& op)
{
    size_t dims = op.meta.ndim;

    multi_array<T>* result = &reduce(op, MIN, 0);
    for(size_t i=1; i<dims; i++) {
        result = &reduce(*result, MIN, 0);
    }
    return *result;
}

template <typename T>
multi_array<T>& max(multi_array<T>& op)
{
    size_t dims = op.meta.ndim;

    multi_array<T>* result = &reduce(op, MAX, 0);
    for(size_t i=1; i<dims; i++) {
        result = &reduce(*result, MAX, 0);
    }
    return *result;
}

template <typename T>
multi_array<bool>& any(multi_array<T>& op)
{
    size_t dims = op.meta.ndim;

    multi_array<T>* result = &reduce(op, LOGICAL_OR, 0);
    for(size_t i=1; i<dims; i++) {
        result = &reduce(*result, LOGICAL_OR, 0);
    }
    return *result;
}

template <typename T>
multi_array<bool>& all(multi_array<T>& op)
{
    size_t dims = op.meta.ndim;

    multi_array<T>* result = &reduce(op, LOGICAL_AND, 0);
    for(size_t i=1; i<dims; i++) {
        result = &reduce(*result, LOGICAL_AND, 0);
    }
    return *result;
}

template <typename T>
multi_array<size_t>& count(multi_array<T>& op)
{
    return sum(op.template as<size_t>());
}

}
#endif
