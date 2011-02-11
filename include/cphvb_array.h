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

#ifndef __CPHVB_ARRAY_H
#define __CPHVB_ARRAY_H

#include "cphvb_type.h"

#define CPHVB_MAXDIM (16)

#define CPHVB_MAX_EXTRA_META_DATA (1024)

// Operand id used to indicate that the operand is a scalar constant
#define CPHVB_CONSTANT (NULL)

// Memory layout of an array
typedef struct
{
    //Field used by VEM to manage ownership
    cphvb_int32      owner;
    //Pointer to the base array. If NULL this is a base array
    cphvb_array*     base;
    //The type of data in the array
    cphvb_type       type;
    //Number of dimentions
    cphvb_int32      ndim;
    //Index of the start element (always 0 for base-array)
    cphvb_index      start;
    //Number of elements in each dimention
    cphvb_index      shape[CPHVB_MAXDIM];
    //The stride for each dimention
    cphvb_index      stride[CPHVB_MAXDIM];
    //Pointer to the actual data
    void*            data;
    //Does the array have an initial value (if not initialized)
    cphvb_int32      has_init_value;
    //The initial value
    cphvb_constant   init_value;
    //Ref Count
    cphvb_int32      ref_count;
    //Space reserved for extra meta data.
    //Not persistent at ownership change
    char             extra_meta_data[CPHVB_MAX_EXTRA_META_DATA];
} cphvb_array;


#endif
