#!/bin/bash

export LD_LIBRARY_PATH=/g/software/linux/pack/python-2.7/lib
lamboot
mpirun C $*
lamclean
lamhalt

