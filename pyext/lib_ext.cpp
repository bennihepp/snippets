#include <boost/python.hpp>
using namespace boost::python;

#include "lib.hpp"

BOOST_PYTHON_MODULE(lib_ext)
{
    def("greet", lib::greet);
    def("square", lib::square);
}

