/*
 * Copyright 2011 Troels Blum <troels@blum.dk>
 *
 * This file is part of cphVB.
 *
 * cphVB is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * cphVB is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with cphVB.  If not, see <http://www.gnu.org/licenses/>.
 */

#include <cphvb.h>
#include <assert.h>
#include <stdlib.h>
#include <string.h>

/* Reduce nDarray info to a base shape
 *
 * Remove dimentions that just indicate orientation in a
 * higher dimention (Py:newaxis)
 *
 * @ndim          Number of dimentions
 * @shape[]       Number of elements in each dimention.
 * @stride[]      Stride in each dimention.
 * @base_ndim     Placeholder for base number of dimentions
 * @base_shape    Placeholder for base number of elements in each dimention.
 * @base_stride   Placeholder for base stride in each dimention.
 */
void cphvb_base_shape(cphvb_intp ndim,
                      const cphvb_index shape[],
                      const cphvb_index stride[],
                      cphvb_intp* base_ndim,
                      cphvb_index* base_shape,
                      cphvb_index* base_stride)
{
    *base_ndim = 0;
    for (int i = 0; i < ndim; ++i)
    {
        // skipping (shape[i] == 1 && stride[i] == 0)
        if (shape[i] != 1 || stride[i] != 0)
        {
            base_shape[*base_ndim] = shape[i];
            base_stride[*base_ndim] = stride[i];
            ++(*base_ndim);
        }
    }
}

/* Is the data accessed continuously, and only once
 *
 * @ndim     Number of dimentions
 * @shape[]  Number of elements in each dimention.
 * @stride[] Stride in each dimention.
 * @return   Truth value indicating continuousity.
 */
bool cphvb_is_continuous(cphvb_intp ndim,
                         const cphvb_index shape[],
                         const cphvb_index stride[])
{
    cphvb_intp my_ndim = 0;
    cphvb_index my_shape[ndim];
    cphvb_index my_stride[ndim];
    cphvb_base_shape(ndim, shape, stride, &my_ndim, my_shape, my_stride);
    for (int i = 0; i < my_ndim - 1; ++i)
    {
        if (my_shape[i+1] != my_stride[i])
            return true;
    }
    if (my_stride[my_ndim-1] != 1)
        return false;

    return true;
}

/* Number of element in a given shape
 *
 * @ndim     Number of dimentions
 * @shape[]  Number of elements in each dimention.
 * @return   Number of element operations
 */
cphvb_index cphvb_nelements(cphvb_intp ndim,
                            const cphvb_index shape[])
{
    cphvb_index res = 1;
    for (int i = 0; i < ndim; ++i)
    {
        res *= shape[i];
    }
    return res;
}

/* Calculate the offset into an array based on element index
 *
 * @ndim     Number of dimentions
 * @shape[]  Number of elements in each dimention.
 * @stride[] Stride in each dimention.
 * @element  Index of element in question
 * @return   Truth value indicating continuousity.
 */
cphvb_index cphvb_calc_offset(cphvb_intp ndim,
                              const cphvb_index shape[],
                              const cphvb_index stride[],
                              const cphvb_index element)
{
    cphvb_intp dimIndex;
    cphvb_intp dim = ndim -1;
    cphvb_index dimBound = shape[dim];
    cphvb_index offset = (element % dimBound) * stride[dim];
    for (--dim; dim >= 0 ; --dim)
    {
        if (stride[dim] > 0)
        {
            dimIndex = element % (dimBound * shape[dim]);
            dimIndex = dimIndex / dimBound; 
            offset = offset + dimIndex * stride[dim];
            dimBound *= shape[dim];
        }
    }
    return offset;
}

/* Find the base array for a given array/view
 *
 * @view   Array/view in question
 * @return The Base array
 */
cphvb_array* cphvb_base_array(cphvb_array* view)
{
    if(view->base == NULL)
    {
        return view;
    }
    else
    {
        assert(view->base->base == NULL);
        return view->base;
    }
}

/* Allocate data memory for the given array if not already allocated.
 * Initialize the memory if needed.
 * For convenience array is allowed to be NULL.
 *
 * @array  The array in question
 * @return Error code (CPHVB_SUCCESS, CPHVB_OUT_OF_MEMORY)
 */
cphvb_error cphvb_malloc_array_data(cphvb_array* array)
{
    cphvb_intp i, nelem;
    cphvb_array* base;
    int dtypesize;

    if(array == NULL)
        return CPHVB_SUCCESS;

    base = cphvb_base_array(array);

    if(base->data != NULL)
        return CPHVB_SUCCESS;

    assert(base->data == NULL);
    nelem = cphvb_nelements(base->ndim, base->shape);
    dtypesize = cphvb_type_size(base->type);
    base->data = malloc(nelem * dtypesize);
    if(base->data == NULL)
        return CPHVB_OUT_OF_MEMORY;

    if(base->has_init_value)
        for(i=0; i<nelem; ++i)
            memcpy(base->data+i*dtypesize, &base->init_value, dtypesize);

    return CPHVB_SUCCESS;
}
