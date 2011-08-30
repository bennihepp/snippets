from mpi4py import MPI
import subprocess

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()
#print 'rank:', rank
stdout,stderr = subprocess.Popen(
        'hostname', stdout=subprocess.PIPE).communicate()
hostname = stdout.strip()

msg = 'rank %d running on %s' % (rank, hostname)

if rank == 0:
    print msg
    print 'collecting messages...'
    for i in xrange(1, size):
        msg = comm.recv(source=i, tag=12)
        print msg
else:
   comm.send(msg, dest=0, tag=12)

