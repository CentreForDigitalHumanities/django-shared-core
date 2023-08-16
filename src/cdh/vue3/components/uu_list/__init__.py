"""UU-List is a Vue component implementing a UU-designed list view
with filtering, searching, ordering and pagination support.

The base UU-List component (from cdh-vue-lib) is UI only, requiring
any user to implement data fetching on their own.

In addition, the UU-List does not, by default, have any way of
visualizing the data. Instead, this is left to a 'Visualizer'
component. It does, however, provide the Data-Defined Visualizer
(DDV) as a pre-written visualizer that can be used.

This package provides a pre-compiled implementation of UU-List using
the DDV, already setup to fetch and process data from Django.
It also provides the necessary backend code to easily provide the
required views for this pre-compiled version of UU-List.

Any implementer should be able to use both to quickly set up a page
using UU-List, without any custom JS required. An example of a complete
setup can be found in the DSC dev project.
The source code of this pre-compiled version can be found in assets/vue/uu-list.

However, the DDV is limited in its configurability. If you need to
implement more advanced visualisation, you will need to compile
your own version of UU-List. The assets dir in the DSC project
provides an example to get you started. This example already
contains all the hooks needed to tap into the provided backend classes,
you will only eed to write a custom visualizer.
"""
from .columns import *
from .paginator import *
from .serializers import *
from .views import *
