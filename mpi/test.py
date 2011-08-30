from mpi4py import MPI

comm = MPI.COMM_WORLD
size = comm.Get_size()
rank = comm.Get_rank()

if rank == 0:
    print 'size:', size

if rank == 0:
    data = []
else:
    data = comm.recv(source=rank-1, tag=rank)
print 'rank:', rank, 'data:', data
new_data = data + [rank]
if (rank+1) < size:
    comm.send(new_data, dest=rank+1, tag=rank+1)

