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
#ifndef __BOHRIUM_BRIDGE_CPP_RUNTIME_EXTENSIONS
#define __BOHRIUM_BRIDGE_CPP_RUNTIME_EXTENSIONS

namespace bxx {

template <typename T>
void bh_ext_visualizer(multi_array<T>& ary, multi_array<T>& args)
{
    Runtime::instance().enqueue_extension(
        "visualizer",
        ary,
        args,
        ary
    );
}

}
#endif
