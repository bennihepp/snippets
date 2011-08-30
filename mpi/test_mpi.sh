#!/bin/bash

export LD_LIBRARY_PATH=/g/software/linux/pack/openmpi-1.4.3/lib:$LD_LIBRARY_PATH
#mpiexec-1.4.3 -x LD_LIBRARY_PATH=$LD_LIBRARY_PATH -v -nolocal -n 1 openmpi-python-2.7 /g/pepperkok/hepp/code/mpi/mpi_test2.py
#/g/software/bin/mpiexec-1.4.3 $PBS_NODEFILE -v -n $N -x LD_LIBRARY_PATH="$LD_LIBRARY_PATH" /bin/bash /g/pepperkok/hepp/code/mpi/job.sh
/g/software/bin/mpiexec-1.4.3 -nolocal -v hostname

