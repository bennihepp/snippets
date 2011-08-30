#from subprocess import Popen,PIPE
#hostname = Popen('hostname',stdout=PIPE).communicate()[0]
#f = open('/g/pepperkok/hepp/code/mpi/mpi_%s.log'%hostname,'w')
#f.write('abc')
#f.close()

from mpi4py import MPI

comm = MPI.COMM_WORLD
name = MPI.Get_processor_name()
size = comm.Get_size()
rank = comm.Get_rank()

if rank == 0:
    import mpi4py
    print mpi4py
    print 'size:', size

if rank == 0:
    data = []
else:
    data = comm.recv(source=rank-1, tag=rank)
print 'rank:', rank, 'name:', name, 'data:', data
new_data = data + [rank]
if (rank+1) < size:
    comm.send(new_data, dest=rank+1, tag=rank+1)

