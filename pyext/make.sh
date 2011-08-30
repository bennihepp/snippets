#!/bin/bash

g++ -c -fPIC -I/opt/local/Library/Frameworks/Python.framework/Versions/2.7/include/python2.7 -I/opt/local/include lib.cpp -o lib
g++ -shared -W1,-soname,liblib.so lib.o lib.o -o liblib.so
echo liblib built
g++ -shared -c -fPIC -I/opt/local/Library/Frameworks/Python.framework/Versions/2.7/include/python2.7 -I/opt/local/include lib_ext.cpp -o lib_ext.o
echo 2
g++ -shared -W1,-soname,lib_ext.so -L/opt/local/lib -lpython2.7 -lboost_python lib.o lib_ext.o -o lib_ext.so
echo 3

