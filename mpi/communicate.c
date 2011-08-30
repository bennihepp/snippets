#include <stdio.h>
#include <mpi.h>

#define TAG 12

int main(int argc, char *argv[])
{
  int numprocs, rank, namelen;
  char processor_name[MPI_MAX_PROCESSOR_NAME];
  char buf[1024];
  int i;
  MPI_Status stat;

  MPI_Init(&argc, &argv);
  MPI_Comm_size(MPI_COMM_WORLD, &numprocs);
  MPI_Comm_rank(MPI_COMM_WORLD, &rank);
  MPI_Get_processor_name(processor_name, &namelen);

  printf("Process %d on %s out of %d\n", rank, processor_name, numprocs);

  if (rank == 0) {
    printf("Receiving messages...\n");
    for (i=1; i < numprocs; ++i) {
      MPI_Recv(buf, sizeof(buf), MPI_CHAR, i, TAG, MPI_COMM_WORLD, &stat);
      printf("Message from %d: %s\n", i, buf);
    }
  }
  else {
    sprintf(buf, "Process %d on %s out of %d",
            rank, processor_name, numprocs);
    MPI_Send(buf, sizeof(buf), MPI_CHAR, 0, TAG, MPI_COMM_WORLD);
  }

  MPI_Finalize();
}

